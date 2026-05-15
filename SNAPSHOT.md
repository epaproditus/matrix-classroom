# Matrix Classroom — Project Snapshot
# Generated: 2026-05-15 (Warm-up DM system deployed — hook + plugin + context injection)

## Architecture
```
class.mr-romero.com / class.epaphrodit.us (Cloudflare Tunnel)
  ├── Synapse (port 8010) — Matrix homeserver
  ├── PostgreSQL — Database
  └── Cinny (port 8012) — Web client at https://class.epaphrodit.us

Hermes Profiles (running simultaneously):
  Main Profile (hermes)              Classroom Profile (classroom-bot)
  ├── Discord, CLI, email            ├── Matrix only
  ├── Honcho workspace hermes-main   ├── Honcho workspace vanguard-25_26-7th
  ├── OpenCode Go (DeepSeek)         ├── OpenCode Go (DeepSeek)
  ├── No E2EE                        ├── E2EE enabled (bot has decryption keys)
  └── Gateway (Discord, Matrix)      └── Gateway (Matrix only)

Attendance + Warm-up System (deployed 2026-05-15):
  Gateway Hook: classroom-attendance/handler.py
    ├── Intercepts !here / !roll via command:* events
    ├── Records check-in → ~/.hermes/classroom/attendance/YYYY-MM-DD.json
    ├── Creates DM room between @bot and student (if not cached)
    ├── Sends Bell Ringer problem via raw Matrix API (sub-100ms)
    └── Seeds ~/.hermes/classroom/active_warmups.json with problem context

  Plugin: matrix-warmup-context
    └── pre_llm_call hook → injects warm-up problem text + TEKS into LLM prompt
        automatically when student replies in DM. See ADR-004 (implemented).
```

## Users (4 active, 21 deactivated)
| User | Type | Role | Status |
|------|------|------|--------|
| admin | Admin | Server administration | ✅ Active |
| aromero | Support | Teacher | ✅ Active |
| hermes | Bot | Main Hermes AI assistant | ✅ Active |
| bot | Bot | Classroom bot (via classroom-bot profile) | ✅ Active |

All test student accounts were **soft-deactivated** via Synapse admin API on 2026-05-13 (pre-SSO cleanup). 21 deactivated accounts remain in the DB but cannot log in.

## Rooms & Spaces
| Room | ID | Purpose | Status |
|------|----|---------|--------|
| Playground | `!hGLjdogwxZhpXpKXSc:class.mr-romero.com` | Test/check-in room for teacher + admin | ✅ Active (public, no E2EE) |
| DM rooms | Created on-demand by `!here` hook | Per-student warm-up delivery | ✅ Auto-created, auto-cached |

Room creation is restricted by the `room_blocker` Synapse module — only @admin and @bot can create rooms. @bot creates DM rooms on demand via the Matrix API when students check in with `!here`.

## Security Restrictions
| Feature | Status | How |
|---------|--------|-----|
| Room creation (non-admin) | ❌ Blocked | Synapse room_blocker module — only @admin + @bot can create rooms |
| Room creation (@admin) | ✅ Allowed | Listed in room_blocker admin_users |
| Room creation (@bot) | ✅ Allowed | Listed in room_blocker admin_users (trusted bot, needed for operations) |
| Room creation (@aromero) | ❌ Blocked | By design — teacher account simulates student experience |
| Direct messages (with @bot) | ✅ Allowed | dm_allowed_users in room_blocker — students can DM @bot for tutoring |
| Direct messages (with other students) | ❌ Blocked | room_blocker blocks non-admin invites |
| Room_name/topic/avatar changes | ❌ Blocked | state_default=50 |
| Messaging | ✅ Allowed | events_default=0 |
| File uploads | ✅ Allowed | default |
| E2EE | ✅ Enabled (bot has keys) | MATRIX_ENCRYPTION=true in bot profile + server allows |
| Google SSO | ✅ Enabled | OIDC with Google Workspace |
| Room directory | ❌ Blocked | default deny |

## Classroom Bot Config
| Setting | Value | Why |
|---------|-------|-----|
| `require_mention` | `false` | Bot responds to bare `!here` without @-mention |
| `allowed_rooms` | Playground room ID only | Limits LLM response scope (hook handles `!here` regardless) |
| `free_response_rooms` | Playground room ID only | Same — hook is pre-LLM, so always fires |
| `max_turns` | 30 | Agent budget per session |

## Gateway Hooks & Plugins
| Component | Type | Location | Purpose |
|-----------|------|----------|---------|
| `classroom-attendance` | Gateway hook (HOOK.yaml) | `hooks/classroom-attendance/handler.py` | Intercepts `!here`/`!roll`, records attendance, sends warm-up DMs |
| `classroom-attendance` | Plugin | `plugins/classroom-attendance/plugin.yaml` | Registers `/here`, `/roll` as known commands (handler=None) |
| `matrix-warmup-context` | Plugin | `plugins/matrix-warmup-context/__init__.py` | `pre_llm_call` hook — injects warm-up context before every LLM call |

### Warm-up Context Pipeline
```
Student types !here
  → Hook catches command:here
    → Records attendance (JSON file)
    → Creates/reuses DM room via Matrix API
    → Sends warm-up problem (Bell Ringer pool, deterministic per-student/day)
    → Seeds ~/.hermes/classroom/active_warmups.json

Student replies in DM
  → Gateway routes to LLM session
  → pre_llm_call hook fires (matrix-warmup-context plugin)
    → Reads active_warmups.json for this user_id
    → Injects warm-up problem text + TEKS + instructions
  → LLM sees context, responds appropriately
  → Plugin marks status as "responded"
```

