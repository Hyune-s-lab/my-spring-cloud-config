# 솔루션 리서치

## 결론

이 문서는 구현 완료 상태를 설명하지 않고, 공통 설정 관리 서버를 제로베이스에서 설계하기 위한 후보를 비교합니다. Spring Cloud Config를 선택한다면 Gitea는 Spring Cloud Config 입장에서 일반 Git remote로 보이므로 Git backend 후보가 됩니다.

새로 검토한 **Apollo**는 Spring Cloud Config의 backend가 아니라 Portal, Admin Service, Config Service, DB, SDK를 포함한 독립형 설정 관리 제품입니다. 특히 회사 요구가 `application / profile / cluster` 3중 구조라면, `application / profile` 중심인 Spring Cloud Config보다 `appId / clusterName / namespaceName`을 직접 노출하는 Apollo가 더 자연스럽습니다. 자세한 내용은 [Apollo 대안 리서치](02-apollo-alternative.md)에 분리했습니다.

- Gitea + Spring Config Git backend는 `label/version` 모델, commit history, pull request review, webhook 흐름이 자연스럽습니다.
- OpenBao KV path 구조를 Spring Config Git backend의 파일 구조로 옮기는 migration은 필요합니다.
- Gitea는 secret/config vault가 아니므로 민감값 저장, masking, audit device 성격은 OpenBao가 더 적합합니다.
- feature flag evaluation은 여전히 소비 애플리케이션이 직접 처리합니다. 필요해지면 facade/API를 별도로 추가합니다.

| Solution                   | Self-hosted           | SDK/API                       | UI | Audit/Persistence                 | Runtime Updates          | Pros                                                                                 | Cons                                                                                                |
|----------------------------|-----------------------|-------------------------------|----|-----------------------------------|--------------------------|--------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| Apollo                     | ✅                     | ✅ Java/.NET SDK<br>✅ HTTP API | ✅  | ✅ DB release/version<br>✅ rollback | ✅ SDK long polling/polling | `appId/clusterName/namespaceName` 구조라 회사의 `application/profile/cluster` 모델에 더 잘 맞습니다.<br>Portal, release, rollback, runtime update를 제품 기능으로 제공합니다. | Spring Cloud Config backend가 아니라 별도 config center입니다.<br>Kotlin Spring Boot 4+/Java 25 조합에서 client 호환성 검증이 필요합니다. |
| Gitea + Spring Config Git  | ✅                     | ✅ Git<br>✅ HTTP API           | ✅  | ✅ Git commit history<br>✅ PR trace | ✅ Webhook + Bus 확장      | Spring Cloud Config Git backend와 가장 자연스럽게 맞습니다.<br>branch/tag/commit 모델을 그대로 활용할 수 있습니다. | secret 저장소가 아니므로 민감값 관리에는 부적합합니다.<br>OpenBao KV path에서 Git 파일 구조로 migration이 필요합니다.          |
| OpenBao + Spring Config Vault | ✅                  | ✅ HTTP API<br>⚠️ generic clients | ✅  | ✅ KV v2 versioning<br>✅ audit devices | ⚠️ 별도 trigger 필요       | versioned KV, audit, policy, UI를 self-hosted로 제공합니다.                                  | Spring Config의 `label/version/state`와 자연스럽게 맞지 않습니다.<br>KV 변경 webhook callback이 기본 제공되지 않습니다.       |
| Spring Cloud Config        | ✅                     | ✅ HTTP API<br>✅ Spring client | ❌  | ⚠️ backend 의존                      | ✅ Actuator/Bus 확장       | Git/Vault backend, Spring client, refresh 흐름을 공식 기능으로 제공합니다.                     | 기본 조회 모델이 `application/profile` 중심입니다. `label`은 cluster가 아니라 branch/tag/commit 같은 version label입니다. |
| Unleash                    | ⚠️ Enterprise license | ✅ 다언어 SDK                     | ✅  | ⚠️ PostgreSQL 필수<br>⚠️ audit 제한   | ✅ SDK polling/cache      | feature flag 도메인이 성숙하고 self-hosted, 관리자 UI, 다언어 SDK를 제공합니다.                       | OSS는 project 1개, environment 2개 제한이 있어 `local/dev/qa/live/jp-live` 요구와 충돌합니다. PostgreSQL 운영도 필요합니다. |
| OpenFeature                | ✅                     | ✅ 표준 SDK/API                  | ❌  | ❌ 제공 안 함                          | ⚠️ provider 구현 의존      | Java/Kotlin, Node.js, Python 등에서 flag evaluation API를 표준화할 수 있습니다.                 | 서버 제품이 아니므로 관리자 UI, 저장소, audit/history, runtime update 경로는 별도로 필요합니다.                              |
| Vercel Edge Config / Flags | ❌                     | ⚠️ OpenFeature 지원             | ✅  | ✅ Vercel managed                  | ✅ platform 제공          | dashboard, targeting, segment, environment control, OpenFeature 지원 등 UX 참고 가치가 큽니다. | Vercel 플랫폼 의존으로 self-hosted가 불가능하므로 핵심 솔루션 후보에서 기각합니다.                                             |
| AWS KMS                    | ❌                     | ⚠️ AWS SDK                    | ⚠️ | ✅ AWS managed<br>✅ CloudTrail     | ❌ config runtime 아님     | secret/key management와 audit 설계 참고점이 있습니다.                                          | AWS managed service이고 feature flag/config 관리 도구가 아니므로 핵심 솔루션 후보에서 기각합니다.                           |

