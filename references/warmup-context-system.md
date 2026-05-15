# Warm-Up Context System

> Full architecture of the `!here` check-in, warm-up DM delivery, and context injection pipeline.
> Deployed 2026-05-15. Updated 2026-05-15.

## Overview

The warm-up context system solves a fundamental problem with the "send-and-seed" pattern (ADR-004):

> **Problem:** When a gateway hook sends a message outside Hermes (via raw Matrix API), the LLM has zero context when the student replies in that DM room.

**Solution:** A two-component system:
1. A **gateway hook** that intercepts `!here`, records attendance, sends the warm-up via Matrix API, and writes context to a JSON file
2. A **plugin** with a `pre_llm_call` hook that reads the file and injects the problem into the LLM prompt before every call

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    STUDENT FLOW                                  │
│                                                                   │
│  Student types "!here"                                            │
│       │                                                           │
│       ▼                                                           │
│  ┌─────────────────┐     ┌──────────────────────────┐            │
│  │ Gateway Hook     │────▶│ Attendance Record         │            │
│  │ (command:here)   │     │ ~/.hermes/classroom/     │            │
│  │                  │     │ attendance/YYYY-MM-DD.json│            │
│  │ 1. Record check- │     └──────────────────────────┘            │
│  │    in            │                                            │
│  │ 2. Create/reuse  │     ┌──────────────────────────┐            │
│  │    DM room       │────▶│ DM Room via Matrix API    │            │
│  │ 3. Send warm-up  │     │ (createRoom + send event) │            │
│  │ 4. Seed context  │     └──────────────────────────┘            │
│  └────────┬─────────┘                                            │
│           │                                                       │
│           ▼                                                       │
│  ┌─────────────────┐     ┌──────────────────────────┐            │
│  │ Seed Context     │────▶│ active_warmups.json      │            │
│  │ (JSON file)      │     │ Keyed by Matrix ID       │            │
│  │                  │     │ status: awaiting_response│            │
│  └─────────────────┘     └──────────────────────────┘            │
│                                                                   │
│  Student replies in DM                                            │
│       │                                                           │
│       ▼                                                           │
│  ┌─────────────────────────────────────────────────────┐          │
│  │ pre_llm_call Plugin                                  │          │
│  │ (matrix-warmup-context)                              │          │
│  │                                                      │          │
│  │ 1. Check platform == "matrix"                        │          │
│  │ 2. Get sender_id from kwargs                         │          │
│  │ 3. Look up sender_id in active_warmups.json          │          │
│  │ 4. If found + awaiting_response → inject context     │          │
│  │                                                      │          │
│  │ Context injected:                                     │          │
│  │ [Warm-Up Bell Ringer Context]                         │          │
│  │ The student (@s_aromero:...) was sent a warm-up...   │          │
│  │ Problem: slope of line through (2,4) and (4,8)       │          │
│  │ TEKS: 8.5I                                           │          │
│  │ [End Warm-Up Context]                                │          │
│  └─────────────────────────────────────────────────────┘          │
│                                                                   │
│  LLM sees context → responds intelligently                         │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Gateway Hook: `classroom-attendance`

**Location:** `~/.hermes/profiles/classroom-bot/hooks/classroom-attendance/handler.py`

**Registers for:** `command:*` events (via `HOOK.yaml`)

**Commands handled:**
- `!here` — Check-in (any user) + warm-up DM
- `!roll` — Attendance report (teacher only)

**Key functions:**

| Function | Purpose |
|----------|---------|
| `_handle_here(context)` | Check-in logic, teacher easter egg, warm-up dispatch |
| `_handle_roll(context)` | Teacher-only attendance report |
| `_send_warmup_dm(student_mxid)` | Selects problem, creates DM room, sends message |
| `_seed_context_file(student_mxid, warmup, room_id)` | Writes to `active_warmups.json` |
| `_get_or_create_dm_room(student_mxid)` | Create/reuse DM room between @bot and student |
| `_pick_warmup(student_mxid)` | Deterministic problem selection by day + student |
| `_friendly_name(user_id)` | Extracts localpart from Matrix ID (currently unused in greeting) |
| `_send_matrix_message(room_id, body)` | Raw Matrix API message send |

