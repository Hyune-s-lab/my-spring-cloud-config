#!/usr/bin/env python3
"""
OpenBao KV v2에 common-config 샘플 데이터를 생성하거나 삭제합니다.

IDE에서 이 파일을 바로 실행할 수 있도록 docker/.env를 자동으로 읽습니다.

Usage:
    python3 docker/openbao/sample-config.py
    python3 docker/openbao/sample-config.py --create
    python3 docker/openbao/sample-config.py --clear

상단 설정값을 바꿔서 IDE에서 바로 실행할 수 있습니다.
CLI option은 상단 설정값을 덮어씁니다.

Options:
    --create       샘플 config 생성
    --clear        샘플 path만 삭제
"""
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path


ACTION = "create"

DOCKER_DIR = Path(__file__).resolve().parents[1]


def load_dotenv():
    env_file = DOCKER_DIR / ".env"
    if not env_file.exists():
        return {}

    values = {}
    with open(env_file) as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip("\"'")

    return values


ENV = load_dotenv()
OPENBAO_ADDR = "http://localhost:8200"
OPENBAO_TOKEN = ENV.get("OPENBAO_TOKEN", ENV.get("COMMON_CONFIG_OPENBAO_TOKEN", ""))
OPENBAO_KV_MOUNT = "kv"


SAMPLE_CONFIGS = {
    "some-frontend": {
        "local": {
            "feature-toggles": {
                "new-home": True,
                "beta-search": True,
                "jp-banner": False,
            },
        },
        "dev": {
            "feature-toggles": {
                "new-home": True,
                "beta-search": True,
                "jp-banner": False,
            },
        },
        "qa": {
            "feature-toggles": {
                "new-home": True,
                "beta-search": False,
                "jp-banner": False,
            },
        },
        "live": {
            "feature-toggles": {
                "new-home": False,
                "beta-search": False,
                "jp-banner": False,
            },
        },
        "jp-live": {
            "feature-toggles": {
                "new-home": False,
                "beta-search": False,
                "jp-banner": True,
            },
        },
    },
    "some-backend": {
        "local": {
            "SERVER_PORT": "18080",
            "LOG_LEVEL": "DEBUG",
            "ENABLE_BATCH_WORKER": "true",
            "REQUEST_TIMEOUT_MS": "3000",
        },
        "dev": {
            "SERVER_PORT": "8080",
            "LOG_LEVEL": "DEBUG",
            "ENABLE_BATCH_WORKER": "true",
            "REQUEST_TIMEOUT_MS": "3000",
        },
        "qa": {
            "SERVER_PORT": "8080",
            "LOG_LEVEL": "INFO",
            "ENABLE_BATCH_WORKER": "true",
            "REQUEST_TIMEOUT_MS": "5000",
        },
        "live": {
            "SERVER_PORT": "8080",
            "LOG_LEVEL": "INFO",
            "ENABLE_BATCH_WORKER": "false",
            "REQUEST_TIMEOUT_MS": "5000",
        },
        "jp-live": {
            "SERVER_PORT": "8080",
            "LOG_LEVEL": "INFO",
            "ENABLE_BATCH_WORKER": "false",
            "REQUEST_TIMEOUT_MS": "7000",
        },
    },
}


def request_json(method, url, token, payload=None):
    body = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(
        url=url,
        data=body,
        method=method,
        headers={
            "Content-Type": "application/json",
            "X-Vault-Token": token,
        },
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode() or "{}")


def put_kv(addr, token, mount, path, data):
    url = f"{addr}/v1/{mount}/data/{path}"
    request_json("POST", url, token, {"data": data})


def delete_metadata(addr, token, mount, path):
    url = f"{addr}/v1/{mount}/metadata/{path}"
    try:
        request_json("DELETE", url, token)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise


def target_paths(application, environments):
    return [f"{application}/{environment}" for environment in environments]


def legacy_target_paths(application, environments):
    return [f"{application},{environment}" for environment in environments]


def clear_sample(args):
    for application, environments in SAMPLE_CONFIGS.items():
        paths = legacy_target_paths(application, environments) + target_paths(application, environments)

        for path in paths:
            delete_metadata(args.addr, args.token, args.mount, path)
            print(f"cleared {args.mount}/{path}")


def seed_sample(args):
    if args.action == "clear":
        clear_sample(args)
        return

    for application, environments in SAMPLE_CONFIGS.items():
        for environment, data in environments.items():
            path = f"{application}/{environment}"

            delete_metadata(args.addr, args.token, args.mount, f"{application},{environment}")

            put_kv(args.addr, args.token, args.mount, path, data)
            print(f"seeded {args.mount}/{path}")


def parse_args():
    parser = argparse.ArgumentParser(usage=__doc__)
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--clear", action="store_true", default=None)

    args = parser.parse_args()
    args.addr = OPENBAO_ADDR
    args.token = OPENBAO_TOKEN
    args.mount = OPENBAO_KV_MOUNT

    cli_create = args.create is True
    cli_clear = args.clear is True

    if cli_create and cli_clear:
        parser.error("--create and --clear cannot be used together")

    if cli_create:
        args.action = "create"
    elif cli_clear:
        args.action = "clear"
    else:
        args.action = ACTION

    if args.action not in {"create", "clear"}:
        parser.error("ACTION must be create or clear")

    if not args.token:
        parser.error("OPENBAO_TOKEN or docker/.env COMMON_CONFIG_OPENBAO_TOKEN is required")

    return args


if __name__ == "__main__":
    seed_sample(parse_args())
