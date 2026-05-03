# Agent Notes

이 파일은 작업자가 먼저 읽는 짧은 인덱스입니다. 제품 설명과 설계 상세는 `docs/` 문서를 기준으로 합니다.

## 문서 포인터

- 요구사항: [docs/00-requirements.md](docs/00-requirements.md)
- 솔루션 리서치와 결론: [docs/01-solution-research.md](docs/01-solution-research.md)
- 초기 아키텍처: [docs/02-architecture.md](docs/02-architecture.md)
- 코드 컨벤션: [docs/03-code-conventions.md](docs/03-code-conventions.md)
- future 런타임 refresh: [docs/04-best-practice-sequences.md](docs/04-best-practice-sequences.md)

## 작업 규칙

- 구현으로 바로 들어가지 않습니다. 요구사항과 리서치 합의 후 설계를 작성합니다.
- 설계와 결정 사항은 `docs/` 아래에 문서로 남깁니다.
- `main`에 바로 머지하지 않습니다. feature branch에서 작업하고 PR은 squash merge를 전제로 합니다.
- 로컬 IDE 파일은 커밋하지 않습니다. `.gitignore` 기준을 따릅니다.
- 상세 코드 규칙은 [docs/03-code-conventions.md](docs/03-code-conventions.md)를 따릅니다.

## 현재 방향

- 핵심 방향은 OpenBao를 UI/저장소/audit 계층으로 두고, Spring 서비스는 Spring Cloud Config Server의 Vault/OpenBao backend를 사용하게 하는 것입니다.
- Common Config Server의 수동 구현 범위는 프론트 refresh/fetch projection API로 제한합니다.
- 프론트는 명시적으로 refresh/fetch 해서 최신 설정을 가져갑니다.
- Python, Node.js 등 비 Spring 서비스의 HTTP 기반 조회 방식은 future 범위에서 검토합니다.
