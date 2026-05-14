#!/usr/bin/env python3
"""Auto-convert new SSO users to 'support' type — blocks room creation."""

import json, os, sys
from urllib.request import Request, urlopen

SYNAPSE_URL = "http://localhost:8010"
ADMIN_TOKEN = os.environ.get("MATRIX_ADMIN_TOKEN", "")
if not ADMIN_TOKEN:
    with open(os.path.join(os.path.dirname(__file__), ".admin-token.env")) as f:
        ADMIN_TOKEN = f.read().strip().split("=", 1)[1].strip()

HOMESERVER = "class.mr-romero.com"
HEADERS = {
    "Authorization": f"Bearer {ADMIN_TOKEN}",
    "Content-Type": "application/json",
}

def api(method, path, data=None):
    url = f"{SYNAPSE_URL}{path}"
    body = json.dumps(data).encode() if data else None
    req = Request(url, data=body, headers=HEADERS, method=method)
    with urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())

def main():
    # List all users
    users = api("GET", "/_synapse/admin/v2/users?limit=200")
    changed = []
    for u in users.get("users", []):
        name = u["name"]
        user_type = u.get("user_type")
        is_admin = u.get("admin", False)
        localpart = name.split(":")[0].replace("@", "")

        # Skip admins, bots, and already-support users
        if is_admin or user_type == "support" or user_type == "bot":
            continue

        # Skip known teacher/admin accounts
        if localpart in ("admin", "aromero"):
            continue

        # This is a new SSO user — lock them down
        api("PUT", f"/_synapse/admin/v2/users/{name}", {"user_type": "support"})
        changed.append(localpart)

    if changed:
        print(f"🔒 Locked down: {', '.join(changed)}")
    else:
        print("✅ No new users to lock down")

if __name__ == "__main__":
    main()