## Google SSO (OIDC)
- Provider: Google Workspace
- Client ID: 918206630189-cgam1e0uaqs1bgkr634rpabn9dreb3p5.apps.googleusercontent.com
- Client Secret: (stored in google-oauth-client.json)
- Redirect URI: https://class.epaphrodit.us/_synapse/client/oidc/callback
- allow_existing_users: true

## Access
### Web Client
https://class.epaphrodit.us (or class.mr-romero.com for admin)

### Desktop Client (alternative)
- Element Desktop: https://element.io/download
- Cinny Desktop: (available for some platforms)

### Direct Login
- Homeserver: class.epaphrodit.us (also accessible via class.mr-romero.com)
- Client: https://app.cinny.in (if externally accessible)

## Honcho Memory Layer 🧠
| Component | Status |
|-----------|--------|
| Honcho API (`:8020`) | ✅ Healthy — Up ~1h |
| PostgreSQL (pgvector) | ✅ Healthy — Up 4h |
| Redis cache | ✅ Healthy — Up 4h |
| Embeddings | ✅ Cohere embed-v4.0 (1536-dim) |
| Dialectic LLM | ✅ kimi-k2.6 via OpenCode Go |

**Data stored:**
| Workspace | Sessions | Messages | Purpose |
|-----------|----------|----------|---------|
| `hermes-main` | 5 | 26 | Discord/CLI conversations (verified working) |
| `vanguard-25_26-7th` | 3 | 14 | Classroom bot Matrix DMs |

**Key fixes applied (historical):**
- DNS: `localhost` → `127.0.0.1` (resolved init failures)
- Dialectic: `LLM_MODEL_CONFIG__*` → `DIALECTIC__LEVELS__*` (wrong env vars)
- Model: `deepseek-v4-flash` → `kimi-k2.6` (thinking mode incompatibility)
- API key: Full 67-char key (was truncated in `.env`)
- **E2EE alignment:** Removed `enable_room_encryption: false` from Synapse config; bot now uses `MATRIX_ENCRYPTION=true` with fresh crypto store (device `bot3`)
- **Room blocker:** Built and deployed `room_blocker.py` Synapse module (2026-05-14)

## Known Issues
| Issue | Status | Notes |
|-------|--------|-------|
| Honcho timeouts (30s MEMORY.md/USER.md uploads) | ⚠️ Intermittent | Adds ~60s latency to session startup |
| DeepSeek API rate limiting | ⚠️ Shared pool | Both gateways share same provider — can hit limits under concurrent load |
| Honcho dialectic timeouts | ⚠️ Intermittent | `honcho_reasoning` queries sometimes hang |
| Old room reference `!UZIftRiqrZRKXagMNr` in gateway logs | 🟢 Benign | Deleted room, gateway retry messages are harmless |

## Key Files
```
~/projects/matrix-classroom/
├── deploy/
│   ├── docker-compose.yml
│   ├── matrix-cli.sh
│   ├── .admin-token.env
│   ├── synapse/data/homeserver.yaml
│   └── synapse/modules/room_blocker.py   # Room creation blocker module
├── references/
│   └── warmup-context-system.md          # Full warmup hook + plugin architecture
├── onboarding-flow.md       # Bot's student onboarding script
├── student-profiles/        # Per-student profile markdown files
├── adr-004-command-context-pattern.md    # Send-and-seed pattern (implemented)
├── domain-migration.md      # Domain switch to class.epaphrodit.us
├── memory-architecture.md   # Honcho memory provider architecture
├── homeserver.yaml.backup   # Synapse config backup (room_blocker included)
└── comparison.md, plan.md, etc.
```

## Classroom Bot File Locations
| File | Path | Purpose |
|------|------|---------|
| Attendance data | `~/.hermes/classroom/attendance/` | Daily JSON check-in records |
| Active warmups | `~/.hermes/classroom/active_warmups.json` | Current pending warm-up contexts |
| DM room cache | `~/.hermes/classroom/dm_rooms.json` | Student → DM room ID mapping |
| Hook handler | `~/.hermes/profiles/classroom-bot/hooks/` | `!here`/`!roll` interception |
| Plugin (warmup context) | `~/.hermes/profiles/classroom-bot/plugins/` | pre_llm_call context injection |
| Gateway config | `~/.hermes/profiles/classroom-bot/config.yaml` | require_mention, allowed_rooms |
| Bot env | `~/.hermes/profiles/classroom-bot/.env` | Matrix token, homeserver URL |
| Bot SOUL.md | `~/.hermes/profiles/classroom-bot/SOUL.md` | Bot personality and behavior |
| Gateway logs | `~/.hermes/profiles/classroom-bot/logs/` | gateway.log + agent.log + errors.log |

## CLI Quick Reference
```bash
cd ~/projects/matrix-classroom/deploy
source .admin-token.env

# List users
./matrix-cli.sh list-users

# List rooms
./matrix-cli.sh list-rooms

# Create user
./matrix-cli.sh create-user <name> <password>

# Reset password
./matrix-cli.sh reset-password <name> <newpass>
```
