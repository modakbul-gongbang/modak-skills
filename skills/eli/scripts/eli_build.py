#!/usr/bin/env python3
"""eli 페이지 조립 + 검증.

    python3 scripts/eli_build.py sections.html --title "제목" --out page.html [--no-verify] [--shots DIR] [--tabs 5살,실무]

- sections.html : <section data-tab="5살" data-default> ... </section> 들만 적은 파일.
                  <script> 블록이 있으면 template의 공통 스크립트 뒤로 옮겨 붙인다.
- 검증 : Playwright(Chromium)로 탭마다 전체 스크린샷, 단계 위젯은 단계별로 찍어 탭 이미지 아래에 이어 붙인다.
         DOM 검사(SVG 글자 수/anchor/여백, 가로 넘침, 금지 문구, 콘솔 오류)를 stdout에 출력한다.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "templates" / "template.html"

DOM_CHECK_JS = r"""
() => {
  const warns = [];
  const snippet = el => (el.outerHTML || '').replace(/\s+/g, ' ').slice(0, 90);
  const visible = el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };

  // 1. SVG text: 12자 이하, text-anchor=middle, viewBox 가장자리에서 20 이상
  document.querySelectorAll('svg').forEach(svg => {
    if (!visible(svg)) return;
    const vb = (svg.getAttribute('viewBox') || '').split(/[\s,]+/).map(Number);
    svg.querySelectorAll('text').forEach(t => {
      const txt = (t.textContent || '').trim();
      if (txt.replace(/\s/g, '').length > 12) warns.push(`SVG text 12자 초과: "${txt}"`);
      const anchor = t.getAttribute('text-anchor') || getComputedStyle(t).textAnchor;
      if (anchor !== 'middle') warns.push(`SVG text anchor≠middle: "${txt}"`);
      if (vb.length === 4) {
        try {
          const b = t.getBBox();
          const [x, y, w, h] = vb;
          if (b.x - x < 20 || b.y - y < 20 || (x + w) - (b.x + b.width) < 20 || (y + h) - (b.y + b.height) < 20)
            warns.push(`SVG text 가장자리 20 이내: "${txt}" bbox=(${b.x|0},${b.y|0},${b.width|0},${b.height|0}) viewBox=${vb.join(' ')}`);
        } catch (e) {}
      }
      if (/[\/\\$`]|--|\.py|\.js|\.html|\.md/.test(txt) && txt.length > 6) warns.push(`SVG text에 코드/경로 의심: "${txt}"`);
    });
  });

  // 2. 가로 넘침 (스크롤 컨테이너 제외)
  document.querySelectorAll('.card').forEach(card => {
    if (!visible(card)) return;
    const cr = card.getBoundingClientRect();
    card.querySelectorAll('*').forEach(el => {
      if (!visible(el) || el.closest('pre, .tablewrap, svg')) return;
      const r = el.getBoundingClientRect();
      if (r.right > cr.right + 1 || r.left < cr.left - 1) warns.push(`카드 밖으로 넘침: ${snippet(el)}`);
    });
  });
  document.querySelectorAll('.lbl, .val, .box, .tile, td.en, .ctx span, .tab, h3').forEach(el => {
    if (!visible(el) || el.closest('pre, .tablewrap')) return;
    if (el.scrollWidth > el.clientWidth + 1) warns.push(`글자 잘림(scrollWidth>clientWidth): ${snippet(el)}`);
  });
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth + 1)
    warns.push('페이지 가로 스크롤 발생');

  // 3. 금지 문구
  const body = document.body.innerText;
  ['20살', '30살', '(실무)'].forEach(s => { if (body.includes(s)) warns.push(`금지 문구 포함: ${s}`); });

  // 4. 빈 카드/빈 단계
  document.querySelectorAll('.card').forEach(c => { if (visible(c) && !c.textContent.trim()) warns.push('빈 카드'); });
  return warns;
}
"""


def build(sections_path: Path, title: str, out: Path) -> Path:
    tpl = TEMPLATE.read_text(encoding="utf-8")
    body = sections_path.read_text(encoding="utf-8")
    scripts = re.findall(r"<script\b[^>]*>.*?</script>", body, flags=re.S | re.I)
    body = re.sub(r"<script\b[^>]*>.*?</script>", "", body, flags=re.S | re.I).strip()
    if "<section" not in body:
        sys.exit("sections 파일에 <section data-tab=...> 이 없음")
    html = (
        tpl.replace("{{TITLE}}", title)
        .replace("{{SECTIONS}}", body)
        .replace("{{SCRIPTS}}", "\n".join(scripts))
    )
    out.write_text(html, encoding="utf-8")
    return out


COL_H = 2400  # Read 도구가 세로로 긴 이미지를 지나치게 축소하므로, 이 높이로 잘라 가로로 나란히 붙인다


def stack(frames):
    from PIL import Image
    w = max(f.width for f in frames)
    h = sum(f.height for f in frames) + 12 * (len(frames) - 1)
    sheet = Image.new("RGB", (w, h), "white")
    y = 0
    for f in frames:
        sheet.paste(f, (0, y))
        y += f.height + 12
    return sheet


def columnize(img):
    from PIL import Image
    if img.height <= COL_H:
        return img.convert("RGB")
    cols = (img.height + COL_H - 1) // COL_H
    gutter = 16
    out = Image.new("RGB", (cols * img.width + gutter * (cols - 1), COL_H), "#888")
    for c in range(cols):
        strip = img.crop((0, c * COL_H, img.width, min(img.height, (c + 1) * COL_H)))
        out.paste(strip, (c * (img.width + gutter), 0))
    return out


def verify(page_path: Path, shots_dir: Path, only_tabs: set[str] | None = None) -> int:
    from PIL import Image
    from playwright.sync_api import sync_playwright

    shots_dir.mkdir(parents=True, exist_ok=True)
    warn_total = 0
    console: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 900, "height": 900})
        page.on("console", lambda m: console.append(f"[{m.type}] {m.text}") if m.type in ("error", "warning") else None)
        page.on("pageerror", lambda e: console.append(f"[pageerror] {e}"))
        page.goto(page_path.resolve().as_uri())
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(400)

        tabs = page.locator("#tabs .tab")
        n = tabs.count()
        labels = [tabs.nth(i).inner_text().strip() for i in range(n)] if n else ["single"]

        for i, label in enumerate(labels):
            if n:
                tabs.nth(i).click()
                page.wait_for_timeout(150)
            if only_tabs and label not in only_tabs:
                # DOM 검사만 하고 스크린샷은 건너뜀
                warns = page.evaluate(DOM_CHECK_JS)
                warn_total += len(warns)
                for w in warns:
                    print(f"[{label}] {w}")
                continue
            frames: list[Image.Image] = []
            frames.append(Image.open(io.BytesIO(page.screenshot(full_page=True))))

            # 단계 위젯: 단계마다 캡처
            steppers = page.locator("section:not([hidden]) .stepper")
            for s in range(steppers.count()):
                st = steppers.nth(s)
                nxt = st.locator("button.next")
                steps = st.locator(":scope > .step").count()
                for _ in range(steps):
                    frames.append(Image.open(io.BytesIO(st.screenshot())))
                    nxt.click()
                    page.wait_for_timeout(80)

            warns = page.evaluate(DOM_CHECK_JS)
            warn_total += len(warns)
            for w in warns:
                print(f"[{label}] {w}")

            out_png = shots_dir / f"tab-{i+1}-{label}.png"
            sheet = columnize(stack(frames))
            sheet.save(out_png)
            print(f"shot: {out_png}  ({sheet.width}x{sheet.height}, 단계 캡처 {len(frames)-1}장)")

        # 다크 테마: 기본 탭 전체
        page.evaluate("document.documentElement.setAttribute('data-theme','dark')")
        if n:
            tabs.nth(0).click()
        page.wait_for_timeout(150)
        dark_png = shots_dir / "dark.png"
        if not only_tabs:
            columnize(Image.open(io.BytesIO(page.screenshot(full_page=True)))).save(dark_png)
        dark_warns = page.evaluate(DOM_CHECK_JS)
        for w in dark_warns:
            if "넘침" in w or "잘림" in w:
                print(f"[dark] {w}")
                warn_total += 1
        if not only_tabs:
            print(f"shot: {dark_png}")
        browser.close()

    for line in console:
        if "favicon" in line:
            continue
        print(f"console {line}")
        warn_total += 1
    print(f"경고 {warn_total}건")
    return warn_total


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sections")
    ap.add_argument("--title", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--shots", default=None, help="스크린샷 폴더 (기본: <out 폴더>/shots)")
    ap.add_argument("--no-verify", action="store_true")
    ap.add_argument("--tabs", default=None, help="스크린샷을 찍을 탭만 쉼표로 (예: 5살,실무). DOM 검사는 모든 탭에 함. 다크 시트는 생략")
    a = ap.parse_args()

    out = build(Path(a.sections), a.title, Path(a.out))
    print(f"built: {out}  ({out.stat().st_size // 1024} KB)")
    if not a.no_verify:
        shots = Path(a.shots) if a.shots else out.parent / "shots"
        only = {x.strip() for x in a.tabs.split(",") if x.strip()} if a.tabs else None
        verify(out, shots, only)


if __name__ == "__main__":
    main()
