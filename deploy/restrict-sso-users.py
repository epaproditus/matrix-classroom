#!/usr/bin/env python3
"""Restrict new SSO users to 'support' type (can't create rooms/DMs)."""
import json, os, subprocess, sys

HOMESERVER = "http://localhost:8010"
EXEMPT = {
    "@admin:class.mr-romero.com",
    "@aromero:class.mr-romero.com",
    "@hermes:class.mr-romero.com",
}

def get_token():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".admin-token.env")
    with open(env_path) as f:
        for line in f:
            if line.startswith("ADMIN_TOKEN="):
                return line.strip().split("=", 1)[1]
    return ""

def main():
    token = get_token()
    if not token:
        print("ERROR: No admin token found")
        return 1
    result = subprocess.run(
        ["curl", "-s", f"{HOMESERVER}/_synapse/admin/v2/users?limit=200",
         "-H", f"Authorization: Bearer {token}"],
        capture_output=True, text=True, timeout=30
    )
    users = json.loads(result.stdout).get("users", [])
    changed = 0
    for u in users:
        name = u["name"]
        if name in EXEMPT or u.get("admin") or u.get("user_type") is not None:
            continue
        resp = subprocess.run(
            ["curl", "-s", "-X", "PUT", f"{HOMESERVER}/_synapse/admin/v2/users/{name}",
             "-H", f"Authorization: Bearer {token}",
             "-H", "Content-Type: application/json",
             "-d", '{"user_type": "support"}'],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(resp.stdout)
        if data.get("user_type") == "support":
            print(f"RESTRICTED: {name}")
            changed += 1
    if changed:
        print(f"Restricted {changed} new user(s) to support type.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
