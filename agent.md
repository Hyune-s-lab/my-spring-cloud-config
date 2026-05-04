# Agent Notes

이 파일은 작업자가 먼저 읽는 짧은 인덱스입니다. 제품 설명과 설계 상세는 `docs/` 문서를 기준으로 합니다.

## 문서 포인터

- 요구사항: [docs/00-requirements.md](docs/00-requirements.md)
- 솔루션 리서치와 결론: [docs/01-solution-research.md](docs/01-solution-research.md)
- 초기 아키텍처: [docs/02-architecture.md](docs/02-architecture.md)

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

- 핵심 방향은 OpenBao를 UI/저장소/audit 계층으로 두고, Spring 서비스는 Spring Cloud Config Server의 Vault/OpenBao backend를 사용하게 하는 것입니다.
- Common Config Server는 우선 Spring Cloud Config 표준 조회 서버로만 동작합니다.
- 프론트도 우선 Spring Cloud Config HTTP 응답을 명시적으로 조회해서 최신 설정을 가져갑니다.
- Python, Node.js 등 비 Spring 서비스의 HTTP 기반 조회 방식은 future 범위에서 검토합니다.
