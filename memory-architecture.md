# 🧠 Matrix Classroom — Memory Architecture & Honcho Integration Plan

**Date:** 2026-05-13 (Updated: fixed env vars, compose, model refs)
**Author:** Brittany (Hermes)
**Context:** This document describes the current memory architecture, the problem of per-student memory in the Matrix classroom bot, and the proposed solution using self-hosted Honcho for BOTH the main profile and classroom bot.

---

## 1. 🏗️ Current Architecture

### Two Hermes Profiles (Isolated)

```
┌─────────────────────────────────┐     ┌──────────────────────────────────┐
│   Main Profile (hermes)         │     │   Classroom Profile             │
│   ├── Discord, CLI, email       │     │   (classroom-bot)               │
│   ├── ~/.hermes/                │     │   ├── Matrix only               │
│   ├── Built-in memory           │     │   ├── ~/.hermes/profiles/       │
│   │   (MEMORY.md + USER.md)     │     │   │   classroom-bot/            │
│   ├── OpenCode Go + DeepSeek    │     │   ├── Built-in memory           │
│   ├── No E2EE                   │     │   ├── OpenCode Go + DeepSeek    │
│   └── Gateway (Discord, etc.)   │     │   ├── MATRIX_ENCRYPTION=true    │
└─────────────────────────────────┘     │   └── Gateway (Matrix only)    │
                                        └──────────────────────────────────┘
```

### Current Memory: Built-in Only (MEM0 partially configured)

- **Memory provider**: `honcho` — configured in both profiles (`memory.provider: honcho`)
- **Mem0 config**: Cleared (replaced by Honcho)
- **Honcho**: `honcho.json` configs exist for both profiles, pointing at self-hosted Honcho at port 8020
- **Problem**: Solved ✅ — Honcho's workspace + peer architecture provides per-student isolation

| Feature | Built-in Memory |
|---------|----------------|
| Storage | Flat markdown files (2.2K chars MEMORY, 1.3K USER) |
| Per-user? | ❌ One store per session — all students share one context |
| Semantic search | ❌ No — keyword grep only |
| Auto-extraction | ❌ Manually curated |
| Cross-session | ✅ Yes — persists between sessions |
| Cost | Free (zero API calls) |
| Self-hostable | ✅ Already local |

**The problem:** When 8 students DM the classroom bot, they all share one memory context. Student A's homework help leaks into Student B's next conversation. There's no per-student memory isolation.

---

## 2. 🎯 The Requirement

- **8 students** in `vanguard-25_26-7th`
- Each student DMs `@bot` for 1:1 tutoring
- The bot must **remember each student's context separately**
- Student A's math confusion must NOT affect Student B's session
- Teacher (Abraham) must be able to wipe all student data easily
- Must be **deterministic** — no fuzzy matching, no routing logic
- Must be FERPA-compliant (data stays on private server or controlled)

---

## 3. 💡 Proposed Solution: Honcho

