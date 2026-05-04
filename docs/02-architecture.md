# Architecture

## Phase 1

Phase 1은 OpenBao를 설정 저장소와 관리자 UI로 사용하고, common-config 서버는 Spring Cloud Config 표준 API를 제공하는 조회 서버로 둡니다.

- 설정 조회는 OpenBao KV v2의 latest 값만 대상으로 합니다.
- OpenBao version, created_time, audit 이력은 Spring Config 응답에 포함하지 않습니다.

```mermaid
sequenceDiagram
    actor Admin as Admin/Operator
    box rgb(235, 245, 255) Docker Compose
        participant Bao as OpenBao UI/API
        participant Config as Spring Cloud Config Server
    end
    participant FE as Frontend
    Note over Admin, Bao: 관리자가 설정을 변경합니다.
    Admin ->> Bao: OpenBao UI에서 설정 변경
    Bao ->> Bao: Raft storage 에 저장
    Bao ->> Admin: 저장 완료
    Note over Bao, FE: OpenBao는 KV 변경 webhook callback을 제공하지 않습니다. <br>따라서 소비자가 명시적으로 조회 합니다.
    Note over FE, Config: Spring Cloud Config 표준 API로 설정을 조회합니다.
    FE ->> Config: GET /config/{application}/{profile}
    Config ->> Bao: Vault/OpenBao backend로 KV 조회
    Config ->> FE: Spring Config Environment 응답
```

```json
GET /config/{name}/{profiles}
GET /config/some-frontend/dev

{
  "name": "some-frontend", // 요청 application
  "profiles": [
    "dev" // 요청 profile
  ],
  "label": null, // Git branch/tag용. Vault/OpenBao 대응값 없음
  "version": null, // Git commit hash용. OpenBao KV version은 path별 metadata
  "state": null, // backend 추가 상태용. Vault/OpenBao backend는 보통 미사용
  "propertySources": [ // n개 가능. Spring Config가 우선순위대로 병합
    {
      "name": "vault:some-frontend/dev", // Spring Config property source 이름. vault 출처 표시
      "source": {
        "feature-toggles.new-home": true, // OpenBao KV 값을 flat property로 변환
        "feature-toggles.beta-search": true
      }
    }
  ]
}
```

## Future: Spring Runtime Refresh

- Spring 서비스는 Spring Cloud Config Server로 설정을 조회합니다.
- OpenBao는 KV 변경 webhook callback을 제공하지 않으므로 별도 refresh trigger가 필요합니다.

```mermaid
sequenceDiagram
    actor Admin as Admin/Operator
    participant Bao as OpenBao
    participant Config as Spring Cloud Config Server
    participant Broker as RabbitMQ/Kafka Broker
    participant App as A Service 1..N
    Note over Admin, Bao: 관리자가 설정을 변경합니다.
    Admin ->> Bao: OpenBao UI에서 설정 변경
    Bao ->> Admin: 저장 완료
    Note over Admin, Config: OpenBao는 KV 변경 webhook callback을 제공하지 않습니다.
    Note over Admin, Config: Config Server에 bus refresh를 요청합니다.
    Admin ->> Config: POST /actuator/busrefresh
    Config ->> Broker: refresh 이벤트 publish
    Broker ->> App: 각 인스턴스에 refresh 이벤트 전파
    Note over App, Config: 각 인스턴스가 최신 설정을 다시 조회합니다.
    App ->> Config: 설정 재조회
    Config ->> Bao: Vault backend로 KV v2 설정 조회
    Config ->> App: Spring Environment 응답
    App ->> App: refresh scope 값 재바인딩
```
