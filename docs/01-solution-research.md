# 솔루션 리서치

## 결론

현재 요구사항에는 **OpenBao를 영속성/audit 저장소로 사용하고, Spring Cloud Config Server의 Vault backend로 설정 조회를 제공하는 구조**가 가장 적합합니다.

- OpenBao는 KV v2 versioning, audit device, policy, HTTP API, Web UI를 제공합니다.
- Spring Cloud Config Server는 Vault backend로 OpenBao를 조회해 표준 설정 API를 제공합니다.
- 프론트도 우선 Spring Cloud Config 표준 응답을 직접 사용합니다.
- feature flag/config 검증과 프론트용 projection API는 표준 응답이 부족해지는 시점에 추가합니다.
- 런타임 refresh는 Spring Cloud Config Server와 Spring Cloud Bus의 공식 흐름을 우선 검토합니다.
- HashiCorp Vault는 라이선스/상용 정책 부담, Unleash는 OSS environment 제한과 PostgreSQL 운영 부담, OpenFeature는 서버 제품이 아니라는 이유로 핵심 솔루션에서 제외합니다.

| Solution                   | Self-hosted           | SDK/API                          | UI | Audit/Persistence                     | Runtime Updates       | Pros                                                                               | Cons                                                                                              |
|----------------------------|-----------------------|----------------------------------|----|---------------------------------------|-----------------------|------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| OpenBao                    | ✅                     | ✅ HTTP API<br>⚠️ generic clients | ✅  | ✅ KV v2 versioning<br>✅ audit devices | ⚠️ polling/ETag 직접 구현 | versioned KV, audit, policy, UI를 self-hosted로 제공합니다.                                | feature flag 제품은 아니므로 도메인 검증, projection API, refresh contract는 직접 구현해야 합니다.                       |
| Spring Cloud Config        | ✅                     | ✅ HTTP API<br>✅ Spring client    | ❌  | ⚠️ Vault backend 사용                    | ✅ Actuator/Bus 확장     | Vault/OpenBao backend, Spring client, refresh 흐름을 공식 기능으로 제공합니다.                      | 관리자 UI와 feature flag projection은 제공하지 않으므로 필요해지면 facade를 추가합니다.                                      |
| Unleash                    | ⚠️ Enterprise license | ✅ 다언어 SDK                        | ✅  | ⚠️ PostgreSQL 필수<br>⚠️ audit 제한       | ✅ SDK polling/cache   | feature flag 도메인이 성숙하고 self-hosted, 관리자 UI, 다언어 SDK를 제공합니다.                         | OSS는 project 1개, environment 2개 제한이 있어 `local/dev/qa/live/jp-live` 요구와 충돌합니다. PostgreSQL 운영도 필요합니다. |
| OpenFeature                | ✅                     | ✅ 표준 SDK/API                     | ❌  | ❌ 제공 안 함                              | ⚠️ provider 구현 의존     | Java/Kotlin, Node.js, Python 등에서 flag evaluation API를 표준화할 수 있습니다.                   | 서버 제품이 아니므로 관리자 UI, 저장소, audit/history, runtime update 경로는 별도로 필요합니다.                              |
| Vercel Edge Config / Flags | ❌                     | ⚠️ OpenFeature 지원                | ✅  | ✅ Vercel managed                      | ✅ platform 제공         | dashboard, targeting, segment, environment control, OpenFeature 지원 등 UX 참고 가치가 큽니다. | Vercel 플랫폼 의존으로 self-hosted가 불가능하므로 핵심 솔루션 후보에서 기각합니다.                                             |
| AWS KMS                    | ❌                     | ⚠️ AWS SDK                       | ⚠️ | ✅ AWS managed<br>✅ CloudTrail         | ❌ config runtime 아님   | secret/key management와 audit 설계 참고점이 있습니다.                                           | AWS managed service이고 feature flag/config 관리 도구가 아니므로 핵심 솔루션 후보에서 기각합니다.                           |

## 후보별 메모

### OpenBao

- MPL 2.0 오픈소스 Vault fork입니다.
- KV v2로 versioned key/value 저장, soft delete, undelete, metadata를 지원합니다.
- audit device가 API request/response를 기록하므로 변경 추적 기반을 제공합니다.
- Web UI와 HTTP API가 있어 운영자가 직접 관리할 수 있습니다.
- feature flag 제품은 아니므로 schema 검증, entitlement, 프론트 projection API가 필요해지면 common-config 서버가 담당해야 합니다.
- 프론트에 OpenBao를 직접 노출하지 않고 Spring Cloud Config Server를 통해 읽게 합니다.

