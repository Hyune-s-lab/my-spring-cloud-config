# my-spring-cloud-config

OpenBao를 설정 저장소와 관리자 UI로 사용하고, Spring Cloud Config 표준 API로 설정을 조회하는 common-config 서버입니다.

## Requirements

- Vercel, AWS, 관리형 DB, Git 서버 없이 온프레미스에서 실행할 수 있어야 합니다.
- 피쳐 토글을 첫 관리 도메인으로 시작하고, 이후 공통 설정 관리로 확장할 수 있어야 합니다.

## Phase 1

- OpenBao 를 KV v2 저장소와 관리자 UI로 사용합니다.
- common-config 서버는 Spring Cloud Config Server로 동작합니다.
- 설정 조회는 OpenBao KV v2의 latest 값만 대상으로 합니다.
- OpenBao version, created_time, audit 이력은 Spring Config 응답에 포함하지 않습니다.

```mermaid
sequenceDiagram
    actor Admin as Admin/Operator
    box rgb(235, 245, 255) Docker Compose
        participant Bao as OpenBao UI/API
        participant Config as Spring Cloud Config Server
    end
    participant Client as Client
    Admin ->> Bao: OpenBao UI에서 설정 변경
    Bao ->> Bao: Raft storage 에 저장
    Bao ->> Admin: 저장 완료
    Note over Bao, Client: OpenBao는 KV 변경 webhook callback을 제공하지 않음
    Client ->> Config: GET /config/{application}/{profile}
    Config ->> Bao: Vault/OpenBao backend로 KV 조회
    Config ->> Client: Spring Config Environment 응답
```

## 실행

```bash
# Docker Compose
docker compose -f docker/docker-compose.yml up -d --build

# 샘플 데이터 생성
python3 docker/openbao/sample-config.py --create

# 샘플 데이터 삭제
python3 docker/openbao/sample-config.py --clear
```

## 설정 조회

```json
GET http://localhost:8085/config/some-frontend/dev

{
  "name": "some-frontend",
  "profiles": [
    "dev"
  ],
  "label": null, // Git branch/tag용. Vault/OpenBao 대응값 없음
  "version": null, // Git commit hash용. OpenBao KV version은 path별 metadata
  "state": null, // backend 추가 상태용. Vault/OpenBao backend는 보통 미사용
  "propertySources": [
    {
      "name": "vault:some-frontend/dev",
      "source": {
        "feature-toggles.new-home": true,
        "feature-toggles.beta-search": true
      }
    }
  ]
}
```

## 문서

- [Agent notes](agent.md)
- [요구사항](docs/00-requirements.md)
- [솔루션 리서치](docs/01-solution-research.md)
