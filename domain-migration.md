# Domain Migration: class.mr-romero.com → class.epaphrodit.us

**Date:** 2026-05-13
**Context:** School district network blocks `*.mr-romero.com` but allows `epaphrodit.us`. Students need to access Cinny + Matrix API via a domain the school doesn't block.

---

## Architecture Decision

**Keep `server_name` as `class.mr-romero.com`** — user IDs (e.g., `@student:class.mr-romero.com`) and room IDs (e.g., `!roomid:class.mr-romero.com`) are embedded in Matrix protocol and changing them would break everything.

**Change `public_baseurl` to `class.epaphrodit.us`** — this tells Synapse to issue OIDC redirects and construct client-facing URLs using the new domain. The server's identity stays the same; only the access point changes.

**Dual-domain through Cloudflare Tunnel** — both domains route through the same tunnel to the same services. Old domain still works for admin access.

---

## Changes Made

### 1. Cloudflare (done by Abraham)
- Added DNS record: `class.epaphrodit.us` → Cloudflare (proxied)
- Added tunnel route: `class.epaphrodit.us/*` → `http://localhost:8010` (Synapse)

### 2. Synapse — public_baseurl
**File:** `~/projects/matrix-classroom/deploy/synapse/data/homeserver.yaml`

```diff
- public_baseurl: "https://class.mr-romero.com"
+ public_baseurl: "https://class.epaphrodit.us"
```

`server_name` intentionally left as `class.mr-romero.com`.

### 3. Cinny — homeserver URL
**File:** `~/projects/matrix-classroom/deploy/cinny/config.json`

```diff
- "homeserverList": ["https://class.mr-romero.com"]
+ "homeserverList": ["https://class.epaphrodit.us"]
```

### 4. Hermes classroom-bot — MATRIX_HOMESERVER
**File:** `~/.hermes/profiles/classroom-bot/.env`

```diff
- MATRIX_HOMESERVER=https://class.mr-romero.com
+ MATRIX_HOMESERVER=https://class.epaphrodit.us
```

### 5. Hermes main profile — MATRIX_HOMESERVER
**File:** `~/.hermes/.env`

```diff
- export MATRIX_HOMESERVER=https://class.mr-romero.com
+ export MATRIX_HOMESERVER=https://class.epaphrodit.us
```

### 6. Google OAuth — redirect URI
**Console:** Google Cloud Console > APIs & Services > Credentials

```diff
- https://class.mr-romero.com/_synapse/client/oidc/callback
+ https://class.epaphrodit.us/_synapse/client/oidc/callback
```

*(Done by Abraham)*

---

## What Did NOT Change

| Item | Why |
|------|-----|
| `server_name` in homeserver.yaml | User IDs and room IDs depend on this — changing it invalidates everything |
| Room IDs in channel_prompts/config | Still `!roomid:class.mr-romero.com` — the `server_name` part of room IDs |
| User IDs | All `@user:class.mr-romero.com` — unchanged |
| Synapse signing key | Unrelated to domain |
| PostgreSQL databases | No schema changes |
| Honcho data | Unaffected — stored MXIDs reference server_name (unchanged) |
| Docker Compose `SYNAPSE_SERVER_NAME` | Matches `server_name` — intentionally kept as `class.mr-romero.com` |
| `matrix-cli.sh` HOMESERVER variable | Matches `server_name` for user ID construction |

---

## Files Updated

| File | What Changed |
|------|-------------|
| `deploy/synapse/data/homeserver.yaml` | `public_baseurl` |
| `deploy/cinny/config.json` | `homeserverList[0]` |
| `.hermes/profiles/classroom-bot/.env` | `MATRIX_HOMESERVER` |
| `.hermes/.env` | `MATRIX_HOMESERVER` |

### Documentation files updated

| File | Changes |
|------|--------|
| `SNAPSHOT.md` | Architecture diagram, OIDC URI, access URLs, homeserver listing |
| `plan.md` | MATRIX_HOMESERVER sample in Phase 4 |
| `TRACKER.md` | Domain chosen entry |
| `README.md` | Status blurb |
| `.hermes/profiles/classroom-bot/SOUL.md` | Scenario + Key Info server domain |

---

## Verification

After the changes, verified:

- `curl https://class.epaphrodit.us/_matrix/client/versions` → **200** ✅
- `curl https://class.mr-romero.com/_matrix/client/versions` → **200** (backward compat) ✅
- Both Hermes gateways (main + classroom-bot) running ✅
- Cinny container restarted ✅
- Synapse healthy ✅

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| OIDC login broken | Low | High | Redirect URI matches public_baseurl exactly — verified |
| Old access tokens invalid | Low (no active students) | Medium | No students using the platform yet — zero cost |
| Cinny config cached in browser | Medium | Low | First-time visit fetches fresh config; existing users clear cache |
| Cross-origin CORS issues | None | — | Same tunnel, same origin from Cloudflare's perspective |
| Both domains need maintenance | Low | Low | One tunnel config change covers both |
