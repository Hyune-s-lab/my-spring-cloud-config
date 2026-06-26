# Agent Notes

이 파일은 작업자가 먼저 읽는 짧은 인덱스입니다. 제품 설명과 설계 상세는 `docs/` 문서를 기준으로 합니다.

## 문서 포인터

- 요구사항: [docs/00-requirements.md](docs/00-requirements.md)
- 솔루션 리서치와 결론: [docs/01-solution-research.md](docs/01-solution-research.md)
- Apollo 대안 리서치: [docs/02-apollo-alternative.md](docs/02-apollo-alternative.md)

## 작업 규칙

- 구현으로 바로 들어가지 않습니다. 요구사항과 리서치 합의 후 설계를 작성합니다.
- 설계와 결정 사항은 `docs/` 아래에 문서로 남깁니다.
- `main`에 바로 머지하지 않습니다. feature branch에서 작업하고 PR은 squash merge를 전제로 합니다.
- 로컬 IDE 파일은 커밋하지 않습니다. `.gitignore` 기준을 따릅니다.

## 코드 컨벤션

- 모델은 불변 `data class`를 기본으로 두고, 변경은 `copy()`로 표현합니다.
- 값이 없다는 의미가 분명할 때만 nullable을 사용합니다. 컬렉션은 `emptyList()`, `emptyMap()`을 우선합니다.
- 외부 확장 지점이 아니면 `internal`을 우선합니다. public API는 entry point, config, model처럼 의도된 경계에만 둡니다.
- 상태 없는 유틸은 `object`, 설정이 필요한 구현체는 생성자 파라미터를 받는 `class`로 둡니다.
- 고객/서비스/환경에만 맞는 특화 로직을 공통 계층에 넣지 않습니다.
- 호출 사이에 남는 mutable state를 피합니다. per-call 상태는 지역 변수나 메서드 파라미터로 둡니다.
- 파일당 하나의 top-level 클래스 또는 인터페이스를 둡니다. 예외는 유틸 확장 함수와 nested/inner class입니다.
- 테스트명은 동작을 설명하게 작성합니다.
- 이유 주석 없이 `@Suppress`를 추가하지 않습니다.

## 현재 방향

- 이 저장소는 아직 구현이 구성 완료됐다고 전제하지 않습니다. Spring Cloud Config, Gitea, OpenBao, Apollo 모두 리서치/PoC 후보로 봅니다.
- Spring Cloud Config는 후보 API shape와 backend 연동 방식의 참고안입니다. 이미 표준 조회 서버가 존재한다고 쓰지 않습니다.
- Apollo는 새 대안으로 조사 중입니다. Apollo는 Spring Cloud Config backend가 아니라 독립형 설정 관리 제품이므로, 제로베이스 PoC는 Apollo SDK/HTTP API를 직접 쓰는 방향이 자연스럽습니다.
- 회사 서비스 표준은 Kotlin Spring, Java 25, Spring Boot 4+입니다.
- 회사 설정 모델은 `application / profile / cluster` 3중 구조입니다. Spring Config의 `label`은 cluster가 아니라 version/branch label로 봅니다.
- Python, Node.js 등 비 Spring 서비스의 HTTP 기반 조회 방식도 Apollo direct API를 우선 기준으로 보고, Spring Config 응답 shape는 필요할 때만 facade로 검토합니다.
