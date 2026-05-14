# Matrix Classroom — Project Snapshot
# Generated: 2026-05-14 (Room blocker deployed — Synapse custom module + config)

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
- 🏫 **All rooms were deleted** during user cleanup (2026-05-13) and room_blocker testing (2026-05-14)
- No rooms currently exist on the server
- @admin will recreate team rooms when students are ready to onboard

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

**Key fixes applied:**
- DNS: `localhost` → `127.0.0.1` (resolved init failures)
- Dialectic: `LLM_MODEL_CONFIG__*` → `DIALECTIC__LEVELS__*` (wrong env vars)
- Model: `deepseek-v4-flash` → `kimi-k2.6` (thinking mode incompatibility)
- API key: Full 67-char key (was truncated in `.env`)
- **E2EE alignment:** Removed `enable_room_encryption: false` from Synapse config; bot now uses `MATRIX_ENCRYPTION=true` with fresh crypto store (device `bot3`)
- **Room blocker:** Built and deployed `room_blocker.py` Synapse module (2026-05-14). Blocks room creation for non-admin users. @aromero intentionally excluded — simulates student experience.

## Key Files
```
~/projects/matrix-classroom/
├── deploy/
│   ├── docker-compose.yml
│   ├── matrix-cli.sh
│   ├── .admin-token.env
│   ├── synapse/data/homeserver.yaml
│   └── synapse/modules/room_blocker.py   # Room creation blocker module
├── onboarding-flow.md    # Bot's student onboarding script
├── student-profiles/      # Per-student profile markdown files
├── domain-migration.md    # Domain switch to class.epaphrodit.us
├── memory-architecture.md     # Honcho memory provider architecture
├── homeserver.yaml.backup     # Synapse config backup (room_blocker included)
├── student-creds.md
├── google-oauth-client.json
└── comparison.md, plan.md, etc.
```

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
