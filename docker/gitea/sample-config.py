#!/usr/bin/env python3
"""
Gitea sample config repo 생성 스크립트.

사용법:
    python docker/gitea/sample-config.py

상단 설정:
    ACTION = "create"  # create 또는 clear

동작:
    - create: Gitea admin/user/repo를 준비하고 sample Spring Config 파일을 commit
    - clear: sample repository만 삭제

전제:
    - docker compose로 Gitea가 http://localhost:3100 에 떠 있어야 함
    - Gitea 컨테이너 이름은 common-config-gitea
"""

import base64
import json
import subprocess
import time
import uuid
import urllib.error
import urllib.request

ACTION = "create"

GITEA_ADDR = "http://localhost:3100"
GITEA_CONTAINER = "common-config-gitea"
GITEA_ADMIN_USERNAME = "gitea-admin"
GITEA_ADMIN_PASSWORD = "example"
GITEA_ADMIN_EMAIL = "gitea-admin@example.com"
CONFIG_OWNER = "common-config"
CONFIG_REPO = "config-repo"

SAMPLE_FILES = {
    "some-frontend-local.yml": """feature-toggles:
  new-home: true
  beta-search: true
  jp-banner: false
""",
    "some-frontend-dev.yml": """feature-toggles:
  new-home: true
  beta-search: true
  jp-banner: false
""",
    "some-frontend-qa.yml": """feature-toggles:
  new-home: false
  beta-search: true
  jp-banner: false
""",
    "some-frontend-live.yml": """feature-toggles:
  new-home: false
  beta-search: false
  jp-banner: false
""",
    "some-frontend-jp-live.yml": """feature-toggles:
  new-home: false
  beta-search: false
  jp-banner: true
""",
    "some-backend-dev.yml": """service:
  timeout-ms: 3000
  cache-enabled: true
  provider: local
""",
}


def main():
    wait_for_gitea()
    ensure_admin_user()
    token = create_access_token()

    if ACTION == "clear":
        delete_repo(token)
        return

    if ACTION != "create":
        raise SystemExit(f"지원하지 않는 ACTION 입니다: {ACTION}")

    ensure_org(token)
    ensure_repo(token)
    for path, content in SAMPLE_FILES.items():
        upsert_file(token, path, content)

    print(f"sample config repo ready: {GITEA_ADDR}/{CONFIG_OWNER}/{CONFIG_REPO}")


def wait_for_gitea():
    deadline = time.time() + 120
    while time.time() < deadline:
        try:
            request("GET", "/api/healthz")
            return
        except (ConnectionResetError, urllib.error.URLError):
            time.sleep(2)

    raise SystemExit("Gitea가 준비되지 않았습니다.")


def ensure_admin_user():
    run_gitea(
        "admin",
        "user",
        "create",
        "--admin",
        "--username",
        GITEA_ADMIN_USERNAME,
        "--password",
        GITEA_ADMIN_PASSWORD,
        "--email",
        GITEA_ADMIN_EMAIL,
        "--must-change-password=false",
        check=False,
    )


def create_access_token():
    output = run_gitea(
        "admin",
        "user",
        "generate-access-token",
        "--username",
        GITEA_ADMIN_USERNAME,
        "--token-name",
        f"common-config-sample-{uuid.uuid4().hex}",
        "--scopes",
        "all",
        check=True,
    )
    for line in output.splitlines():
        if line.startswith("Access token was successfully created:"):
            return line.rsplit(" ", 1)[-1].strip()

    raise SystemExit("Gitea access token 생성에 실패했습니다.")


def ensure_org(token):
    response = request("GET", f"/api/v1/orgs/{CONFIG_OWNER}", token=token, allow_404=True)
    if response is not None:
        return

    request(
        "POST",
        "/api/v1/orgs",
        token=token,
        body={
            "username": CONFIG_OWNER,
            "full_name": "Common Config",
            "visibility": "public",
        },
    )


def ensure_repo(token):
    response = request(
        "GET",
        f"/api/v1/repos/{CONFIG_OWNER}/{CONFIG_REPO}",
        token=token,
        allow_404=True,
    )
    if response is not None:
        return

    request(
        "POST",
        f"/api/v1/orgs/{CONFIG_OWNER}/repos",
        token=token,
        body={
            "name": CONFIG_REPO,
            "private": False,
            "auto_init": True,
            "default_branch": "main",
        },
    )


def delete_repo(token):
    response = request(
        "GET",
        f"/api/v1/repos/{CONFIG_OWNER}/{CONFIG_REPO}",
        token=token,
        allow_404=True,
    )
    if response is None:
        print("sample repository가 없습니다.")
        return

    request("DELETE", f"/api/v1/repos/{CONFIG_OWNER}/{CONFIG_REPO}", token=token)
    print(f"sample repository deleted: {CONFIG_OWNER}/{CONFIG_REPO}")


def upsert_file(token, path, content):
    existing = request(
        "GET",
        f"/api/v1/repos/{CONFIG_OWNER}/{CONFIG_REPO}/contents/{path}",
        token=token,
        allow_404=True,
    )
    encoded = base64.b64encode(content.encode()).decode()
    body = {
        "content": encoded,
        "message": f"Update {path}",
        "branch": "main",
    }

    if existing is None:
        request(
            "POST",
            f"/api/v1/repos/{CONFIG_OWNER}/{CONFIG_REPO}/contents/{path}",
            token=token,
            body=body,
        )
        return

    body["sha"] = existing["sha"]
    request(
        "PUT",
        f"/api/v1/repos/{CONFIG_OWNER}/{CONFIG_REPO}/contents/{path}",
        token=token,
        body=body,
    )


def request(method, path, token=None, body=None, allow_404=False):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if token is not None:
        headers["Authorization"] = f"token {token}"

    req = urllib.request.Request(
        f"{GITEA_ADDR}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req) as response:
            payload = response.read()
            if not payload:
                return {}
            return json.loads(payload.decode())
    except urllib.error.HTTPError as error:
        if allow_404 and error.code == 404:
            return None
        detail = error.read().decode()
        raise RuntimeError(f"Gitea API 요청 실패: {method} {path} {error.code} {detail}") from error


def run_gitea(*args, check=True):
    result = subprocess.run(
        ["docker", "exec", "--user", "git", GITEA_CONTAINER, "gitea", *args],
        check=False,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    if check and result.returncode != 0:
        raise RuntimeError(output)
    return output


if __name__ == "__main__":
    main()