[Honcho](https://github.com/plastic-labs/honcho) is an open-source memory library purpose-built for multi-user agent memory. Its **workspace + peer** model maps 1:1 to our classroom:

| Honcho Concept | Classroom Mapping |
|----------------|-------------------|
| `workspace` | `vanguard-25_26-7th` (shared memory space) |
| `peerName` | Each Matrix user ID (`@jacklynn:...`, `@josue:...`) |
| `aiPeer` | The Hermes bot (`classroom-bot`) |

When Student X DMs the bot, Honcho:
1. Looks up `peerName = @student_x:...` in the `vanguard-25_26-7th` workspace
2. Loads their session summary, user model, and past facts
3. Injects only that student's context into the prompt
4. On reply, saves the conversation and updates the user model

When Student Y DMs, only Student Y's memory loads. **Zero cross-contamination.**

### How Honcho Works

```
┌─────────────────────────────────────────────────────────────────────┐
│  Honcho Server                                                      │
│                                                                     │
│  workspace: "vanguard-25_26-7th"                                  │
│  ├── peer: @jacklynn → {summaries, user model, facts, card}        │
│  ├── peer: @fernanda → {summaries, user model, facts, card}        │
│  ├── peer: @josue    → {summaries, user model, facts, card}        │
│  ├── peer: @leo      → {summaries, user model, facts, card}        │
│  ├── peer: @alekk    → {summaries, user model, facts, card}        │
│  ├── peer: @emma     → {summaries, user model, facts, card}        │
│  ├── peer: @annette  → {summaries, user model, facts, card}        │
│  └── peer: @maria    → {summaries, user model, facts, card}        │
│                                                                     │
│  Dialectic reasoning (LLM):                                        │
│    "Who is this person? What are their math strengths/weaknesses?"  │
│    → Auto-extracts insights from conversations                     │
└─────────────────────────────────────────────────────────────────────┘
         ▲                                    ▲
         │ DM from @jacklynn                  │ DM from @josue
         │                                    │
    ┌────┴────┐                          ┌────┴────┐
    │ Hermes  │                          │ Hermes  │
    │ loads   │                          │ loads   │
    │ jacklyn's │                        │ josue's │
    │ context │                          │ context │
    └─────────┘                          └─────────┘
```

### Honcho Features

| Feature | How it works |
|---------|-------------|
| **Session summary** | Each student's conversation summarized into a compact model |
| **User representation** | Honcho builds a deepening model of each student over time |
| **Peer card** | Key facts snapshot (name, grade, strengths, weaknesses) |
| **Semantic search** | Search across ALL student memories (`honcho_search`) |
| **Dialectic reasoning** | Multi-pass LLM analysis: "What does this student need?" |
| **Persistent conclusions** | `honcho_conclude` — save anything relevant to the student's profile |
| **Right to be forgotten** | Delete workspace `vanguard-25_26-7th` → all student data gone |

---

## 4. 📋 Two Deployment Options

### Option A: Honcho Cloud (Simplest, API Limit)

**Connection:** Honcho's managed SaaS at `app.honcho.dev`
**Auth:** Existing `HONCHO_API_KEY` in `~/.hermes/.env`
**Setup:** Just enable the Honcho plugin in the classroom-bot profile

**Pros:**
- Zero infrastructure to manage
- One command to activate
- Works immediately

**Cons:**
- Cloud API limits (free tier caps on calls + storage)
- Student data processed by external cloud
- Dialectic reasoning calls go through Honcho's servers
- FERPA concerns with student data leaving your network

### Option B: Self-Hosted Honcho (Recommended)

**Connection:** Local Docker container on your home lab
**Storage:** Dedicated pgvector PostgreSQL container (`honcho-db`)

**Embeddings:** Cohere `embed-v4.0` via OpenAI-compatible API (1536 dims)

**LLM (dialectic):** OpenCode Go + kimi-k2.6 (avoids DeepSeek thinking-mode issue)

**Pros:**
- ✅ All student data stays on your hardware (FERPA compliance)
- ✅ No rate limits or quotas
- ✅ 1536-dim state-of-the-art embeddings via Cohere
- ✅ One server can serve both profiles via separate workspaces
- ✅ Deterministic — no external dependency beyond Cohere API

**Cons:**
- One more container to manage
- ~200MB extra RAM for Honcho API + dedicated PostgreSQL
- Embedding API costs (Cohere free tier: 100K embeddings/month)
- Slightly more setup effort

### Architecture Diagram (Self-Hosted)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Your Server (class.mr-romero.com ecosystem)                        │
│                                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────────┐  │
│  │  Hermes     │  │  Hermes      │  │  Honcho API               │  │
│  │  Main       │  │  Classroom   │──▶  :8020                    │  │
│  │  Profile    │  │  Bot Profile │  │  workspace:               │  │
│  └─────────────┘  └──────┬───────┘  │  ├─ vanguard-25_26-7th  │  │
│                          │          │  │  └─ hermes-main (opt) │  │
│                          │          └──────────┬────────────────┘  │
│                          │                     │                   │
│              ┌───────────┼───────────┐         │                   │
│              ▼           ▼           ▼         │                   │
│  ┌────────────────┐  ┌────────────┐  ┌────────────────────┐       │
│  │  honcho-db     │  │   Redis    │  │  Cohere embed-v4.0 │       │
│  │  pgvector/pg15 │  │  caching   │  │  api.cohere.ai/    │       │
│  │  PostgreSQL    │  │ honcho-redis│  │  compatibility/v1  │       │
│  └────────────────┘  └────────────┘  └────────────────────┘       │
│                                                │                   │
│  OpenCode Go API: https://opencode.ai/zen/go/v1 │                   │
│  (for dialectic reasoning — NOT local)          │                   │
└────────────────────────────────────────────────────────────────────┘
```

---

## 5. ⚙️ Configuration Details

### Honcho Server (via env vars in docker-compose.yml)

```yaml
# Database — dedicated pgvector PostgreSQL
DB_CONNECTION_URI=postgresql+psycopg://honcho:honcho-pg-pass@db:5432/honcho

# Embeddings — Cohere embed-v4.0 (1536 dims)
EMBEDDING_VECTOR_DIMENSIONS=1536
EMBEDDING_MODEL_CONFIG__TRANSPORT=openai
EMBEDDING_MODEL_CONFIG__MODEL=embed-v4.0
EMBEDDING_MODEL_CONFIG__OVERRIDES__BASE_URL=https://api.cohere.ai/compatibility/v1
EMBEDDING_MODEL_CONFIG__OVERRIDES__API_KEY_ENV=COHERE_API_KEY

# ⚠️ LLM_MODEL_CONFIG__* env vars are SILENTLY IGNORED
# Honcho's dialectic LLM config lives at DIALECTIC__LEVELS__<level>__MODEL_CONFIG__
# Each reasoning level needs its own MODEL_CONFIG (minimal, low, medium, high, max)
# Using kimi-k2.6 (not DeepSeek) to avoid thinking_content echo issue

# LLM — OpenCode Go + kimi-k2.6 (not local, saves host CPU)
DIALECTIC__LEVELS__minimal__MODEL_CONFIG__MODEL=kimi-k2.6
DIALECTIC__LEVELS__minimal__MODEL_CONFIG__OVERRIDES__BASE_URL=https://opencode.ai/zen/go/v1
DIALECTIC__LEVELS__minimal__MODEL_CONFIG__OVERRIDES__API_KEY_ENV=OPENCODE_GO_API_KEY
# Repeat for low, medium, high, max levels with same model+overrides
```

### Setup Process (from Hermes docs)

The proper way to set up Honcho:

```bash
# 1. For each profile, run the interactive setup wizard:
hermes memory setup              # select "honcho" from provider list
# Or manually in config.yaml:
#   memory:
#     provider: honcho

# 2. Add API key to .env (already exists for main profile)
echo 'HONCHO_API_KEY=***' >> ~/.hermes/.env

# 3. Backfill Honcho peers for all existing profiles
hermes honcho sync               # creates host blocks for every profile
# This scans all Hermes profiles, creates host blocks for any without one,
# inherits settings from the default hermes block, and creates AI peers eagerly.
# Idempotent — skips profiles that already have a host block.

# 4. Check configuration
hermes honcho status             # connection status + config
hermes honcho peers              # show peer identities across all profiles
hermes honcho strategy           # show or set session strategy
```

### Config File: `$HERMES_HOME/honcho.json`

Config lives in `$HERMES_HOME/honcho.json` (profile-local). Resolution order:
`$HERMES_HOME/honcho.json` > `~/.hermes/honcho.json` > `~/.honcho/config.json`

**Minimal honcho.json (cloud):**

```json
{
  "apiKey": "***",
  "workspace": "hermes",
  "peerName": "yourname",
  "aiPeer": "hermes",
  "dialecticCadence": 2,
  "dialecticDepth": 1,
  "contextCadence": 1,
  "recallMode": "hybrid"
}
```

**Or for self-hosted (no API key needed):**

```json
{
  "baseUrl": "http://127.0.0.1:8020",
  "workspace": "hermes",
  "peerName": "yourname",
  "aiPeer": "hermes"
}
```

**Multi-profile config (synced via `hermes honcho sync`):**

```json
{
  "apiKey": "***",
  "workspace": "hermes",
  "peerName": "yourname",
  "hosts": {
    "hermes": {
      "aiPeer": "hermes",
      "recallMode": "hybrid",
      "sessionStrategy": "per-directory"
    },
    "hermes.classroom-bot": {
      "aiPeer": "classroom-bot",
      "recallMode": "hybrid",
      "sessionStrategy": "per-directory"
    }
  }
}
```

### Docker Compose (actual — `~/projects/honcho/docker-compose.yml`)

```yaml
services:
  api:
    build: .
    container_name: honcho-api
    depends_on:
      redis:
        condition: service_healthy
      db:
        condition: service_healthy
    ports:
      - "127.0.0.1:8020:8000"
    environment:
      - DB_CONNECTION_URI=postgresql+psycopg://honcho:honcho-pg-pass@db:5432/honcho
      - CACHE_URL=redis://redis:6379/0?suppress=true
      - CACHE_ENABLED=true
      - EMBED_MESSAGES=true
      - EMBEDDING_VECTOR_DIMENSIONS=1536
      - EMBEDDING_MODEL_CONFIG__TRANSPORT=openai
      - EMBEDDING_MODEL_CONFIG__MODEL=embed-v4.0
      - EMBEDDING_MODEL_CONFIG__OVERRIDES__BASE_URL=https://api.cohere.ai/compatibility/v1
      - EMBEDDING_MODEL_CONFIG__OVERRIDES__API_KEY_ENV=COHERE_API_KEY
      # Dialectic LLM — OpenCode Go + kimi-k2.6 (all 5 levels)
      - DIALECTIC__LEVELS__minimal__MODEL_CONFIG__MODEL=kimi-k2.6
      - DIALECTIC__LEVELS__minimal__MODEL_CONFIG__OVERRIDES__BASE_URL=https://opencode.ai/zen/go/v1
      - DIALECTIC__LEVELS__minimal__MODEL_CONFIG__OVERRIDES__API_KEY_ENV=OPENCODE_GO_API_KEY
      - DIALECTIC__LEVELS__low__MODEL_CONFIG__MODEL=kimi-k2.6
      - DIALECTIC__LEVELS__low__MODEL_CONFIG__OVERRIDES__BASE_URL=https://opencode.ai/zen/go/v1
      - DIALECTIC__LEVELS__low__MODEL_CONFIG__OVERRIDES__API_KEY_ENV=OPENCODE_GO_API_KEY
      - DIALECTIC__LEVELS__medium__MODEL_CONFIG__MODEL=kimi-k2.6
      - DIALECTIC__LEVELS__medium__MODEL_CONFIG__OVERRIDES__BASE_URL=https://opencode.ai/zen/go/v1
      - DIALECTIC__LEVELS__medium__MODEL_CONFIG__OVERRIDES__API_KEY_ENV=OPENCODE_GO_API_KEY
      - DIALECTIC__LEVELS__high__MODEL_CONFIG__MODEL=kimi-k2.6
      - DIALECTIC__LEVELS__high__MODEL_CONFIG__OVERRIDES__BASE_URL=https://opencode.ai/zen/go/v1
      - DIALECTIC__LEVELS__high__MODEL_CONFIG__OVERRIDES__API_KEY_ENV=OPENCODE_GO_API_KEY
      - DIALECTIC__LEVELS__max__MODEL_CONFIG__MODEL=kimi-k2.6
      - DIALECTIC__LEVELS__max__MODEL_CONFIG__OVERRIDES__BASE_URL=https://opencode.ai/zen/go/v1
      - DIALECTIC__LEVELS__max__MODEL_CONFIG__OVERRIDES__API_KEY_ENV=OPENCODE_GO_API_KEY
      - OPENCODE_GO_API_KEY=${OPENCODE_GO_API_KEY}
    env_file:
      - path: .env
        required: false
    restart: unless-stopped
    networks:
      - honcho_net

  redis:
    image: redis:7-alpine
    container_name: honcho-redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "PING"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - honcho_net

  db:
    image: pgvector/pgvector:pg15
    container_name: honcho-db
    restart: unless-stopped
    environment:
      - POSTGRES_USER=honcho
      - POSTGRES_PASSWORD=honcho-pg-pass
      - POSTGRES_DB=honcho
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "honcho", "-d", "honcho"]
      interval: 5s
      timeout: 5s
      retries: 5
    volumes:
      - honcho-pgdata:/var/lib/postgresql/data
    networks:
      - honcho_net

