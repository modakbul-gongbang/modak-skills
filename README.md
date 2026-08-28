# modak-skills

모닥불 공방에서 쓰는 [Agent Skills](https://code.claude.com/docs/en/skills) 모음이다.
Claude Code, Codex, Cursor, Gemini CLI 등 SKILL.md를 읽는 에이전트에서 함께 쓸 수 있다.

## 스킬 목록

| 스킬 | 설명 |
| --- | --- |
| [`eli`](skills/eli/README.md) | 주제를 5살, 입문, 실무 세 수준으로 나눠 그림 위주의 HTML 설명 자료를 만든다. 수준을 지정하지 않으면 세 수준을 탭 하나로 묶는다. |

### eli 결과물 예시

`/eli git rebase`를 실행하면 세 수준이 탭으로 묶인 페이지가 만들어진다.
아래는 그중 5살 탭이다. 입문과 실무 탭은 [eli 사용 가이드](skills/eli/README.md#예시-결과물)에서 볼 수 있다.

<img src="docs/assets/eli-5.png" alt="eli 5살 탭" width="520">

## 설치 방법

각 스킬은 `skills/<이름>/SKILL.md` 한 파일로 구성된다.
이 레이아웃은 [vercel-labs/skills](https://github.com/vercel-labs/skills)가 기대하는 구조와 같아서 아래 세 가지 방법 중 편한 쪽을 쓰면 된다.

### 방법 A : `npx skills` (권장)

여러 에이전트 런타임에 한 번에 설치한다. Node.js 18 이상과 `npx`만 있으면 된다.

```bash
# 전체 스킬 설치
npx --yes skills add modakbul-gongbang/modak-skills --all -g

# 특정 스킬만 설치
npx --yes skills add modakbul-gongbang/modak-skills --skill eli -g
```

`~/.agents/skills/<이름>`에 실제 파일을 두고, 감지된 에이전트의 스킬 경로에 심볼릭 링크를 건다.
설치 후 새 세션을 시작하면 인식된다. 업데이트는 같은 명령을 다시 실행한다.

### 방법 B : Claude Code 플러그인

Claude Code만 쓴다면 마켓플레이스로 설치할 수 있다.

```
/plugin marketplace add modakbul-gongbang/modak-skills
/plugin install modak-skills@modak-skills
```

스킬이 추가되면 마켓플레이스를 갱신하는 것만으로 반영된다.

### 방법 C : 수동 clone + 연결

`npx`를 쓰지 않거나 특정 런타임 하나에만 넣고 싶을 때 쓴다.

```bash
git clone https://github.com/modakbul-gongbang/modak-skills.git ~/projects/modak-skills
```

Claude Code는 심볼릭 링크를 인식한다.

```bash
mkdir -p ~/.claude/skills
for d in ~/projects/modak-skills/skills/*/; do
  ln -s "$d" ~/.claude/skills/"$(basename "$d")"
done
```

Codex는 심볼릭 링크로 연결된 SKILL.md를 인식하지 못할 수 있으므로 실제 파일로 복사한다.

```bash
mkdir -p ~/.codex/skills/eli
cp ~/projects/modak-skills/skills/eli/SKILL.md ~/.codex/skills/eli/SKILL.md
```

업데이트는 `git pull`로 한다. Claude Code는 심볼릭 링크라 바로 반영되고, Codex는 파일을 다시 복사해야 한다.

## 폴더 구조

```
modak-skills/
├── .claude-plugin/
│   ├── marketplace.json   # 마켓플레이스 정의
│   └── plugin.json        # 플러그인이 포함하는 스킬 목록
├── docs/assets/           # README에 쓰는 이미지
└── skills/
    └── <스킬 이름>/
        ├── SKILL.md       # 에이전트가 읽는 지침
        └── README.md      # 사람이 읽는 사용 문서 (선택)
```

## 스킬 추가하기

기여 방법은 [CONTRIBUTING.md](CONTRIBUTING.md)에 정리해 두었다.

## 라이선스

MIT
