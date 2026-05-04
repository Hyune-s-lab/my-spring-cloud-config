# Common Config Server 요구사항

## 배경

현재 프론트 개발자가 Vercel storage를 활용해 피쳐 토글을 개발하고 있습니다.

- 하지만 회사 서비스는 온프레미스 배포도 필요하므로 Vercel에 의존하는 방식은 장기적으로 맞지 않습니다.
- 이번 프로젝트의 목표는 특정 프론트 피쳐 토글만 대체하는 것이 아니라, 회사의 여러 서비스가 공통으로 사용할 수 있는 내부 `common-config` 서버를 만드는 것입니다.
- 초기 피쳐 토글 형태는 다음 구조에 가깝습니다.

```json
{
  "STM-0000": {
    "note": "Sample flag.",
    "local": true,
    "dev": false,
    "qa": false,
    "live": false,
    "jp-live": false,
    "entitledTeamIds": {
      "dev": [
        "teamID000000000000000000"
      ],
      "qa": [
        "teamID000000000000000000"
      ],
      "live": [
        "teamID000000000000000000"
      ],
      "jp-live": []
    },
    "createdAt": "2026-04-22T07:29:27.340Z",
    "createdBy": "jiwon@sionic.ai",
    "modifiedAt": "2026-04-22T07:29:50.727Z",
    "modifiedBy": "jiwon@sionic.ai"
  }
}
```

이 구조는 첫 리소스 타입으로 보고, 전체 제품 경계를 이것에만 묶지는 않습니다.

## 목표

- 회사 공통 설정 관리 서버를 온프레미스 친화적으로 제공합니다.
- 첫 관리 도메인은 피쳐 플래그로 시작하고, 이후 일반 설정 관리로 확장할 수 있게 설계합니다.
- 관리 UI와 저장소는 OpenBao를 우선 사용하고, common-config 서버는 Spring Cloud Config 표준 조회 API를 제공합니다.
- 첫 마일스톤부터 audit/history와 다언어 서비스 소비 방식을 고려합니다.
- 런타임 설정 변경은 명시적 refresh/fetch로 시작하고, 이후 확장 경로를 남깁니다.

## 첫 마일스톤의 비목표

- 별도 외부 DB, Git 저장소, Vercel/AWS 같은 managed service를 필수 의존성으로 두지 않습니다.
- 서버 push 기반 런타임 refresh와 고급 승인 워크플로우는 우선 제외합니다.
- 별도 관리자 프론트를 직접 구현하지 않습니다.

## 기능 요구사항

- OpenBao UI에서 피쳐 플래그 설정을 생성, 조회, 수정, 삭제할 수 있어야 합니다.
- OpenBao KV v2 versioning과 audit device로 변경 이력 기반을 남깁니다.
- common-config 서버는 Spring Cloud Config 표준 HTTP API로 설정을 조회할 수 있어야 합니다.
- 프론트와 Spring 서비스는 우선 같은 Spring Cloud Config HTTP 응답을 명시적으로 조회합니다.