**Warm-up problem pool:** 4 problems covering TEKS 8.5A–8.5I (scatterplots, associations, trend lines, linear equations, slope). Problems are selected deterministically — same student gets same problem all day, different students get variety, changes daily.

### 2. Plugin: `matrix-warmup-context`

**Location:** `~/.hermes/profiles/classroom-bot/plugins/matrix-warmup-context/__init__.py`

**Registers for:** `pre_llm_call` hook (via `register()` function)

**Configuration:** None — reads `~/.hermes/classroom/active_warmups.json` automatically.

**Kwargs received from gateway:**
```python
session_id, user_message, conversation_history,
is_first_turn, model, platform, sender_id
```

**Plugin logic:**
1. Check `platform == "matrix"` — only Matrix sessions get warm-up context
2. Get `sender_id` from kwargs — this is the student's Matrix ID
3. Look up sender in `active_warmups.json` — must have `status: "awaiting_response"`
4. If found → construct context block and return it as `{"context": ctx}`
5. If not found → return `None` (pass through)

**Context block structure:**
```
[Warm-Up Bell Ringer Context]

The student (@s_aromero:class.mr-romero.com) was sent a warm-up problem.
Here is what was asked:

**Problem ID:** br_4
**TEKS:** 8.5I
**Problem text:**
📝 **Bell Ringer — Linear Equations**
A line passes through the points (2, 4) and (4, 8).
What is the slope of this line?

The student may be answering the problem or asking a question about
it. Use your judgement: if they gave an answer, respond appropriately
(affirm or scaffold). If they're asking for help, guide them step by
step with probing questions. Never reveal the answer directly.

[End Warm-Up Context]
```

### 3. Data Files

| File | Path | Format | Purpose |
|------|------|--------|---------|
| Active warmups | `~/.hermes/classroom/active_warmups.json` | JSON object, keyed by Matrix ID | Current pending warm-up contexts |
| DM cache | `~/.hermes/classroom/dm_rooms.json` | JSON object, keyed by Matrix ID | Maps students to their DM room IDs |
| Attendance | `~/.hermes/classroom/attendance/YYYY-MM-DD.json` | JSON array of check-in objects | Daily attendance records |

**active_warmups.json format:**
```json
{
  "@s_aromero:class.mr-romero.com": {
    "warmup_id": "br_2",
    "teks": "8.5C",
    "prompt": "📝 **Bell Ringer — Scatterplots**\n\nWhich type of association does this data show?...",
    "answer_hint": "As temperature goes up, sales go down. That's a negative association! (B)",
    "room_id": "!DzoxzLLwtiaeFZRZLn:class.mr-romero.com",
    "sent_at": "14:24:06",
    "sent_date": "2026-05-15",
    "status": "awaiting_response"
  }
}
```

## Gateway Config

**File:** `~/.hermes/profiles/classroom-bot/config.yaml`

```yaml
matrix:
  require_mention: false        # Bot responds to bare !here without @-mention
  free_response_rooms:
    - '!hGLjdogwxZhpXpKXSc:class.mr-romero.com'  # Playground room (the active room)
  allowed_rooms:
    - '!hGLjdogwxZhpXpKXSc:class.mr-romero.com'
plugins:
  enabled:
    - classroom-attendance      # Registers /here, /roll commands
    - matrix-warmup-context     # pre_llm_call context injection
```

## Bug History (2026-05-15)

These were discovered during testing and fixed in sequence:

### Bug 1: Config pointed to deleted rooms
**Symptom:** Bot ignored `!here` from the new Playground room because `free_response_rooms` and `allowed_rooms` still referenced deleted room IDs.

**Fix:** Updated config with the current Playground room ID.

