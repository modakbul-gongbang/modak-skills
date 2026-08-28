---
name: eli
description: Explain a topic at a chosen reader level: 5살 / 입문 / 실무 (eli 5 / 20 / 30). Use when the user types /eli <age> <topic>, or asks to explain something "like I'm N", "N살한테 설명하듯", or wants a picture explainer with adjustable depth.
argument-hint: "[5|입문|실무] <주제>"
---

# eli

Explain `$ARGUMENTS` as an HTML artifact. The first token is the level; the rest is the topic.
Levels are named by reader, not age. Numbers are shortcuts for typing:

| token | tab label | reader |
|---|---|---|
| `5`, `5살` | 5살 | someone hearing the topic for the first time |
| `20`, `입문` | 입문 | someone who started learning it |
| `30`, `실무` | 실무 | someone who uses it at work |

If no level is given, build all three as tabs on one page, 5살 selected by default. Several tokens (`5 20 30`) also means tabs.
Never show "20살", "30살", or "(실무)" in the page. Tab labels are exactly `5살`, `입문`, `실무`.

The one-line lead under each tab is a summary of the topic at that level (e.g. 5살: "책을 많이 읽고 다음 말을 맞히는 친구"), never a description of the format or of these rules.

Always: load the `artifact-design` skill first, big pictures (inline SVG or CSS shapes), one idea per card,
Korean by default, headings as noun phrases, body lines ending in `~함 / ~됨 / ~임`.

## Age levels

| level | reader | analogy | terms | mechanism | cards |
|---|---|---|---|---|---|
| 5살 | non-developer, no background | everyday objects only | none | none, only "what it does" | 4–5 |
| 입문 | beginner, junior | everyday objects + one real step | 1 per card, `한글(English) : 뜻` | one real step per card | 6–8 |
| 실무 | working developer | optional, only if it clarifies | as needed, defined on first use | real flow, trade-offs, failure modes, where it breaks in practice | 6–10 |

Other numbers map to the nearest level (5–12 → 5살, 13–25 → 입문, 26+ → 실무).

## Topic kind decides the order (all levels, strictest at 실무)

Classify the topic first. When unsure, treat it as a tool.

| kind | examples | order of cards |
|---|---|---|
| concept | hash, branch, DNS, cache | definition => mechanism => example |
| tool / command | rebase -i, grep, docker run, a CLI flag | **the pain without it** (show the actual mess: a log, an error, a screen) => the command => screen before/after => when not to use |
| procedure / workflow | PR flow, deploy, onboarding | step list => input and output of each step => where people get stuck |

Rules for tools:
- Never open a tool card with a definition. Open with "이게 없으면 이렇게 됨" and show the real artifact (ugly `git log`, the error text, the manual repetition).
- If the tool has a screen, write it as a terminal replay: what you type => what appears => the part you edit (highlighted) => the result. A simulator is optional and comes after the replay, never instead of it.
- Tie back to the lower levels' analogy in one line (e.g. "사진 4장 중 3장은 실수 수정 => 1장에 겹쳐 붙이기").

## 실무 specifics

- Start with a one-line note: "5살, 입문 탭을 먼저 보면 좋음" when the page has lower levels; never assume the reader skipped nothing.
- Every term the 입문 level did not define gets a `한글(English) : 뜻` on first use (cherry-pick, upstream, merge-base, reflog ...).
- Glossary card comes AFTER the flow/mechanism widget, never before it, titled `용어 : 위 흐름에 나온 것`. Each row: plain Korean first, the 입문-level analogy in parentheses, the English term last. No row may introduce a second unexplained term.
- The definition card uses no acronym the reader has not met. Spell out what the protocol/tool fixes in three plain clauses; the formal names go in the glossary.
- Open with the one-sentence definition, then the mechanism diagram.
- If the mechanism is step-based, make it a step-through widget ("다음 단계" button, one change per click, a caption per step) instead of a static before/after.
- If the topic has a mode where the user edits something and sees a result (interactive rebase, config flags, query plans), build a small simulator: inputs on the left, live result on the right, plain JS, no libraries.
- Include: when to use / when not to, common mistakes, one concrete command or code snippet if applicable.
- Numbers carry sources in parentheses: `약 20% (자체 집계, 2026년 6월)`.
- No motivational filler. A working developer reads it in 3 minutes.

## Verify before publishing (mandatory)

- Commands, code, file paths: never inside SVG `<text>`. Use a `<pre><code>` block under the picture. SVG text is for one or two words.
- Every SVG `<text>` has `text-anchor="middle"`, is under 12 Korean characters, and sits at least 20 viewBox units from every edge. Longer captions go in a `<p>` under the picture.
- Open each tab once and read every card top to bottom. Fix any clipped, overlapped, or wrapped-mid-word text before publishing.

## Output

Publish with the Artifact tool. Title is the topic as a noun phrase. Favicon: 🖍️ for 5살, 📘 for 입문, 🧭 for 실무, 🎚️ for a tabbed page.