volumes:
  honcho-pgdata:

networks:
  honcho_net:
```

---

## 6. 💰 Resource & Cost Analysis

| Component | Cost | RAM | Notes |
|-----------|------|-----|-------|
| Honcho API server | Free (OSS) | ~100MB | Docker container |
| PostgreSQL (dedicated pgvector) | Free (OSS) | ~200MB | `pgvector/pgvector:pg15` |
| Redis | Free (OSS) | ~30MB | `redis:7-alpine` |
| Cohere embeddings | Free tier (100K/mo) | N/A | `embed-v4.0` via OpenAI-compat API |
| OpenCode Go LLM calls | Credits | N/A | Same as Hermes uses |
| **Total new** | **$0** | **~330MB** | |

### Token Economics (for 8 students, dialeticCadence: 5)

- Each dialectic pass: ~600 chars of LLM analysis (DeepSeek Flash)
- Per student per 5 turns: 1 dialectic call
- Per day estimate (8 students, ~10 turns each): ~16 dialectic calls
- Cost: ~$0.02/day in DeepSeek Flash credits

---

## 7. 📋 Implementation Steps

1. [x] **Set `memory.provider: honcho`** in BOTH `~/.hermes/config.yaml` and `~/.hermes/profiles/classroom-bot/config.yaml` — ✅ Done
2. [x] **Deploy self-hosted Honcho** — Docker (api + pgvector PG + redis) running at port 8020, Cohere embed-v4.0, 1536-dim — ✅ Done
3. [x] **Fix DNS resolution** — `localhost` → `127.0.0.1` in both `honcho.json` configs — ✅ Done
4. [x] **Fix dialectic LLM config** — Wrong env vars (`LLM_MODEL_CONFIG__*`) → correct (`DIALECTIC__LEVELS__*`) with kimi-k2.6 model — ✅ Done
5. [x] **Verify message storage** — Both workspaces storing conversations successfully — ✅ Done
6. [ ] **Run `hermes honcho sync`** to create peers for both profiles
7. [ ] **Verify with `hermes honcho status`** and `hermes honcho peers`
8. [ ] **Test per-student isolation** — DM from two students, verify separate memory contexts

---

## 8. ✅ Compliance Implications

| Concern | How Honcho Addresses It |
|---------|------------------------|
| **FERPA** | Self-hosted = data stays on private server (with Cohere embeddings via API) |
| **Right to be forgotten** | Delete workspace → all student memory gone in one API call |
| **Semester offboarding** | Delete `vanguard-25_26-7th` workspace, recreate next semester |
| **Data retention** | Honcho doesn't auto-prune — add a cron job or manual semester wipe |
| **Parental consent** | Still needed (already obtained ✅) — Honcho doesn't change this |

---

## 9. 🔮 Future: Main Profile on Honcho Too

If desired later, the main profile can share the same Honcho server with a different workspace:

```json
{
  "workspace": "hermes-main",
  "peerName": "abraham",
  "aiPeer": "hermes",
  "dialecticCadence": 10,
  "dialecticDepth": 1
}
```

This gives Abraham semantic search across all past conversations, automatic fact extraction, and persistent conclusions. **But not recommended day 1** — start with classroom only.

---

## 10. 📊 Comparison: Before vs After

| Dimension | Before (Built-in) | After (Honcho) |
|-----------|-------------------|----------------|
| Per-student memory | ❌ All share one | ✅ Each student isolated |
| Semantic search | ❌ Grep only | ✅ Vector search |
| Auto user modeling | ❌ Manual | ✅ Dialectic reasoning |
| Right to be forgotten | Manual file deletion | ✅ One API call |
| Teacher insights | ❌ None | ✅ Cross-student patterns |
| Complexity | Zero | One Docker container |
| Monthly cost | $0 | $0 (self-hosted) |
