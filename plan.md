# Matrix Classroom AI — Implementation Plan

## Goal

Build a self-hosted Matrix-based classroom platform where students join team rooms, an AI bot facilitates discussion and tutoring, a moderation bot handles classroom management, and everything runs on Abraham's infrastructure.

---

## Chosen Stack 🎯

| Layer | Choice | Why |
|-------|--------|-----|
| **Homeserver** | **Synapse** | Only Matrix server with admin GUI |
| **Admin UI** | **Ketesa** | Modern web dashboard for managing users/rooms |
| **Student Client** | **Cinny** | Cleanest UI for students — Discord-like, just chat |
| **Teacher Client** | **Element** | More features for teacher (voice, admin) |
| **AI Bot** | **Hermes** | AI facilitation, tutoring, warm-ups |
| **Moderation Bot** | **Draupnir** | Auto-kick, word filters, ban propagation |
| **Badge Bot** | **Hermes** (not separate) | Claude recommends Hermes posts badges, not a 3rd bot |
| **Reverse Proxy** | **Caddy** | Auto-HTTPS, simpler than nginx for home lab |
| **Database** | PostgreSQL | Required by Synapse |

### What we're NOT using:
- ❌ **Conduit** — No admin GUI
- ❌ **Dendrite** — No admin GUI, forked
- ❌ **Rocket.Chat** — Not Matrix protocol, Hermes can't connect
- ❌ **Hydrogen** — Archived/dead (Element archived it)
- ❌ **Commet** — Adds confusion. Element for teacher is enough.

---

## Feature Ownership

| Feature | Handled by | Layer |
|---------|-----------|-------|
| ✅ Reactions / emoji | Matrix protocol + Cinny client | Protocol |
| ✅ Kick/ban users | Draupnir (auto) or manual (room power levels) | Bot / Protocol |
| ✅ Censor/filter words | Draupnir policy lists | Bot |
| ✅ Multiple bots | Matrix supports unlimited bot accounts | Protocol |
| 🏅 Badges | Hermes posts badge messages (no separate bot) | Bot |
| 🤖 AI discussion | Hermes | Bot |
| 📝 Warm-ups | Hermes via cron | Bot |
| 👩‍🏫 Teacher dashboard | **Need to build** — Ketesa manages infra, not pedagogy | Custom |

⚠️ **E2EE:** Classroom bot uses Hermes' built-in E2EE (`MATRIX_ENCRYPTION=true` + `mautrix[encryption]`). See ADR-002.

---

---

## Architecture Decision Records

### ADR-001: Two-Profile Architecture (2026-05-12)

**Status:** Accepted

