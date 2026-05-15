# ADR-004: Command Hook Context Pattern (Send-and-Seed / Send-and-File)

**Date:** 2026-05-15
**Status:** Implemented (Option D — Send-and-File with pre_llm_call hook injection)

## The Dilemma

When a gateway hook sends a message outside the Hermes gateway (via direct
Matrix Client-Server API), the LLM has zero context when the student replies
in that DM room. The conversation chain is broken.

Every `!` command built this way will have the same context gap.

## The Four Options

### Option A — Current State (Send Only)
Hook sends warm-up via raw Matrix API. Fast. Zero LLM context.
- ✅ Sub-100ms, no LLM cost
- ❌ LLM is blind — asks "what are we working on?" or hallucinates
- ❌ Functionally broken for tutoring

### Option B — LLM Handles Everything
Hook records attendance only. LLM picks up the command and sends the
warm-up through the gateway naturally.
- ✅ Full context preserved (Hermes is the sender)
- ❌ ~1-3s latency added
- ❌ Burns API budget on a deterministic relay task

### Option C — Send-and-Seed (via Honcho)
Hook sends instantly via Matrix API (fast). Hook ALSO seeds Honcho with a
synthetic assistant message describing what was sent and what the expected
response looks like.
- ✅ Sub-100ms (honcho write is fire-and-forget)
- ✅ LLM has full context via Honcho memory injection
- ⚠️ Depends on Honcho reliability for context retrieval

### Option D — Send-and-File with pre_llm_call Plugin (IMPLEMENTED)
Hook sends instantly via Matrix API (fast). Hook ALSO writes context to a
JSON file (`active_warmups.json`). A `pre_llm_call` plugin reads the file
and injects the context directly into the LLM prompt before every call.
- ✅ Sub-100ms (file write is instant)
- ✅ Deterministic — no API calls, no Honcho dependency
- ✅ Context injected every turn, not just once
- ✅ Zero latency overhead — file read during the gateway's processing pipeline
- ⚠️ Must keep path in sync between hook and plugin (two bugs fixed 2026-05-15)

## Decision

**Option D was implemented.** The actual approach differs from the original
proposal (Option C via Honcho) because:
1. Honcho showed intermittent timeouts (30s+ for MEMORY.md/USER.md uploads)
2. File-based injection is simpler and more reliable
3. The `pre_llm_call` hook is called on EVERY turn, so context stays fresh

## Implementation: Send-and-File

### Architecture
```
Hook (command:here):
  Phase 1 — Synchronous (<50ms, blocks gateway response):
    └── Record attendance, validate command

  Phase 2 — Fire-and-forget (after gateway response):
    ├── Send warm-up via raw Matrix API
    └── Write to ~/.hermes/classroom/active_warmups.json:
        {
          "@student:server": {
            "warmup_id": "br_1",
            "teks": "8.5A",
            "prompt": "The problem text...",
            "answer_hint": "For LLM guidance only",
            "room_id": "!room123:server",
            "status": "awaiting_response"
          }
        }

Plugin (pre_llm_call):
  Every LLM call:
    └── Check if sender has pending warmup in active_warmups.json
        ├── Yes → inject problem + TEKS + guidance into prompt
        └── No  → pass through
```

### Components
| Component | Type | Path |
|-----------|------|------|
| `classroom-attendance` hook | Gateway hook (HOOK.yaml) | `~/.hermes/profiles/classroom-bot/hooks/classroom-attendance/handler.py` |
| `matrix-warmup-context` plugin | Hermes plugin (pre_llm_call) | `~/.hermes/profiles/classroom-bot/plugins/matrix-warmup-context/__init__.py` |
| Warmup state file | JSON | `~/.hermes/classroom/active_warmups.json` |
| Warmup problem pool | Python list in handler.py | `handler.py` — 4 problems, TEKS 8.5A–8.5I |
| Attendance data | JSON per day | `~/.hermes/classroom/attendance/YYYY-MM-DD.json` |
| DM room cache | JSON | `~/.hermes/classroom/dm_rooms.json` |

### Plugin Code
```python
def _inject_warmup_context(**kwargs) -> Optional[dict[str, str]]:
    platform = kwargs.get("platform", "")
    if platform != "matrix":
        return None

    # Gateway passes user identity as 'sender_id' in pre_llm_call hooks
    user_id = kwargs.get("sender_id", "") or kwargs.get("user_id", "")
    if not user_id:
        return None

    warmup = _load_pending_warmup(user_id)
    if not warmup:
        return None

    ctx = (
        "[Warm-Up Bell Ringer Context]\n\n"
        f"The student ({user_id}) was sent a warm-up problem. "
        f"Here is what was asked:\n\n"
        f"**Problem ID:** {warmup.get('warmup_id', '?')}\n"
        f"**TEKS:** {warmup.get('teks', '?')}\n"
        f"**Problem text:**\n{warmup.get('prompt', '?')}\n\n"
        f"The student may be answering the problem or asking a question about "
        f"it. Use your judgement: if they gave an answer, respond appropriately "
        f"(affirm or scaffold). If they're asking for help, guide them step by "
        f"step with probing questions. Never reveal the answer directly.\n\n"
        f"[End Warm-Up Context]"
    )
    return {"context": ctx}
```

## Bugs Fixed (2026-05-15)

| Bug | Symptom | Root Cause | Fix |
|-----|---------|-----------|-----|
| Context never injected | Bot responded as if no warmup existed | Plugin looked for `user_id` kwarg, gateway passes `sender_id` | Changed to `sender_id` with `user_id` fallback |
| Context file never found | Plugin couldn't read warmup data | Plugin used profile-scoped `HERMES_HOME`, hook hardcoded `~/.hermes` | Both now use `Path.home() / ".hermes"` |
| LLM hallucinated name | Bot called user "Leea" | Greeting used raw username, context had no identity info | Generic greeting + Matrix ID in context |

## Hooks that NEED seeding (send-and-file):
- `!here` — sends warm-up → student expected to reply
- `!exit` — sends exit ticket → student expected to reply
- `!hint` — sends scaffolded hint → student expected to use it
- `!check` — sends comprehension check → student expected to answer
- Any hook that creates a DM conversation chain

## Hooks that do NOT need seeding:
- `!roll` — teacher-only, no follow-up expected
- `!pause` / `!resume` — orchestrator control, no student DM
- Any teacher-only command

## Migration Path

When the Lesson Orchestrator (§4.1 of infrastructure-design.md) replaces
the standalone attendance hook, the send-and-file pattern moves to a
formal `slot_dispatch` → Honcho write in the orchestrator's state machine.
The file-based approach is a simpler interim solution that works today.

## References
- [`references/warmup-context-system.md`](references/warmup-context-system.md) — Full architecture walkthrough
- VISION.md §4.5 — Attendance Check-in
- infrastructure-design.md §4.1 — Lesson Orchestrator
- infrastructure-design.md §4.10 — Attendance Tracking (migration path)
- bluebonnet-runtime-spec.json — Bell Ringer slot definition
