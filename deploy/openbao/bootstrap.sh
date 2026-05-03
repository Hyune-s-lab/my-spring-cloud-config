#!/bin/sh
set -eu

# Learning-only bootstrap:
# - runs OpenBao with Raft storage
# - initializes and unseals automatically
# - creates a fixed common-config policy token

cat > /tmp/openbao.hcl <<'EOF'
ui = true
disable_mlock = true

listener "tcp" {
  address = "0.0.0.0:8200"
  tls_disable = true
}

storage "raft" {
  path = "/openbao/data"
  node_id = "openbao-0"
}

api_addr = "http://127.0.0.1:8200"
cluster_addr = "http://127.0.0.1:8201"
EOF

bao server -config=/tmp/openbao.hcl &
bao_pid="$!"

export BAO_ADDR="http://127.0.0.1:8200"

until bao status >/tmp/openbao-status.txt 2>&1; do
  status_code="$?"
  if [ "$status_code" = "2" ]; then
    break
  fi
  sleep 1
done

if grep -q "Initialized[[:space:]]*false" /tmp/openbao-status.txt; then
  bao operator init -key-shares=1 -key-threshold=1 > /openbao/data/init.txt
fi

unseal_key="$(awk -F': ' '/Unseal Key 1/ { print $2 }' /openbao/data/init.txt)"
root_token="$(awk -F': ' '/Initial Root Token/ { print $2 }' /openbao/data/init.txt)"

if grep -q "Sealed[[:space:]]*true" /tmp/openbao-status.txt; then
  bao operator unseal "$unseal_key"
fi

export BAO_TOKEN="$root_token"
bao secrets enable -path=kv -version=2 kv >/tmp/openbao-enable-kv.txt 2>&1 || true

cat > /tmp/common-config-policy.hcl <<'EOF'
path "kv/data/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "kv/metadata/*" {
  capabilities = ["read", "list", "delete"]
}
EOF

bao policy write common-config /tmp/common-config-policy.hcl
bao token lookup "$COMMON_CONFIG_OPENBAO_TOKEN" >/tmp/openbao-token-lookup.txt 2>&1 || \
  bao token create \
    -id="$COMMON_CONFIG_OPENBAO_TOKEN" \
    -policy=common-config \
    -no-default-policy \
    -display-name=common-config

wait "$bao_pid"