**Context:** Hermes serves two distinct roles — Abraham's personal assistant (Discord, CLI, email, Mattermost) and the classroom AI bot (Matrix only). Running both from the same Hermes instance causes:
- Memory pollution (student conversations leak into personal assistant context)
- Config conflicts (E2EE needs for Matrix vs no-E2EE for platforms that don't support it)
- Gateway complexity (one gateway handling both Discord and Matrix with different behavior rules)

**Decision:** Use Hermes **profiles** to run the classroom bot as a fully independent agent.

A profile (`~/.hermes/profiles/<name>/`) is a completely separate Hermes home directory with its own:
- `config.yaml` — model, provider, tools, platform config
- `.env` — separate API keys
- `sessions/` — isolated SQLite session store
- `memory/` — zero memory pollution
- `gateway/` — runs its own gateway (Matrix only)
- `SOUL.md` — separate personality/prompt

**Consequences:**
- ✅ Student memories stay isolated — wipe the profile, wipe all student data
- ✅ Main profile untouched — Discord, CLI, personal configs unaffected
- ✅ Both gateways run simultaneously
- ⚠️ More RAM (another Hermes gateway process, ~200MB)
- ⚠️ Need to manage two gateways (start/stop/restart each)
- ⚠️ Profile needs its own provider API access (can clone main config)

### ADR-003: Honcho Memory Provider for Per-Student Memory (2026-05-13)

**Status:** Accepted ✅ (Deployed)

**Context:** The classroom bot needs per-student persistent memory — each student's conversation history, strengths, weaknesses, and tutoring context must be isolated. Built-in Hermes memory (MEMORY.md/USER.md) is a single shared store — all 8 students would pollute one context. Mem0 was initially considered but Honcho's workspace + peer architecture maps 1:1 to the classroom (one workspace per class period, one peer per student).

**Decision:** Replace Mem0 with Honcho as the external memory provider for both profiles:
- **Main profile** — Honcho workspace `hermes-main`, peer `abraham`, aiPeer `hermes`
- **Classroom-bot profile** — Honcho workspace `vanguard-25_26-7th`, peers per-student Matrix ID, aiPeer `classroom-bot`

**Self-hosted Honcho** on local Docker (dedicated pgvector PostgreSQL) for:
- FERPA compliance (all data on private server)
- No API rate limits (vs Honcho cloud free tier)
- Cost control
- Cohere `embed-v4.0` via OpenAI-compatible API (1536 dims)
- OpenCode Go + kimi-k2.6 for dialectic reasoning (avoids DeepSeek thinking-mode issue)

**Architecture:**
```
One Honcho Server (:8020)
├── workspace: "hermes-main"
│   ├── peer: abraham
│   └── aiPeer: hermes
└── workspace: "vanguard-25_26-7th"
    ├── peer: @jacklynn:class.mr-romero.com
    ├── peer: @fernanda:class.mr-romero.com
    ├── peer: @josue:class.mr-romero.com
    ├── peer: @leo:class.mr-romero.com
    ├── peer: @alekk:class.mr-romero.com
    ├── peer: @emma:class.mr-romero.com
    ├── peer: @annette:class.mr-romero.com
    ├── peer: @maria:class.mr-romero.com
    └── aiPeer: classroom-bot
```

**Configuration:**

1. ✅ Main profile `memory.provider: honcho` in `~/.hermes/config.yaml`
2. ✅ Classroom-bot profile `memory.provider: honcho` in its own `config.yaml`
3. ✅ `honcho.json` per profile with separate `workspace` values (hermes-main + vanguard-25_26-7th)
4. ✅ Self-hosted Honcho API at `http://localhost:8020` (api + pgvector PG + redis)

**Consequences:**
- ✅ Per-student memory isolation (deterministic by Matrix sender ID)
- ✅ Zero cross-contamination between students
- ✅ One API call to wipe all student data (delete workspace)
- ✅ Semantic search across student conversations
- ✅ Auto-extracted user models per student (dialectic reasoning)
- ⚠️ One additional Docker stack (~330MB RAM total)
- ⚠️ Honcho dialectic calls burn kimi-k2.6 credits (~$0.02/day for 8 students)
- ⚠️ Must manage Honcho migrations/database
- ⚠️ Embedding API costs (Cohere free tier: 100K embeddings/month)

### ADR-002: E2EE Re-Enabled for Classroom Bot (2026-05-12)

**Status:** Accepted

**Context:** We originally disabled E2EE server-wide (`enable_room_encryption: false`) because Hermes couldn't read encrypted messages. This worked but meant student conversations were unencrypted — not ideal for a classroom with minors.

**Decision:** Re-enable E2EE for the **classroom-bot profile only**, while keeping it disabled for the main profile. This leverages Hermes' built-in Matrix E2EE support (`MATRIX_ENCRYPTION=true` + `mautrix[encryption]`).

The bot generates its own device keys and stores them in `~/.hermes/profiles/classroom-bot/platforms/matrix/store/`. It decrypts incoming messages and encrypts outgoing responses automatically. Cross-signing recovery key (`MATRIX_RECOVERY_KEY`) allows other Matrix clients to trust the bot's device.

**Consequences:**
- ✅ Students get encrypted conversations
- ✅ Hermes can read and respond (it has the keys)
- ✅ Main profile stays unencrypted (no libolm dependency)
- ⚠️ Requires `apt install libolm-dev` + `pip install 'mautrix[encryption]'`
- ✅ Server-wide `enable_room_encryption` removed — E2EE now fully allowed

---

## Phases (reordered per Claude Code audit)

**Goal:** Get legal/policy foundations in place before any student data enters the system.

**Tasks:**
- [ ] Research COPPA/FERPA requirements for self-hosted chat + AI
- [ ] Determine if Hermes calls external LLM APIs (OpenCode Go + DeepSeek Flash) or local models
- [ ] Create parental consent form template
- [ ] Draft data retention/deletion policy
- [ ] Plan student offboarding (end-of-semester account cleanup)
- [ ] Get district IT approval if needed

**⚠️ OUT OF SCOPE:**
- Actual legal review → teacher/parents handle
- This is a documentation/knowledge phase

---

### 🧱 Phase 1: Infrastructure — Synapse + Ketesa

**Goal:** Docker stack running with admin dashboard accessible.

**Docker Compose stack:**
- Synapse (pinned version, not `:latest`)
- PostgreSQL 15+
- Ketesa admin UI
- Caddy (reverse proxy with auto-HTTPS)
- Uptime Kuma (monitoring)
- pg_dump cron job (backups)

**Definition of Done:**
- [ ] Docker Compose stack running
- [ ] Caddy providing HTTPS
- [ ] Can log into **Ketesa** admin UI via browser
- [ ] Can create/delete users via Ketesa
- [ ] Can create rooms and manage them
- [ ] Can log into **Cinny** as a test student
- [ ] Can send messages between test accounts
- [ ] Automated PostgreSQL backups configured
- [ ] Uptime Kuma monitoring set up

**⚠️ OUT OF SCOPE:**
- Federation → not needed for classroom
- SSO/Google login → deferred indefinitely (manual accounts via Ketesa)

---

### 👥 Phase 2: Classroom Structure (moved UP)

**Goal:** Room structure and student accounts working BEFORE bots are added.

**Experiment:** Create ONE team by hand (2-3 test accounts in one room). Validate workflow.

**Replicate:** Build a script to generate N team rooms from a roster CSV.

**Tasks:**
- [ ] Design team naming convention (e.g., `#team-alpha`, `#team-beta`)
- [ ] Create whole-class Matrix space ("Mr. Romero's Class 2026")
- [ ] Set up room hierarchy: Space → Team Rooms
- [ ] Disable E2EE for classroom rooms (bots need access)
- [ ] Create first team room with test accounts
- [ ] Verify team isolation (students only see their team)
- [ ] Test password reset / account recovery flow
- [ ] Script room creation from attendance CSV

**⚠️ OUT OF SCOPE:**
- Self-registration → accounts created by teacher via Ketesa
- SSO → manual accounts

---

### 🛡️ Phase 3: Draupnir Moderation (moved UP)

**Goal:** Moderation infrastructure exists BEFORE students use the platform.

**Rationale from Claude:** "Moderation must exist before students enter rooms. AI facilitation can wait."

**Tasks:**
- [ ] Deploy Draupnir Docker container (pinned version)
- [ ] Create Draupnir bot account
- [ ] Invite Draupnir to all team rooms
- [ ] Configure word-filter policy lists (start small)
- [ ] Test auto-kick on bad words
- [ ] Test manual kick/ban via Draupnir commands
- [ ] Tune policy lists — middle school slang will create false positives
- [ ] Set up moderation alert channel (DM to teacher)

**⚠️ OUT OF SCOPE:**
- Advanced ML-based moderation → word lists are fine
- Community policy lists → start with own list

---

### 🤖 Phase 4: Hermes Bot Integration — DONE ✅

**Goal:** Hermes AI bot lives in every team room. Uses a **separate Hermes profile** for memory isolation.

**Design decision:** See ADR-001 (Two-Profile Architecture), ADR-002 (E2EE Re-Enabled), and ADR-003 (Honcho Memory Provider).

| Component | Implementation |
|-----------|---------------|
| Profile | `hermes profile create classroom-bot` — isolated memory, config, gateway |
| E2EE | `MATRIX_ENCRYPTION=true` + `pip install 'mautrix[encryption]'` + `apt install libolm-dev` |
| Memory | **Honcho** — self-hosted, per-student workspace isolation |
| DM behavior | No @mention needed — responds to every DM |
| Room behavior | `require_mention: true` — only responds when @mentioned in group rooms |
| Provider | Same as main profile (OpenCode Go + kimi-k2.6 via `--clone`) |

**Profile config (`~/.hermes/profiles/classroom-bot/.env`):**
```
MATRIX_HOMESERVER=https://class.epaphrodit.us
MATRIX_ACCESS_TOKEN=...
MATRIX_ENCRYPTION=true
MATRIX_DEVICE_ID=classroom-bot
MATRIX_REQUIRE_MENTION=true
```

**Tasks:**
- [x] Profile created and configured
- [x] E2EE dependencies installed (libolm-dev + mautrix[encryption])
- [x] Matrix gateway connected to classroom server
- [x] DMs working — students can DM Hermes
- [x] **Deploy self-hosted Honcho** — Docker (api + pgvector PG + redis) at port 8020, Cohere embed-v4.0
- [x] **Configure `memory.provider: honcho`** in both profiles' config.yaml
- [x] **Create `honcho.json`** — workspace "hermes-main" for main, "vanguard-25_26-7th" for classroom-bot
- [ ] **Run `hermes honcho sync`** to create Honcho peers for all profiles
- [ ] **Test per-student isolation** — two students DM, verify separate memory
- [ ] Set up channel_prompts for bot behavior in different rooms
- [ ] Define Hermes behavior rules (see below)
- [ ] Warm-up via cron (school-calendar-aware)
- [ ] Participation tracking → Honcho per-student memory

**Hermes Behavior Specification (define before coding):**
```yaml
# When does Hermes speak?
speak_when:
  - mentioned_by_name: true       # @Hermes or "Hermes" in message
  - daily_warm_up: true           # Sends warm-up at class start
  - question_to_group: false      # Don't answer every question — let students discuss
  - no_recent_activity: true      # After 5+ min of silence, prompt discussion

# Limits
max_messages_per_minute_per_room: 2
cooldown_after_message: 30s       # Seconds before replying again

# Topics to refuse
refuse:
  - profanity
  - off_topic_during_class
  - direct_homework_answers        # Use scaffolding instead
  - personal_info_sharing

# Wrong answer handling
wrong_answer_behavior: scaffold   # Ask guiding questions, don't give answer
```

**⚠️ OUT OF SCOPE:**
- Grading → confirmed deferred
- Advanced NLP → basic participation tracking only

---

### 📝 Phase 5: Hermes Bot Behaviors

**Goal:** The AI bot does useful classroom things.

**Experiment:** ONE behavior — daily warm-up posting via cron (school-calendar-aware).

**Replicate:** Add discussion facilitation, DM tutoring, participation tracking.

**Behaviors:**
1. **Daily warm-up** — School-day-aware cron posts math problem
2. **Discussion facilitation** — Ask follow-ups, keep conversation going
3. **DM tutoring** — Students DM Hermes for 1:1 help
4. **Participation tracking** — Hermes logs who contributed
5. **Badge announcements** — Hermes posts "🏅 Maria earned Quick Thinker!"

**⚠️ OUT OF SCOPE:**
- Grading → deferred
- Analytics dashboard → maybe future

---

### 🔊 Phase 6: Teacher Dashboard (NEW)

**Goal:** Abraham can see participation, moderation events, and bot activity at a glance.

**Claude's insight:** "Ketesa manages Matrix infra, not classroom pedagogy. A teacher will want: who participated today? what did Hermes discuss? any moderation events?"

**Tasks:**
- [ ] Design dashboard views
- [ ] Determine data source (Honcho queries / logs?)
- [ ] Build simple web view or report script
- [ ] Show: per-student participation, moderation events, warm-up responses

**⚠️ OUT OF SCOPE:**
- Grading integration
- Student analytics beyond participation

---

## Roles

- **Abraham**: Teacher/admin — manages students, approves architecture, has Ketesa + dashboard access
- **Brittany (Hermes)**: Implementation engineer — builds infrastructure, writes configs, scripts
- **Claude Code**: External reviewer — audited the plan (see `claude-feedback.md`)

## Definition of Ready (Phase 1)

- [x] Homeserver selected: **Synapse**
- [x] Admin UI selected: **Ketesa**
- [x] Student client selected: **Cinny**
- [x] Moderation bot selected: **Draupnir**
- [x] Comparison research complete
- [x] External audit complete (Claude Code)
- [ ] Legal/compliance reviewed (COPPA/FERPA)
- [ ] Port/hosting available (Docker host)
- [ ] Domain/subdomain ready (or local-only)

## Definition of Done (Project)

V2 (updated per Claude feedback):
- [ ] Legal compliance documented (COPPA/FERPA)
- [ ] Students can log into Cinny from a browser
- [ ] Students are placed in team rooms — each team isolated
- [ ] **E2EE disabled for classroom rooms** (bots need access)
- [ ] Draupnir auto-moderates (word filter, kick)
- [ ] Hermes posts daily warm-ups (school-calendar-aware)
- [ ] Hermes facilitates discussion (mention-based + silence prompts)
- [ ] Hermes answers DMs (tutoring with scaffolding)
- [ ] Teacher dashboard shows participation/moderation data
- [ ] Automated backups running
- [ ] Monitoring alerts if Synapse goes down
- [ ] Student offboarding process documented

---

## External Audit

This plan was reviewed by Claude Code (Anthropic's coding agent) on 2026-05-12. See [`claude-feedback.md`](./claude-feedback.md) for the full audit.

**Top action items from Claude:**
1. ✅ Legal/compliance review before student data
2. ✅ Honcho memory design document → `memory-architecture.md` (complete)
3. ✅ Automated backups from day one
4. ✅ Password reset / account recovery flow
5. ✅ Disable E2EE for classroom rooms
6. ✅ Pilot with 3 students before full rollout
7. ✅ Version pin everything in Docker
8. ✅ Caddy for reverse proxy
9. ✅ Uptime Kuma for monitoring
10. ✅ Define Hermes behavior precisely before coding
11. ✅ Student offboarding plan

---

## Next Step

**Pick a domain/subdomain!** 🏠 Once I know that, I'll Docker Compose the whole stack and get you a login link you can open in your browser.
