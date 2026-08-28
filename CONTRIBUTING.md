# 기여 가이드

## 스킬 추가 절차

1. `skills/` 아래에 스킬 이름으로 폴더를 만든다. 이름은 소문자와 하이픈만 사용한다.
2. `skills/<이름>/SKILL.md`를 작성한다. 스킬 하나에 필수 파일은 이것 하나뿐이다.
3. 사용 문서가 필요하면 같은 폴더에 `README.md`를 둔다. GitHub에서 스킬 폴더를 열면 이 파일이 바로 보인다.
4. `.claude-plugin/plugin.json`의 `skills` 배열에 `"./skills/<이름>"`을 추가한다.
5. 루트 `README.md`의 스킬 목록 표에 한 줄을 추가한다.

스크립트나 참고 자료가 필요하면 스킬 폴더 안에 `scripts/`, `references/`, `templates/`를 만들어 넣는다.
README에만 쓰는 이미지는 스킬 폴더가 아니라 `docs/assets/`에 둔다. 설치할 때 따라오지 않게 하기 위해서이다.

## SKILL.md 작성 기준

frontmatter는 `name`, `description`을 반드시 넣는다. 슬래시 명령으로 인자를 받는다면 `argument-hint`를 더한다.

```yaml
---
name: eli
description: Explain a topic at a chosen reader level. Use when the user types /eli <age> <topic>, or asks to explain something "like I'm N".
argument-hint: "[5|입문|실무] <주제>"
---
```

`description`은 에이전트가 이 스킬을 언제 불러야 하는지 판단하는 유일한 근거이다.
무엇을 하는지에 더해, 사용자가 실제로 말할 법한 표현을 구체적으로 나열한다.

본문은 에이전트가 따라야 할 규칙을 구체적으로 적는다. 표와 예시를 적극적으로 사용하고,
하지 말아야 할 동작도 함께 명시한다.

## 검토 기준

- 스킬은 자기 완결적이어야 한다. 특정 SSH 호스트나 개인 프로젝트 경로처럼 실행 환경 전제가 필요하면 SKILL.md 안에 명시한다.
- 다른 스킬과 발동 조건이 겹치지 않는지 확인한다.
- 크리덴셜을 하드코딩하지 않는다. 비밀 값은 환경변수로 읽는다.
- 외부 API를 호출한다면 그 사실과 필요한 키를 스킬 폴더의 `README.md`에 명시한다.

## 작업 방식

변경은 main에 바로 push하지 않는다. 브랜치를 만들고 PR을 올린 뒤 squash 머지한다.