### Bug 2: `require_mention: true`
**Symptom:** Bot only responded to `@bot !here`, not bare `!here`.

**Fix:** Set `require_mention: false`.

### Bug 3: Wrong file path for warmup context
**Symptom:** Plugin never found `active_warmups.json` because it used the profile-scoped `HERMES_HOME`, while the hook wrote to `~/.hermes/classroom/active_warmups.json`.

**Hook (writer):**
```python
_MAIN_HOME = Path.home() / ".hermes"  # Always ~/.hermes
```

**Plugin (reader) — before fix:**
```python
HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
# For classroom-bot profile, HERMES_HOME = ~/.hermes/profiles/classroom-bot/
# So it looked in ~/.hermes/profiles/classroom-bot/classroom/active_warmups.json
```

**Plugin (reader) — after fix:**
```python
_MAIN_HOME = Path.home() / ".hermes"  # Same as hook
ACTIVE_WARMUPS_PATH = _MAIN_HOME / "classroom" / "active_warmups.json"
```

### Bug 4: Wrong kwarg name in pre_llm_call
**Symptom:** Plugin checked `kwargs.get("user_id")` but the gateway passes `sender_id`. Always empty → always returned None → context never injected.

**Fix:**
```python
user_id = kwargs.get("sender_id", "") or kwargs.get("user_id", "")
```

### Bug 5: LLM hallucinated student name
**Symptom:** The warm-up greeting said "Good morning, s_aromero!" and the context message said "The student's reply IS their answer to this problem." The LLM saw the ugly username "s_aromero" and hallucinated "Leea" as the student's name. Also, every student message was treated as an answer attempt.

**Fixes:**
```python
# Greeting — no raw username
f"👋 Hey there! Here's your warm-up:\n\n"

# Context — include actual Matrix ID, don't assume everything is an answer
f"The student ({user_id}) was sent a warm-up problem. "
f"The student may be answering the problem or asking a question about "
f"it. Use your judgement: if they gave an answer, respond appropriately "
f"(affirm or scaffold). If they're asking for help, guide them step by "
f"step with probing questions. Never reveal the answer directly."
```

## Testing

### End-to-End Test
1. Type `!here` in the Playground room → expect "✅ Checked in! Check your DMs for the warm-up!"
2. Check DMs → expect warm-up Bell Ringer problem
3. Reply in DM → expect context-aware response (knows the problem)
4. Type `!roll` → expect attendance report (teacher only)

### Clean Reset
```bash
rm -f ~/.hermes/classroom/active_warmups.json
rm -f ~/.hermes/classroom/dm_rooms.json
rm -f ~/.hermes/classroom/attendance_watch.state
rm -rf ~/.hermes/classroom/attendance/*
```

### Debugging
- Check gateway log: `tail -f ~/.hermes/profiles/classroom-bot/logs/gateway.log | grep "inbound\|here\|warmup\|inject"`
- Check agent log: `grep "injected context\|Seeded warmup" ~/.hermes/profiles/classroom-bot/logs/agent.log`
- Check warmup file: `cat ~/.hermes/classroom/active_warmups.json`
- Check DM cache: `cat ~/.hermes/classroom/dm_rooms.json`

## Limitations & Future

### Current Limitations
- Only 4 Bell Ringer problems (can be extended in WARMUP_POOL)
- No school calendar awareness (every day is a school day)
- Warm-up problem selection is simple hash-based (not adaptive)
- No mechanism to mark warmup as "responded" after the LLM processes it (status stays "awaiting_response")

### Planned Improvements
- **Warm-up via cron** — Auto-send warm-ups at class start time, not just on `!here`
- **Forgetting curve spiral review** — Priority to TEKS the student hasn't seen recently
- **Evidence quality tracking** — Honcho stores whether the student got the warm-up right
- **Exit ticket flow** — `!exit` command with similar send-and-seed pattern
- **Skill-based warmup selection** — Pick problems targeting student's weak TEKS