## OpenBao 후보와 Gitea 후보 비교

| Concern | OpenBao 방식 | Gitea 방식 | 판단 |
|---------|--------------|------------|------|
| Spring Config backend | Vault backend | Git backend | Spring Cloud Config를 선택한다면 둘 다 backend 후보가 됩니다. |
| 저장 모델 | `kv/{application}/{profile}` path | `{application}-{profile}.yml` 파일 | Spring Config API shape를 선택하면 조회 응답 shape는 유사하게 둘 수 있지만 데이터 구조 설계는 달라집니다. |
| Version | OpenBao KV v2 path별 version | Git commit hash | Git 방식이 Spring Config의 `version/label` 모델과 더 잘 맞습니다. |
| 변경 이력 | KV metadata + audit device | commit history + PR review | 일반 config 이력은 Git이 더 읽기 쉽습니다. API-level audit은 OpenBao가 더 강합니다. |
| 변경 알림 | KV 변경 webhook 없음 | Gitea repository webhook | Gitea가 Spring Cloud Config Monitor와 더 잘 맞습니다. |
| 민감값 | secret store 성격에 가까움 | Git에 평문 저장 위험 | API key/password는 Gitea보다 OpenBao 또는 별도 secret manager가 맞습니다. |
| 운영 부담 | OpenBao storage/unseal/policy 이해 필요 | Gitea repository/backup/DB 이해 필요 | Git 운영에 익숙한 팀이면 Gitea가 더 낮은 진입 장벽일 수 있습니다. |

## 후보별 메모

### Apollo

- self-hosted configuration management system입니다.
- Portal UI, Admin Service, Config Service, ApolloPortalDB, ApolloConfigDB로 구성됩니다.
- Quick Start는 H2 또는 MySQL로 로컬 실행할 수 있고, Docker Quick Start는 `apollo-quick-start`와 `mysql:8.0` 컨테이너를 사용합니다.
- 분산 배포는 MySQL 5.6.5+를 기본 전제로 하며, `ApolloPortalDB`는 보통 1개, `ApolloConfigDB`는 환경별 1개를 둡니다.
- 클라이언트는 Java/.NET SDK 또는 HTTP API를 사용합니다. Java/Spring은 Config Data Loader 방식으로 `spring.config.import=apollo://application` 같은 통합이 가능합니다.
- 변경 전파는 SDK의 HTTP long polling과 주기 polling fallback 구조입니다.
- Spring Cloud Config `Environment` 응답과 JSON shape가 다릅니다. 제로베이스에서는 Apollo API를 직접 쓰고, Spring Config 응답 shape가 필요할 때만 adapter/facade를 검토합니다.
- PostgreSQL은 공식 주 경로가 아니고 오래된 커뮤니티 포팅 사례만 문서에 언급됩니다. 현재 로컬 `local-postgres`는 Apollo 운영 DB로 바로 재사용하기 어렵습니다.

