# 🧠 Honcho Integration — Fix Log & Status

**Date:** 2026-05-13 (Updated: main profile storage verified working)
**Author:** Brittany (Hermes)

---

## Final Verdict
Both Honcho workspaces are now fully operational. Main profile stores Discord conversations (26+ msgs), classroom bot stores Matrix DMs (14 msgs). Dialectic running on kimi-k2.6. All four issues resolved.

---

## Problems Found & Fixed

### 🔴 Issue 1: DNS Resolution Failure

**Symptom:** `WARNING plugins.memory.honcho: Honcho init failed: Connection failed: [Errno -2] Name or service not known`

**Root cause:** Both `honcho.json` configs used `http://localhost:8020` as the base URL. The long-running classroom-bot gateway process occasionally failed to resolve `localhost` via DNS, especially during agent session initialization.

**Fix:** Changed `localhost` → `127.0.0.1` in both:
- `~/.hermes/honcho.json`
- `~/.hermes/profiles/classroom-bot/honcho.json`

---

### 🔴 Issue 2: Wrong Environment Variables for LLM Config

**Symptom:** `ValidationException` in Honcho dialectic (couldn't find model)

**Root cause:** `docker-compose.yml` had these env vars on Honcho's `api` service:
```yaml
- LLM_MODEL_CONFIG__OVERRIDES__BASE_URL=...
- LLM_MODEL_CONFIG__OVERRIDES__API_KEY_ENV=...
```
But `LLMSettings` (the config class these target) **has no `MODEL_CONFIG` field**. It only has `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `DEFAULT_MAX_TOKENS`, etc. These env vars were silently ignored.

The LLM config for Honcho's dialectic lives at:
```
settings.DIALECTIC.LEVELS[level].MODEL_CONFIG
```
Each reasoning level (minimal, low, medium, high, max) has its own `ConfiguredModelSettings` with its own `model`, `transport`, and `overrides`.

**Fix:** Replaced the dead `LLM_MODEL_CONFIG__*` env vars with correct `DIALECTIC__LEVELS__<level>__MODEL_CONFIG__*` env vars for all 5 reasoning levels (15 total).

**Before (wrong):**
```yaml
- LLM_MODEL_CONFIG__OVERRIDES__BASE_URL=https://opencode.ai/zen/go/v1
- LLM_MODEL_CONFIG__OVERRIDES__API_KEY_ENV=OPENCODE_GO_API_KEY
```

**After (correct):**
```yaml
- DIALECTIC__LEVELS__minimal__MODEL_CONFIG__MODEL=kimi-k2.6
- DIALECTIC__LEVELS__minimal__MODEL_CONFIG__OVERRIDES__BASE_URL=https://opencode.ai/zen/go/v1
- DIALECTIC__LEVELS__minimal__MODEL_CONFIG__OVERRIDES__API_KEY_ENV=OPENCODE_GO_API_KEY
# ... (repeated for low, medium, high, max)
```

---

### 🔴 Issue 3: Truncated API Key in Honcho `.env`

**Symptom:** `AuthenticationError` → DeepSeek API returned 403

**Root cause:** `~/projects/honcho/.env` had `OPENCODE_GO_API_KEY=sk-AMg...pe7E` — only **13 characters**, when the real key is **67 characters**. The middle portion (`...`) was literally three periods in the file, not masking.

**Fix:** Copied the full 67-char key from `~/.hermes/.env` into `~/projects/honcho/.env`.

---

### 🔴 Issue 4: DeepSeek Thinking Mode Incompatibility

**Symptom:** `BadRequestError` — `Error from provider (DeepSeek): The reasoning_content in the thinking mode must be passed back to the API.`

**Root cause:** DeepSeek's API returns `reasoning_content` in thinking mode. On subsequent API calls, DeepSeek requires this `reasoning_content` to be included in assistant messages in the conversation history. Honcho's OpenAI backend doesn't echo `reasoning_content` back in its message history, so tool-calling conversations fail on the second iteration.

**Fix:** Switched the dialectic model from `deepseek-v4-flash` → `kimi-k2.6`, which doesn't use thinking mode.

---

## Current Status

### ✅ Classroom Bot Profile (`vanguard-25_26-7th`)
| Component | Status |
|-----------|--------|
| Honcho connection (127.0.0.1:8020) | ✅ Connected |
| Session creation | ✅ Working |
| Message storage | ✅ Storing |
| Peer creation | ✅ Created for Abraham |
| USER.md import | ✅ Imported as starting context |
| Dialectic reasoning (kimi-k2.6) | ✅ Working |
| Per-student peers | ⏳ Pending (students use SSO now) |

### ✅ Main Profile (`hermes-main`)
| Component | Status |
|-----------|--------|
| Honcho connection (127.0.0.1:8020) | ✅ Connected |
| Dialectic responding | ✅ Working (kimi-k2.6) |
| Message storage | ✅ **26 messages and counting** (Discord conversations now routed through gateway) |

The DNS fix (`localhost` → `127.0.0.1`) was the missing link for main profile storage. After the fix, `sync_turn()` successfully writes every conversation turn to Honcho. This was verified by comparing gateway logs, Honcho API sessions, and raw PostgreSQL queries.

### ❌ Still Pending (from TRACKER.md)
- [ ] `hermes honcho sync` — create Honcho peers for all profiles
- [ ] Per-student memory verification (need real students)
- [ ] Warm-up cron (school-calendar-aware)
- [ ] Participation tracking

---

## Files Modified

| File | Change |
|------|--------|
| `~/.hermes/honcho.json` | `localhost` → `127.0.0.1` |
| `~/.hermes/profiles/classroom-bot/honcho.json` | `localhost` → `127.0.0.1` |
| `~/projects/honcho/docker-compose.yml` | `LLM_MODEL_CONFIG__*` → `DIALECTIC__LEVELS__*` + model kimi-k2.6 |
| `~/projects/honcho/.env` | Full 67-char API key |

## Honcho Docker Stack

| Container | Image | Port |
|-----------|-------|------|
| `honcho-api` | Custom (Dockerfile) | `127.0.0.1:8020→8000` |
| `honcho-db` | `pgvector/pgvector:pg15` | — |
| `honcho-redis` | `redis:7-alpine` | — |
