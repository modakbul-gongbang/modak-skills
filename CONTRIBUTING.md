# 기여 가이드

## 스킬 추가 절차

1. 레포 루트에 스킬 이름으로 폴더를 만든다. 이름은 소문자와 하이픈만 사용한다.
2. 폴더 안에 세 파일을 만든다.
   - `SKILL.md` : 에이전트가 읽는 지침이다. frontmatter에 `name`, `description`이 반드시 있어야 한다.
   - `skill.json` : 스킬 메타데이터이다. `SKILL.md`의 `name`, `description`과 값을 일치시킨다.
   - `instruction.md` : 사람이 읽는 사용 문서이다. 하는 일, 언제 쓰는지, 사용법, 결과물을 적는다.
3. `.claude-plugin/plugin.json`의 `skills` 배열에 `"./<스킬 이름>"`을 추가한다.
4. `README.md`의 스킬 목록 표에 한 줄을 추가한다.

스크립트나 참고 자료가 필요하면 스킬 폴더 안에 `scripts/`, `references/`, `templates/`를 만들어 넣는다.

## SKILL.md 작성 기준

`description`은 에이전트가 이 스킬을 언제 불러야 하는지 판단하는 유일한 근거이다.
따라서 무엇을 하는지에 더해, 사용자가 어떤 말을 했을 때 발동해야 하는지를 함께 적는다.

```yaml
---
name: eli
description: Explain a topic at a chosen reader level. Use when the user types /eli <age> <topic>, or asks to explain something "like I'm N".
license: MIT
metadata:
  category: writing
  locale: ko-KR
---
```

본문은 에이전트가 따라야 할 규칙을 구체적으로 적는다. 표와 예시를 적극적으로 사용하고,
하지 말아야 할 동작도 함께 명시한다.

## 검토 기준

- 다른 스킬과 발동 조건이 겹치지 않는지 확인한다.
- 크리덴셜을 하드코딩하지 않는다. 비밀 값은 환경변수로 읽는다.
- 외부 API를 호출한다면 그 사실과 필요한 키를 `instruction.md`에 명시한다.