출처: [OpenBao KV v2](https://openbao.org/docs/2.3.x/secrets/kv/kv-v2/), [OpenBao audit devices](https://openbao.org/docs/2.3.x/audit/), [OpenBao UI](https://openbao.org/docs/2.4.x/configuration/ui/), [OpenBao HTTP API](https://openbao.org/api-docs/2.3.x/), [OpenBao license baseline](https://openbao.org/docs/policies/osps-baseline/)

### Spring Cloud Config

- Spring Cloud Config Server는 Vault backend를 공식 지원하므로 Spring 서비스용 설정 조회를 수동 구현하지 않는 편이 낫습니다.
- Vault backend는 KV v2를 지원하므로 OpenBao의 Vault-compatible API를 우선 활용할 수 있습니다.
- Spring client, `Environment`, `PropertySource` 모델과 잘 맞습니다.
- Actuator refresh와 Spring Cloud Bus로 런타임 refresh 확장이 가능합니다.
- 프론트/비 Spring 서비스는 우선 Spring Cloud Config HTTP API를 사용하고, 필요해지면 별도 REST projection API와 polling/ETag/SSE 방식을 추가합니다.

#### Spring Runtime Refresh 판단 기준

Spring Cloud Config는 설정을 key 단위로 부분 조회하기보다 `application/profile` 단위로 `Environment`를 다시 읽습니다. 런타임 반영 범위는 Config Server가 아니라 각 Spring 애플리케이션의 bean 설계로 제한합니다.

| 구분 | 의미 | 예시 | 판단 |
|------|------|------|------|
| 조회 단위 | Config Server가 원격 설정을 다시 읽는 단위 | `GET /config/my-service/dev` | profile source 전체를 다시 읽습니다. |
| 저장 단위 | OpenBao KV v2 path 단위 | `kv/my-service/dev` | 10개 변수 중 1개가 바뀌어도 path 전체가 새 version이 됩니다. |
| 런타임 반영 단위 | 애플리케이션 내부 bean/properties 단위 | `@RefreshScope`, `@ConfigurationProperties` | 자주 바뀌는 2개 값만 별도 prefix/properties class로 분리합니다. |
| 변경 전파 | refresh를 시작하는 신호 | `POST /actuator/refresh`, `POST /actuator/busrefresh` | OpenBao webhook이 없으므로 별도 trigger가 필요합니다. |

따라서 10개 설정 중 2개만 자주 바뀐다면, 원격 설정은 함께 조회하되 자주 바뀌는 값만 별도 prefix와 bean으로 분리해 refresh 대상이 되게 설계합니다.

출처: [Spring Cloud Config Vault Backend](https://docs.spring.io/spring-cloud-config/reference/server/environment-repository/vault-backend.html), [Composite Environment Repositories](https://docs.spring.io/spring-cloud-config/reference/server/environment-repository/composite-repositories.html), [Push Notifications and Spring Cloud Bus](https://docs.spring.io/spring-cloud-config/reference/server/push-notifications-and-bus.html), [Spring Cloud Bus](https://docs.spring.io/spring-cloud-bus/docs/current/reference/html/index.html), [OpenBao Libraries](https://openbao.org/api-docs/libraries/), [OpenBao Migration Guide](https://openbao.org/docs/migration-guide/)

### Unleash

- feature flag 도메인, 관리자 UI, 다언어 SDK가 강점입니다.
- OSS는 project 1개, environment 2개 제한이 있어 현재 환경 요구와 충돌합니다.
- self-hosted 운영에는 PostgreSQL이 필요합니다.
- 런타임 변경은 SDK polling/cache 구조로 처리합니다.
- common-config 전체보다는 feature flag 제품에 가깝습니다.

출처: [Unleash feature availability and versioning](https://docs.getunleash.io/support/availability), [Unleash OSS and Enterprise comparison](https://docs.getunleash.io/support/oss-comparison), [Configure Unleash](https://docs.getunleash.io/deploy/configuring-unleash), [Unleash SDK overview](https://docs.getunleash.io/sdks), [Unleash GitHub](https://github.com/Unleash/unleash)

### OpenFeature

- vendor-neutral feature flag evaluation API 표준입니다.
- Java/Kotlin, Node.js, Python이 섞인 환경의 client contract로 유용합니다.
- 서버 제품이 아니므로 저장소, audit/history, 관리자 UI는 제공하지 않습니다.
- provider 뒤의 시스템이 persistence와 runtime update를 책임집니다.

출처: [OpenFeature Providers](https://openfeature.dev/docs/reference/concepts/provider/)

## 기각 후보: Self-hosted 불가능

### Vercel Edge Config / Vercel Flags

- Vercel 플랫폼에 내장된 managed edge config/feature flag 계열입니다.
- dashboard, targeting, segment, environment control은 참고할 만합니다.
- Self-hosted가 불가능하므로 핵심 솔루션 후보에서 제외합니다.

출처: [Vercel Edge Config](https://vercel.com/docs/edge-config), [Vercel Flags](https://vercel.com/docs/flags/vercel-flags)

### AWS KMS

- AWS managed key management service입니다.
- CloudTrail 기반 audit와 key permission 모델은 secret management 설계 때 참고할 수 있습니다.
- Self-hosted가 불가능하므로 핵심 솔루션 후보에서 제외합니다.

출처: [AWS KMS documentation overview](https://aws.amazon.com/documentation-overview/kms/)
