# On-prem Docker Compose

이 디렉터리는 on-prem 설치 목표를 위한 Docker Compose 구성을 담습니다.

## 현재 단계

아직 common-config 애플리케이션 이미지가 없으므로 기본 실행은 OpenBao만 대상으로 합니다.

```bash
cp .env.example .env
docker compose up -d openbao
```

OpenBao UI:

```text
http://localhost:8200
```

학습 편의를 위해 Docker Compose는 OpenBao를 자동 initialize/unseal 합니다. `COMMON_CONFIG_OPENBAO_TOKEN`은 common-config가 OpenBao API를 호출할 때 쓰는 토큰이며, `.env.example`의 값으로 common-config 전용 policy token을 생성합니다.

초기 root token과 unseal key는 Docker volume의 `/openbao/data/init.txt`에 저장됩니다. 이 구성은 학습용 shortcut이며 운영용 보안 모델은 아닙니다.

## 최종 목표

common-config 이미지가 준비되면 같은 compose 파일로 OpenBao와 common-config 서버를 함께 실행합니다.

```bash
cp .env.example .env
COMMON_CONFIG_IMAGE=common-config:latest \
docker compose --profile app up -d
```

## 구성 원칙

- OpenBao는 Integrated Storage(Raft)를 사용합니다.
- Docker Compose에서는 `openbao-data` named volume을 사용합니다.
- K8s 배포 시에는 StatefulSet + PVC 구조로 전환합니다.
- OpenBao root token은 common-config 서버에 전달하지 않습니다.
- 운영 환경에서는 TLS, policy, token rotation, Raft snapshot backup을 별도 설정합니다.