출처: [Apollo GitHub](https://github.com/apolloconfig/apollo), [Apollo Quick Start](https://www.apolloconfig.com/#/zh/deployment/quick-start), [Apollo Docker Quick Start](https://www.apolloconfig.com/#/zh/deployment/quick-start-docker), [Apollo Distributed Deployment Guide](https://www.apolloconfig.com/#/zh/deployment/distributed-deployment-guide), [Apollo Java SDK Guide](https://www.apolloconfig.com/#/zh/client/java-sdk-user-guide), [Apollo Other Language HTTP Client Guide](https://www.apolloconfig.com/#/zh/client/other-language-client-user-guide), [Apollo Open API Platform](https://www.apolloconfig.com/#/zh/portal/apollo-open-api-platform)

### Gitea

- self-hosted Git forge입니다.
- repository UI, commit history, pull request, repository webhook, HTTP API를 제공합니다.
- Spring Cloud Config Server는 Gitea를 별도 제품으로 인식할 필요 없이 Git remote로 clone/fetch 합니다.
- `label`은 branch/tag, `version`은 Git commit revision으로 표현할 수 있어 Spring Config 응답 모델과 잘 맞습니다.
- `spring-cloud-config-monitor`와 Spring Cloud Bus를 사용하면 Gitea webhook으로 `/monitor`를 호출하는 구조를 검토할 수 있습니다.
- secret store가 아니므로 API key/password는 평문 Git 저장을 피하고, 암호화 또는 별도 secret manager를 같이 검토해야 합니다.

출처: [Gitea Docker installation](https://docs.gitea.com/installation/install-with-docker), [Gitea webhooks](https://docs.gitea.com/usage/repository/webhooks), [Gitea API](https://docs.gitea.com/api/1.24/), [Spring Cloud Config Git Backend](https://docs.spring.io/spring-cloud-config/reference/server/environment-repository/git-backend.html), [Push Notifications and Spring Cloud Bus](https://docs.spring.io/spring-cloud-config/reference/server/push-notifications-and-bus.html)

### OpenBao

- MPL 2.0 오픈소스 Vault fork입니다.
- KV v2로 versioned key/value 저장, soft delete, undelete, metadata를 지원합니다.
- audit device가 API request/response를 기록하므로 변경 추적 기반을 제공합니다.
- Web UI와 HTTP API가 있어 운영자가 직접 관리할 수 있습니다.
- feature flag 제품은 아니므로 schema 검증, entitlement, 프론트 projection API가 필요해지면 별도 공통 설정 API 계층이 담당해야 합니다.
- Spring Cloud Config Vault backend로 조회할 수 있지만 `label/version/state` 모델은 Git backend보다 덜 자연스럽습니다.
- KV 변경 webhook callback이 기본 제공되지 않아 refresh trigger는 별도 설계가 필요합니다.

출처: [OpenBao KV v2](https://openbao.org/docs/2.3.x/secrets/kv/kv-v2/), [OpenBao audit devices](https://openbao.org/docs/2.3.x/audit/), [OpenBao UI](https://openbao.org/docs/2.4.x/configuration/ui/), [OpenBao HTTP API](https://openbao.org/api-docs/2.3.x/), [OpenBao license baseline](https://openbao.org/docs/policies/osps-baseline/)

### Spring Cloud Config

- Spring Cloud Config Server는 Git backend를 공식 지원하므로 Gitea repository를 설정 저장소로 사용할 수 있습니다.
- Git backend는 `spring.cloud.config.server.git.uri`로 repository 위치를 지정하고, JGit으로 clone/fetch 합니다.
- Vault backend도 공식 지원하므로 OpenBao를 계속 사용할 수도 있습니다.
- Spring client, `Environment`, `PropertySource` 모델과 잘 맞습니다.
- Actuator refresh와 Spring Cloud Bus로 런타임 refresh 확장이 가능합니다.
- feature flag evaluation은 제공하지 않으므로, Spring Cloud Config를 선택하더라도 소비자가 조회된 설정 값을 직접 판단합니다.
- non-Spring 서비스는 Spring Cloud Config HTTP API를 직접 쓰거나, 필요하면 별도 REST projection API와 polling/ETag/SSE 방식을 추가합니다.

#### Spring Runtime Refresh 판단 기준

Spring Cloud Config는 설정을 key 단위로 부분 조회하기보다 `application/profile` 단위로 `Environment`를 다시 읽습니다.  
런타임 반영 범위는 Config Server가 아니라 각 Spring 애플리케이션의 bean 설계로 제한합니다.

| 구분        | 의미                             | 예시                                                    | 판단                                              |
|-----------|--------------------------------|-------------------------------------------------------|-------------------------------------------------|
| 조회 단위     | Config Server가 원격 설정을 다시 읽는 단위 | `GET /config/my-service/dev`                          | profile source 전체를 다시 읽습니다.                     |
| 저장 단위     | Git 파일 또는 backend path 단위       | `my-service-dev.yml`, `kv/my-service/dev`             | 10개 변수 중 1개가 바뀌어도 source 전체를 다시 읽습니다.             |
| 런타임 반영 단위 | 애플리케이션 내부 bean/properties 단위   | `@RefreshScope`, `@ConfigurationProperties`           | 자주 바뀌는 2개 값만 별도 prefix/properties class로 분리합니다. |
| 변경 전파     | refresh를 시작하는 신호               | `POST /actuator/refresh`, `POST /actuator/busrefresh` | Git webhook을 쓰면 push 기반 trigger를 붙이기 쉽습니다.       |

출처: [Spring Cloud Config Git Backend](https://docs.spring.io/spring-cloud-config/reference/server/environment-repository/git-backend.html), [Spring Cloud Config Vault Backend](https://docs.spring.io/spring-cloud-config/reference/server/environment-repository/vault-backend.html), [Composite Environment Repositories](https://docs.spring.io/spring-cloud-config/reference/server/environment-repository/composite-repositories.html), [Push Notifications and Spring Cloud Bus](https://docs.spring.io/spring-cloud-config/reference/server/push-notifications-and-bus.html), [Spring Cloud Bus](https://docs.spring.io/spring-cloud-bus/docs/current/reference/html/index.html)

### Unleash

- feature flag 도메인, 관리자 UI, 다언어 SDK가 강점입니다.
- OSS는 project 1개, environment 2개 제한이 있어 다중 환경 요구와 충돌할 수 있습니다.
- self-hosted 운영에는 PostgreSQL이 필요합니다.
- 런타임 변경은 SDK polling/cache 구조로 처리합니다.
- 공통 설정 관리 전체보다는 feature flag 제품에 가깝습니다.

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
