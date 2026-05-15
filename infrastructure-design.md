# Matrix Classroom — Infrastructure Design

> **Status:** Draft 1
> **Date:** 2026-05-13
> **Inputs:** `VISION.md`, `plan.md`, `gemini-research-analysis.md`
> **Purpose:** Forward-looking technical design that reconciles the current deployed stack with the "curriculum as code" vision and the risks surfaced by the Gemini research paper. Not a re-statement of the vision — a buildable specification.

---

## 0. Scope

**In scope**
- Service topology, ports, processes, and data flow for the production classroom platform
- New subsystems required by the reframed vision: Lesson Orchestrator, `bluebonnet-runtime` spec, Content Pipeline, Teacher Radar, Math Verifier, Math Input Handler, FERPA Audit Log, Lesson Playback Studio
- How those subsystems compose with what is already deployed (Synapse, Cinny, Hermes classroom-bot profile, Honcho)
- Reliability, SPOF mitigation, and operational primitives required for a live K–8 classroom
- Data architecture, retention windows, and FERPA-mapped data lifecycle

**Out of scope (deferred to other docs)**
- Pedagogical content of any individual lesson — owned by `~/Bluebonnet/`
- Bot personality and tone — owned by `~/.hermes/profiles/classroom-bot/SOUL.md`
- Legal text of consent forms — owned by `compliance.md`
- Decision rationale already captured in ADR-001/002/003 in `plan.md`

---

## 1. Architectural north star

The unifying frame from the brainstorm — and the one this design follows — is **curriculum as code** (Claude Opus). A lesson is not a PDF or a slide deck; it is an executable program with state, timers, branching, peer-discourse hooks, and per-student memory.

This produces a clean three-layer separation:

```
┌────────────────────────────────────────────────────────────┐
│  Layer 3  CONTENT       Authored .lesson files               │
│           (the program)  (typed slots, TEKS tags, stems)     │
├────────────────────────────────────────────────────────────┤
│  Layer 2  RUNTIME       Lesson Orchestrator                  │
│           (the interpreter) (state machine, timers, routing) │
├────────────────────────────────────────────────────────────┤
│  Layer 1  TRANSPORT     Matrix + Honcho + Hermes             │
│           (the OS)       (rooms, memory, LLM, gateway)       │
└────────────────────────────────────────────────────────────┘
```

Layer 1 is mostly built. Layer 2 is what this design specifies. Layer 3 is authored content, governed by the `bluebonnet-runtime` spec defined in §4.2.

**Principle the design enforces:** the runtime never makes pedagogical decisions. It dispatches typed slots from a `.lesson` file. Anything that requires judgment (paraphrasing, intervention timing, evaluation) is either pre-authored in the lesson file, deferred to the teacher via the Teacher Radar channel, or routed to a verified subroutine (math verifier, photo grader). This is what prevents the "curriculum fidelity drift" Opus flagged.

---

## 2. Current state vs. target state

### What is deployed today (per `SNAPSHOT.md` and `deploy/docker-compose.yml`)

```
Host
├── matrix-synapse        :8010  Synapse homeserver, room_blocker module loaded
├── matrix-postgres       —      Synapse DB
├── matrix-ketesa         :8011  Admin UI
├── matrix-cinny          :8012  Student web client
├── honcho-api            :8020  Memory layer
├── honcho-pgvector       —      Honcho DB
├── honcho-redis          —      Honcho cache
├── hermes (main)         —      Personal assistant gateway
└── hermes (classroom)    —      Matrix-only gateway, E2EE enabled
```

External: Cloudflare Tunnel terminating at `class.mr-romero.com` / `class.epaphrodit.us`. Google Workspace OIDC for SSO.

### What this design adds

```
Host (additions)
├── lesson-orchestrator   :8030  HTTP service + Matrix client (LRO state machine)
├── teacher-radar         (in-orchestrator) Private DM channel manager
├── math-verifier         :8031  ValiMath-pattern step validator (sympy + LLM)
├── math-input            :8032  Photo intake + vision grading
├── ferpa-audit           :8033  Human-readable parallel log writer/exporter
├── playback-studio       :8034  Session timeline + heatmap generator (Phase 2)
├── content-pipeline      (cron/CLI) PDF/PPTX/JSON → .lesson compiler
├── draupnir              —      Moderation bot (planned Phase 3)
├── uptime-kuma           :8090  Monitoring
└── caddy or cloudflared  :443   TLS termination (already via tunnel)
```

Nothing in Layer 1 is replaced. Every new service is a tenant of the existing Matrix + Honcho + Hermes substrate.

---

## 3. Service topology

```
                             ┌─────────────────────────────┐
                             │   Cloudflare Tunnel          │
                             │  class.epaphrodit.us         │
                             └──────────────┬──────────────┘
                                            │
                          ┌─────────────────┼─────────────────┐
                          │                 │                 │
                  ┌───────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐
                  │  Synapse     │  │  Cinny       │  │ Photo Intake │
                  │  :8010       │  │  :8012       │  │  (form POST) │
                  └───────┬──────┘  └──────────────┘  └───────┬──────┘
                          │ Matrix events                      │
       ┌──────────────────┼──────────────────────┐             │
       │                  │                      │             │
┌──────▼───────┐  ┌───────▼────────┐  ┌──────────▼─────────┐  │
│ Hermes       │  │ Lesson         │  │ Math Input         │◄─┘
│ classroom-bot│◄►│ Orchestrator   │  │  :8032             │
│ (gateway)    │  │  :8030         │  │  vision model      │
└──────┬───────┘  └──┬─────────┬───┘  └──────────┬─────────┘
       │            │         │                  │
       │  responses │  teacher│ DM               │ graded result
       │            │  alerts │                  │
       │            ▼         ▼                  ▼
       │      ┌─────────────────┐       ┌────────────────┐
       │      │ Teacher Radar   │       │ Math Verifier  │
       │      │ (in-orchestr.)  │       │  :8031         │
       │      └─────────────────┘       └────────────────┘
       │
       ▼  embeddings + dialectic
┌──────────────┐
│ Honcho :8020 │──► pgvector ──► reasoning pipeline
└──────┬───────┘
       │ change events
       ▼
┌──────────────────┐
│ FERPA Audit Log  │  human-readable, append-only
│  :8033 (writer)  │
└──────────────────┘
                       ▲
                       │ nightly export
                       │
┌──────────────────┐   │
│ Playback Studio  │───┘  session timelines, heatmaps
│  :8034           │
└──────────────────┘
```

All services bind to `127.0.0.1`; only Synapse and Cinny are exposed through the Cloudflare Tunnel. Internal traffic stays on the loopback. Photo intake is a privileged path (image upload) and is documented separately in §4.5.

### Port map (single source of truth)

| Service              | Port | Bind    | Public? | Owner             |
|----------------------|------|---------|---------|-------------------|
| Synapse              | 8010 | 127.0.0.1 | via tunnel | Layer 1     |
| Ketesa admin         | 8011 | 127.0.0.1 | no      | Layer 1            |
| Cinny client         | 8012 | 127.0.0.1 | via tunnel | Layer 1     |
| Honcho API           | 8020 | 127.0.0.1 | no      | Layer 1            |
| Herald (Honcho UI)   | 8021 | 127.0.0.1 | no      | Layer 1            |
| Lesson Orchestrator  | 8030 | 127.0.0.1 | no      | Layer 2 (new)      |
| Math Verifier        | 8031 | 127.0.0.1 | no      | Layer 2 (new)      |
| Math Input           | 8032 | 127.0.0.1 | via tunnel (POST only) | Layer 2 (new) |
| FERPA Audit          | 8033 | 127.0.0.1 | no      | Layer 2 (new)      |
| Playback Studio      | 8034 | 127.0.0.1 | no (later via tunnel) | Layer 2 |
| Uptime Kuma          | 8090 | 127.0.0.1 | no      | Ops                |

---

## 4. Component designs

### 4.1 Lesson Orchestrator (`:8030`)

The runtime that executes `.lesson` files against Matrix rooms.

**Responsibilities**
- Hold the state machine for an active lesson per `(class_period, day)` tuple
- Dispatch typed slots to Matrix rooms at the right time
- Collect responses, route them to Honcho with evidence-quality tags
- Surface real-time signals to the Teacher Radar channel
- Honor teacher overrides (Pause / Extend / Skip) without breaking the state machine

**Process model**

Single Python service, asyncio-based, persistent state in Postgres (its own DB, not Synapse's). Subscribes to Matrix as the `@bot` account via Hermes' classroom-bot profile — *not* by opening a second Matrix client. The Lesson Orchestrator and Hermes share one device by RPC over a Unix socket. This avoids two devices typing in the same room (which is exactly the kind of thing that produces UTD errors at scale per Gemini's E2EE finding).

```
┌─────────────────────────┐
│ Lesson Orchestrator     │
│  ┌───────────────────┐  │
│  │ State machine     │  │
│  │ (per active run)  │  │     UDS  ┌──────────────┐
│  └────────┬──────────┘  │ ────────►│ Hermes       │──► Matrix
│           ▼             │ commands │ classroom-bot│
│  ┌───────────────────┐  │ ◄────────│ gateway      │◄── events
│  │ Honcho writer     │──┼──────►   └──────────────┘
│  └───────────────────┘  │     HTTP
│  ┌───────────────────┐  │
│  │ Teacher Radar     │──┼──────►   teacher DM room
│  └───────────────────┘  │
└─────────────────────────┘
```

**State machine**

The state machine mirrors the Campus 5-Step Cycle (`VISION.md` §"The Campus Lesson Cycle"). Each state has explicit entry actions, a timer, exit conditions, and override hooks.

```
SCHEDULED → BELL_RINGER → HOOK → DI_BLOCK_1 → THREE_A_TALK_1
   ↘ teacher override
                            → DI_BLOCK_2 → THREE_A_TALK_2
                            → PARTICIPATION_3B
                            → PRACTICE
                            → CLOSURE → ARCHIVED
```

Override transitions available from any state via Teacher Radar commands:
- `PAUSE` — halt timers, keep room state; teacher acknowledgement required to resume
- `EXTEND <minutes>` — push the current state's exit deadline
- `SKIP` — jump to next state
- `REWIND <state>` — return to an earlier state (used when class collectively missed something)
- `END_EARLY` — force CLOSURE then ARCHIVED

**Persistence**

Two tables in the orchestrator's Postgres DB, plus a read-only mirror of the active `.lesson` file's slot definitions:

| Table              | Purpose |
|--------------------|---------|
| `lesson_run`       | One row per `(class_period, day, lesson_id)`; current state, timers, teacher overrides |
| `slot_dispatch`    | One row per Matrix post the orchestrator made; references the source slot in the `.lesson` file by hash |
| `response`         | One row per student response; references `slot_dispatch.id`; evidence_quality enum |
| `intervention`     | One row per Teacher Radar alert and what action the teacher took |

`slot_dispatch.source_slot_hash` is how the curriculum-fidelity eval suite (§4.6) verifies that what got posted matches verbatim TEA content.

**API (internal HTTP, all on loopback)**

| Method  | Path                                | Purpose |
|---------|-------------------------------------|---------|
| POST    | `/runs`                             | Schedule a lesson run from a `.lesson` file path |
| GET     | `/runs/active`                      | List currently running lessons |
| POST    | `/runs/{id}/command`                | Teacher override (PAUSE / SKIP / EXTEND / REWIND / END_EARLY) |
| GET     | `/runs/{id}/state`                  | Inspect current state, timer, last dispatched slot |
| POST    | `/runs/{id}/student/{mxid}/response`| Internal: webhook from Hermes when a student posts |

**Failure modes the design must handle**
- Orchestrator crash mid-lesson → on restart, recover `lesson_run` rows and re-enter the last persisted state; do *not* re-dispatch slots already in `slot_dispatch`
- Synapse outage → drop into "queued" mode, hold dispatches; Teacher Radar must surface this to the teacher within 30s
- Honcho outage → keep dispatching to rooms (instruction continues), buffer responses in a local queue, drain when Honcho returns; never block the lesson on a memory write

### 4.2 The `bluebonnet-runtime` spec

Per Opus' bold idea: a `.lesson` file is the executable curriculum artifact. The Matrix bot is one reference implementation; future runtimes (Chromebook app, Classroom plugin) can target the same spec.

A `.lesson` file is JSON (line-oriented for diff-ability) with typed slots. The schema lives at `bluebonnet-runtime-spec.json` (already present at the project root). The minimal shape this design depends on:

```json
{
  "spec_version": "0.1",
  "lesson_id": "G8_M3_T1_L2",
  "metadata": {
    "title": "Drawing Trend Lines",
    "teks": ["8.5D", "8.5I"],
    "grade": 8,
    "day_of": 1,
    "source_uri": "tea://bluebonnet/G8/M3/T1/L2"
  },
  "slots": [
    { "id": "bell",        "kind": "bell_ringer",   "timer_min": 5,  "content_ref": "...", "verbatim": false },
    { "id": "hook",        "kind": "hook",          "timer_min": 4,  "content_ref": "..." },
    { "id": "di1",         "kind": "di_block",      "timer_min": 8,  "content_ref": "...", "verbatim": true },
    { "id": "talk1",       "kind": "three_a_talk",  "stem": "I think the trend line will ___ because ___.", "min_responses_per_student": 1 },
    { "id": "di2",         "kind": "di_block",      "timer_min": 8,  "content_ref": "...", "verbatim": true },
    { "id": "talk2",       "kind": "three_a_talk",  "stem": "..." },
    { "id": "part",        "kind": "participation", "strategy": "four_corners", "options": ["A","B","C","D"] },
    { "id": "practice",    "kind": "practice",      "mode": "learning_together", "problems": [...] },
    { "id": "closure",     "kind": "closure",       "essential_question": "...", "exit_ticket": {...} }
  ],
  "memory_policy": {
    "evidence_quality": ["mention_only", "stem_completion", "structured_answer", "verified_correct"],
    "per_teks_tracking": true,
    "forgetting_curve": { "enabled": true, "model": "ebbinghaus_v1" }
  },
  "fallback": {
    "printed_pdf": "tea://bluebonnet/G8/M3/T1/L2/print.pdf"
  }
}
```

Key design choices:

- **`verbatim: true`** on a slot is a contract with the curriculum-fidelity eval suite. The orchestrator is forbidden from passing that slot's content through any LLM rewrite path. It posts the exact bytes referenced by `content_ref`. This is the answer to Opus' "fidelity drift" risk.
- **`content_ref`** is a URI, not inline text. Practically that resolves to a path in a content-addressable store (see §4.6). The hash of the resolved content is recorded in `slot_dispatch.source_slot_hash`.
- **`fallback.printed_pdf`** is the SPOF mitigation. Every lesson must have a printable form (Opus' Cloudflare-TOS-complaint risk).

### 4.3 Content Pipeline

Converts the existing Bluebonnet assets — `facilitation-notes.json` (600KB, 51 lessons), TEA PPTX slides, Skills Practice PDFs — into `.lesson` files.

```
~/Bluebonnet/Grade8/facilitation-notes.json ─┐
~/Bluebonnet/Grade8/*.pptx                   ├─► content-pipeline ─► content_store/  (CAS, sha256)
~/Bluebonnet/.../Skills Practice/*.pdf       ┘                       lessons/*.lesson
```

Stages:

1. **Extract** — `facilitation-notes.json` parsed into per-lesson dicts; PPTX slides extracted to text + image assets; Skills Practice PDFs OCR'd if needed and indexed by lesson.
2. **Map** — author mapping from `facilitation_notes.before/during/after` to typed slots. This step is human-in-the-loop. Each lesson takes a teacher ~15–30 minutes the first time, less after templates settle.
3. **Validate** — every slot marked `verbatim: true` is checked against the source bytes. Any drift kills the build.
4. **Emit** — `.lesson` file plus all referenced content blobs written to a content-addressable store keyed by sha256.

The pipeline is a CLI, not a long-running service. Output is committed alongside the codebase. Authoring one lesson is mechanical after the first; per Opus, "the other 50 become mechanical" once the spec is fixed.

### 4.4 Teacher Radar (in-orchestrator)

Private DM channel between the teacher and the bot. It is a *reduction layer* (`VISION.md` principle #7) — never an addition.

**Mechanics**
- One Matrix DM room per teacher, created on first onboarding
- Three message classes, distinguished by Matrix `m.relates_to` annotations so a future client can filter:
  - `signal` — situational awareness ("Team 2 hasn't responded in 4 min")
  - `recommendation` — suggested 90-second move ("Team 2 is treating proportional as additive — ask them to compare ratios")
  - `command_ack` — confirmation of a teacher override
- Outbound alerts are rate-limited per teacher: max 1 every 30 seconds at the bot side, with a `digest_after` rule that batches lower-priority signals into a single "since the last alert: …" message

**Signal sources**
- Silence detection from the orchestrator (`response` table queries against `slot_dispatch.posted_at`)
- Misconception clustering: Honcho's inductive-reasoning lens (`gemini-research-analysis.md` §"Reasoning Pipeline") emits a tag when ≥N students in a team share a misconception. Threshold is per-class, defaulted to 3 of 7
- Evidence-quality regressions: a student previously at `verified_correct` for this TEKS now producing only `mention_only` responses

**Commands the teacher can issue back, in plain text**
```
pause
extend 5
skip
rewind talk1
end early
who hasn't spoken in team 2
how is sofia doing on slopes
```

These are parsed by a constrained grammar (not free-form NLP). If parsing fails, the bot replies with the short command list. This is intentional — under classroom cognitive load, the teacher should never wonder what they can type.

### 4.5 Math Input Handler (`:8032`)

Solves the Math Input Problem (Gemini's biggest practical critique). Students should never have to type fractions, graphs, or geometry into Cinny.

**Primary path: snap-photo via Cinny**

1. Student takes a photo of paper work, uploads as a regular Matrix image to their team room or to `@bot` DM
2. Hermes intercepts uploads with a known caption pattern (`/work`, `/answer`, or the bot @-mentioned with an attachment)
3. Hermes forwards the Matrix `mxc://` URL to `math-input:8032`
4. `math-input` downloads via media repo, runs vision model (Claude Sonnet vision or gpt-4o vision; both already in the OpenCode Go provider pool) with the lesson's problem context as prompt
5. Output is structured: `{ student_attempt: "...", final_answer: "...", confidence: 0.86 }`
6. Result is passed through the Math Verifier (§4.6) — vision is not authoritative on correctness, only on transcription
7. Verified answer + transcription stored in Honcho with `evidence_quality: structured_answer` (if transcribed but not verified) or `verified_correct` (if verifier confirms)

**Secondary paths (later)**
- Voice note → Whisper transcription → text input (ELL accessibility)
- In-room whiteboard drawing (post-prototype; needs custom Matrix message type)

**Privacy**
- Photos are stored only in Synapse's media repo; the math-input service never writes the image elsewhere
- The vision model call is logged to FERPA Audit (§4.7) as "image processed for student work analysis" with hash, not contents
- Retention: photo media is deleted from the media repo at end of grading period unless flagged for parent record

### 4.6 Math Verifier (`:8031`) and Curriculum-Fidelity Eval

Two responsibilities, one service, because they share infrastructure (the lesson-context indexer).

**Math Verifier — ValiMath pattern (Gemini §"Strategic Verdict")**

Every math answer that the bot will *display to a student* — generated reply, feedback on practice, answer key — must pass through the verifier first. This is `VISION.md` principle #15.

```
   LLM math output
        │
        ▼
 ┌──────────────────────────┐
 │ 1. Symbolic check         │ sympy evaluates the expression
 │ 2. Step decomposition     │ LLM (different model) breaks into steps
 │ 3. Per-step verification  │ each step re-checked symbolically
 │ 4. Confidence aggregation │ all 3 must pass; else REJECT
 └──────────────────────────┘
        │
   PASS │ REJECT (route to teacher via Radar, do NOT show to student)
        ▼
   Send to student
```

For middle-school math the symbolic check is sufficient for most problems (arithmetic, linear equations, ratios). For multi-step reasoning the step-decomposition path catches what a single LLM pass would miss.

This is a hard gate. The orchestrator will never bypass it under load. If the verifier is down, the bot silently degrades: it will *not* post answers — it routes the question to the teacher.

**Curriculum-Fidelity Eval**

Runs on:
- Every `.lesson` file build (CI step in the content pipeline)
- A nightly sweep over the last 24h of `slot_dispatch` rows whose source slot was `verbatim: true`

Mechanics: rehash the posted content, compare against `source_slot_hash`. Any drift produces a Sev-2 alert. This catches the case where a future change to the orchestrator accidentally introduces a templating pass on a verbatim slot.

### 4.7 FERPA Audit Log (`:8033`)

Opus' "do not retrofit" item. Vector embeddings in Honcho are educational records under FERPA. When a parent files a records request, the response must be human-readable, complete, and timely. The audit log is the parallel store that makes that request answerable.

**Data model**

Append-only, one row per FERPA-relevant event:

| Column           | Notes |
|------------------|-------|
| `id`             | UUID, monotonic |
| `student_mxid`   | The Matrix ID this event pertains to |
| `occurred_at`    | UTC |
| `event_kind`     | enum: `message_sent`, `message_received`, `response_recorded`, `evidence_quality_change`, `intervention`, `memory_inferred`, `data_exported`, `data_deleted` |
| `lesson_run_id`  | nullable FK to orchestrator |
| `payload_text`   | Human-readable summary of the event (not the embedding) |
| `payload_uri`    | Pointer to the raw artifact in Synapse / Honcho / math-input |
| `actor`          | Which subsystem produced it |

**Write path**

Every other service emits events to `ferpa-audit:8033` over HTTP. Calls are fire-and-forget with local-disk WAL backing — if `ferpa-audit` is down, the originating service still completes its work, but stalls if WAL exceeds 1000 entries. This makes data loss impossible while keeping the live system responsive.

**Honcho-specific hook**

Honcho's reasoning pipeline already runs asynchronously and produces "peer representations" (`gemini-research-analysis.md` §"Reasoning Pipeline"). Every representation update is captured as a `memory_inferred` event with `payload_text` rendered from the inference summary, not the embedding vector. A parent who asks "what did the system conclude about my child?" gets prose, not a `float[1536]`.

**Read path**

A CLI (no UI on day one) produces a per-student records package: chronological, per-event, with raw artifact pointers. Format: a single Markdown file plus an attachments directory. The CLI is the export endpoint for a records request. Retention: events kept for the duration of the student's enrollment + 1 year, then archived to cold storage; full purge on documented parent request.

### 4.8 Lesson Playback Studio (`:8034`)

GPT-5.5's bold idea, named honestly (per Opus' critique): not "the lesson," but "a session replay."

**Inputs**
- `slot_dispatch` + `response` + `intervention` rows for one `lesson_run_id`
- Synapse room timeline for the team rooms involved
- Honcho per-student updates that happened during the run

**Outputs**
- A timeline view (HTML, internal-only): bot posts, student responses, teacher interventions
- A misconception heatmap by TEKS × team × student
- "Critical moment" markers — auto-flagged from clusters of low-evidence-quality responses
- An async replay package for absent students — explicitly labeled "Worksheet + Bot Replay," not "Class Replay" (Opus' "async oversells" warning)
- An auto-drafted small-group plan for the next day (suggestion only — teacher approves)

This service is read-only on Layer 1 data. It runs once per lesson, after CLOSURE, as a Kubernetes-style Job (in our world: a one-shot Docker container). Output is written to a local volume and exposed only to the teacher via the orchestrator's web view (later phase).

### 4.9 Honcho integration (existing, extended)

Honcho is deployed and healthy. This design extends it in three ways without changing the service:

1. **Evidence quality levels** (GPT-5.5 critique). Every message stored is tagged at write-time by the orchestrator with one of four levels. The dialectic reasoning pipeline already in Honcho consumes the tag as a Honcho `metadata` field; we do not need to fork Honcho.
2. **Per-TEKS tracking** (Opus' STAAR early-warning idea). Each Honcho session message gets a `teks: ["8.5D", "8.5I"]` metadata tag from the lesson slot. Honcho's inductive lens then naturally groups by tag without code changes.
3. **Forgetting curve** (Gemini's spaced-repetition extension). A separate process — not Honcho — reads from Honcho weekly per student per TEKS, computes time-since-last-mastery + decay, writes back a `next_review_due` field as Honcho metadata. The Bell Ringer slot for that student then pulls from "TEKS where `next_review_due <= today`."

No fork. No new database. Everything sits on top of Honcho's existing data model.

### 4.10 Attendance Tracking (`:deployed`)

The first working component of Layer 2. Implements daily student check-in via a Hermes gateway hook — no new service, no Docker container.

**Implementation**

| Asset | Path | Purpose |
|-------|------|---------|
| Plugin | `~/.hermes/plugins/classroom-attendance/` | Registers `/here`, `/roll` as known commands |
| Gateway hook | `~/.hermes/hooks/classroom-attendance/` | Intercepts `command:here` / `command:roll` with full sender context |
| Data | `~/.hermes/classroom/attendance/YYYY-MM-DD.json` | Daily JSON — append-only |
| Watchdog | `~/.hermes/scripts/attendance_watch.py` | Detects new check-ins, emits notifications |
| Cron | `every 2m`, `no_agent` | Runs watchdog, delivers to teacher's home channel |

**Data flow**

```
Student types "/here" in Matrix DM
  → Gateway hook fires with user_id, platform, timestamp
  → Matches known students by MXID, records check-in
  → Returns "✅ Checked in, Sofia!" — no LLM involved
  → Watchdog detects new entry on next tick
  → Teacher receives "📋 Sofia checked in at 08:02" via home channel
```

**Why a gateway hook instead of a service**

The `register_command()` handler signature (`fn(raw_args) -> str`) does not expose sender identity, which attendance tracking requires. The `command:<canonical>` gateway hook receives the full event context (`user_id`, `platform`, `command`, `args`) and can return `{"decision": "handled", "message": "..."}` to bypass both the LLM and the handler. This is the intended Hermes-native mechanism for commands that need sender context; `register_command()` is the registration path, and the hook is the execution path.

**Migration path**

When the Lesson Orchestrator (§4.1) is live, attendance becomes a slot-level concern in the `.lesson` file (a `bell_ringer` slot with an `attendance_required: true` flag). The standalone attendance hook is then retired. Until then, this provides production roll call data without blocking on the full content pipeline.

---

## 5. Data architecture

### 5.1 Where data lives

| Data class                       | Primary store           | Retention             | FERPA-record? |
|----------------------------------|-------------------------|-----------------------|---------------|
| Matrix messages (encrypted)      | Synapse Postgres        | 1 school year + 90d   | yes           |
| Matrix media (photos, voice)     | Synapse media repo      | grading period        | yes           |
| Student-bot conversation memory  | Honcho pgvector         | 1 school year + 90d   | yes           |
| Per-TEKS evidence + forgetting   | Honcho metadata         | 1 school year + 90d   | yes           |
| Orchestrator state               | Orchestrator Postgres   | 1 school year + 90d   | partial       |
| FERPA audit events               | FERPA audit DB          | enrollment + 1y       | yes (mirror)  |
| Lesson content (`.lesson` files) | Git repo + CAS          | indefinite (curriculum) | no          |
| Playback Studio artifacts        | Local volume            | 1 school year         | yes           |
| Logs (operational)               | journald / Loki         | 30 days               | scrubbed      |

### 5.2 The FERPA mirror invariant

For every row in any "yes" or "partial" row above, there is at least one row in `ferpa_audit` describing it in human-readable form. This is enforced by:
- Every service that writes to a yes/partial store must also POST to `ferpa-audit:8033` *before acknowledging the write*
- A nightly reconciliation job that scans for orphans in either direction

This is the only way to make a parent records request answerable in days rather than weeks.

### 5.3 Deletion

Two flows, both well-defined:

- **End-of-year purge**: scripted, deletes Matrix room history, Honcho workspace, orchestrator runs, audit events older than retention. Dry-run mode that produces a deletion manifest, then a `--commit` mode.
- **Parent request**: per-student delete that walks the audit log first, generates a deletion plan, and executes against every store that mentions the student. The audit log itself records the deletion event (kind: `data_deleted`) before the row is removed — so the system always knows that a delete happened even after the data is gone.

---

## 6. Security & privacy

### 6.1 E2EE topology

The classroom bot runs E2EE per ADR-002 (`plan.md`). Two changes this design imposes on top of that:

1. **Single device per logical actor.** The Lesson Orchestrator does *not* mint its own Matrix device. It commands the existing `bot3` device via Hermes' RPC. This collapses what would otherwise be 2–3 bot devices in every team room (orchestrator, hermes, draupnir) into 2 (hermes-as-orchestrator + draupnir). Fewer devices = far fewer Megolm session keys to coordinate = far fewer UTD errors (Gemini's E2EE-at-scale finding).

2. **Cross-signing key custody.** `MATRIX_RECOVERY_KEY` is stored in `~/.hermes/profiles/classroom-bot/.env` today. This design requires it to also be backed up to encrypted offline storage (a 1Password vault entry, GPG-encrypted file on USB, etc.) labeled with the recovery procedure. If the host dies, recovery means re-keying every device, not losing message history.

### 6.2 Secrets

| Secret                    | Where it lives now | Where this design wants it |
|---------------------------|--------------------|----------------------------|
| Synapse macaroon          | `homeserver.yaml`  | unchanged                  |
| Postgres passwords        | `.env`             | unchanged                  |
| Matrix recovery key       | profile `.env`     | + offline backup           |
| Google OIDC client secret | `google-oauth-client.json` | unchanged          |
| LLM provider keys (OpenCode Go) | profile `.env` | unchanged                |
| Cohere embedding key      | Honcho `.env`      | unchanged                  |
| Cloudflare tunnel token   | system service     | unchanged                  |

No new secret stores. The existing `.env` discipline is sufficient at this scale.

### 6.3 Threat model deltas vs. the current snapshot

| Threat                           | Mitigation in this design |
|----------------------------------|---------------------------|
| Student exfiltrates classmate data via DM | room_blocker already prevents student↔student DMs; bot↔student DMs are audit-logged |
| Bot says something wrong about math      | Math Verifier hard gate before any math output is displayed |
| Bot paraphrases TEA content              | `verbatim: true` slot contract + nightly fidelity sweep |
| Parent FERPA request for embeddings      | FERPA audit log produces human-readable export |
| Cloudflare cuts the tunnel mid-class     | `.lesson.fallback.printed_pdf` + documented offline procedure |
| Orchestrator state corrupted             | All state idempotent + recoverable from `slot_dispatch` |
| Honcho leaks across workspaces           | Workspace-per-class isolation per ADR-003; explicit deny in code path |

---

## 7. Reliability & SPOF mitigation

This is Opus' "Cloudflare TOS complaint takes class dark mid-period" concern, addressed concretely.

### 7.1 Tiered availability targets

| Tier | Component                       | Target | If it's down... |
|------|---------------------------------|--------|-----------------|
| T0   | Synapse + Postgres              | 99.5%  | Class falls back to printed PDF |
| T0   | Hermes classroom-bot gateway    | 99.5%  | Class falls back to printed PDF |
| T1   | Lesson Orchestrator             | 99.0%  | Bot becomes "chat only"; lesson continues from printed PDF |
| T1   | Math Verifier                   | 99.0%  | Bot will not post any math; teacher answers |
| T2   | Math Input                      | 95.0%  | Students show paper work to teacher physically |
| T2   | Teacher Radar                   | 99.0%  | Teacher uses normal classroom judgment |
| T3   | Playback Studio                 | 90.0%  | Replay is delayed; no impact on live class |
| T3   | FERPA Audit                     | 99.9%  | Writers stall after 1000-entry WAL — rare; high target is non-negotiable for compliance |

### 7.2 Backup & restore

- Postgres (Synapse + Honcho + Orchestrator + FERPA audit): `pg_dump` nightly to host disk + offsite (rclone to a B2 or S3 bucket). 30-day retention. Tested restore quarterly.
- Synapse media: `rsync` snapshot weekly + same offsite path.
- Lesson content: in Git; offsite by virtue of being pushed to a remote.

### 7.3 Failover-to-printed-PDF

Every `.lesson` file has `fallback.printed_pdf`. A weekly cron pre-renders the next 5 school days of PDFs and stores them on the teacher's machine *outside* the host. When the digital path is unavailable:
1. Teacher opens the printed (or locally cached) PDF
2. Class proceeds without bot facilitation
3. Honcho data resumes on next live class — no attempt to backfill the missed day

### 7.4 Monitoring

Uptime Kuma on `:8090` watches every service endpoint above. Alert routing:
- T0/T1 down → SMS to Abraham
- T2/T3 down → email + Hermes-main DM
- FERPA Audit WAL > 500 entries → SMS to Abraham (this is rare and important)

---

## 8. Deployment

### 8.1 Topology

Single host today. This design does not require sharding or multi-host until at least 5 simultaneous classrooms (>100 students). The architecture is, however, written to allow horizontal split later: every new service is stateless except for its own database, and inter-service traffic is HTTP.

### 8.2 Compose layout

The existing `deploy/docker-compose.yml` grows by ~6 services. Suggested split into two compose files to keep blast radius small:

- `deploy/docker-compose.yml` — Layer 1 (existing): synapse, postgres, ketesa, cinny
- `deploy/docker-compose.runtime.yml` — Layer 2 (new): orchestrator, math-verifier, math-input, ferpa-audit, playback-studio, uptime-kuma
- Honcho stays in its own compose, as it is today

Each service runs unprivileged, binds to 127.0.0.1, and is started by a single `make up` from the project root.

### 8.3 Host requirements

Today's host comfortably runs Layer 1 + Honcho. The Layer 2 services add roughly:

| Service              | Idle RAM | Active RAM | CPU peak |
|----------------------|----------|------------|----------|
| Orchestrator         | 120 MB   | 300 MB     | low      |
| Math Verifier        | 200 MB   | 600 MB     | sympy bursts |
| Math Input           | 150 MB   | 500 MB     | vision call latency-bound |
| FERPA Audit          | 80 MB    | 150 MB     | very low |
| Playback Studio (run)| —        | 800 MB     | one-shot |
| Uptime Kuma          | 60 MB    | 80 MB      | very low |

Total active overhead: roughly 1.7 GB RAM and ~1 CPU core. Within current capacity.

### 8.4 Migration order

This is the order in which new services come up, each shippable on its own:

1. FERPA Audit — first, because once anything else is built, it should already be writing
2. Content Pipeline + one `.lesson` file (one Grade 8 lesson, end-to-end)
3. Lesson Orchestrator — wired to that one lesson, running in shadow mode (logs only, no Matrix posts)
4. Orchestrator → Hermes RPC enabled — bot actually posts to one team room
5. Math Verifier — gates any math output from the orchestrator
6. Teacher Radar DM channel
7. Math Input photo path
8. Draupnir moderation bot (independently, per `plan.md` Phase 3)
9. Playback Studio
10. The `.lesson` author tools and a backlog of 50 more lessons

Steps 1–6 are the path to "one full lesson end-to-end" — Opus' Tier-1 milestone.

---

## 9. Observability

- **Logs**: every service emits structured JSON to stdout. Captured by journald, optionally shipped to a local Loki later. Logs that quote student content are tagged `ferpa: true` and routed to a 30-day-retained partition; everything else goes to standard retention.
- **Metrics**: Prometheus scrape endpoints on each service (`/metrics`). Grafana is a Phase-2 addition.
- **Traces**: not deployed initially. Single-host, per-request latency is low enough that traces add cost without clear payoff. Add OpenTelemetry instrumentation only if a specific perf bug requires it.
- **Audit**: FERPA Audit Log (§4.7) is the system-of-record for anything student-relevant.

---

## 10. What this design deliberately does *not* include

To be explicit, since the source documents brainstormed broader scope:

1. **The Crew as live bot personas.** Per VISION principle #12 and Opus' deception-design risk, not deployed until TEA/legal clearance. The orchestrator does not have an integration point for this — adding it later is a one-time spec extension (a new `kind: "crew_voice"` slot type).
2. **Multi-tenant deployments.** Single classroom, single host. Multi-classroom is an explicit Phase 4+ concern that will require changes to the Honcho workspace model and to the room_blocker module's allowed-user list.
3. **Federated Matrix.** Federation is off and stays off (`plan.md` Phase 1 OUT OF SCOPE).
4. **Mobile apps.** Cinny web is the only student client. No mobile app development inside this design.
5. **Grading systems integration.** PowerSchool / Skyward integration is explicitly deferred. Honcho is the only longitudinal store.

---

## 11. Phased build, mapped to the vision

| Phase (this design) | Output                                                     | Maps to VISION §"Next Steps" |
|---------------------|------------------------------------------------------------|------------------------------|
| 0  | FERPA Audit Log live, writing nothing yet                       | Immediate — Phase 3 prereq   |
| 1  | One `.lesson` file authored end-to-end via content pipeline     | Short-term #2, #8            |
| 2  | Orchestrator dispatches that lesson against one team room       | Short-term #1, #3, #4, #5    |
| 3  | Teacher Radar DM channel + override commands                    | Short-term #6                |
| 4  | Math Verifier gating all math output                            | Long-term math verification, principle #15 |
| 5  | Math Input photo path                                            | Short-term #7                |
| 6  | Draupnir + moderation alert channel                             | Plan.md Phase 3              |
| 7  | Playback Studio first artifact                                  | Long-term #1                 |
| 8  | Forgetting-curve job + Bell Ringer spiral review                | Medium-term #9               |
| 9  | Per-TEKS STAAR projection cut from existing Honcho data         | Long-term #5                 |
| 10 | The Crew (conditional on §10.1 clearance)                       | VISION future                |

Phases 0–5 are the minimum to satisfy Opus' Tier-1 transformation criteria: one full lesson end-to-end, end-to-end FERPA-defensible, math-verified, with the teacher amplified rather than replaced.

---

## 12. Open questions this design surfaces (for the next round)

1. **Hermes RPC surface.** §4.1 assumes Hermes exposes a stable RPC for "post message to room X as the classroom-bot device." That interface needs to be specified in Hermes itself before the orchestrator can be built against it.
2. **`.lesson` schema versioning.** `spec_version: "0.1"` is a placeholder. We need a written migration policy before the second lesson ships.
3. **Vision model choice for Math Input.** Both Claude Sonnet vision and gpt-4o vision work; one needs to be picked for cost/latency. Test on 20 paper-work samples first.
4. **Forgetting-curve cold start.** A student in week 1 has no decay data. Default policy: skip spiral review until at least one prior demonstration of mastery exists for that TEKS.
5. **Playback Studio access.** Teacher-only is obvious. Should the principal also have access? That's a policy question with FERPA implications and belongs in `compliance.md`, not here.

---

## Appendix A. Mapping to VISION principles

This design's compliance with the 16 principles in `VISION.md` §"Key Principles":

| # | Principle                                          | Where addressed                       |
|---|----------------------------------------------------|---------------------------------------|
| 1 | Verbatim content only                              | §4.2 `verbatim` slot contract + §4.6 eval |
| 2 | The Crew stays                                     | §10.1 — deferred but spec-accommodated |
| 3 | One concept per slide / bot message                | §4.2 slot kinds enforce this          |
| 4 | Scope guardrails                                   | §0, §10                                |
| 5 | Theme rules (Algebra/Grade 8 colors)              | Out of scope (Cinny rendering)        |
| 6 | Math needs a non-typing path                       | §4.5 Math Input                       |
| 7 | Teacher Radar is reduction, not addition           | §4.4 rate limits + digest rule        |
| 8 | Evidence quality, not activity logs                | §4.9 evidence quality levels          |
| 9 | Bot models uncertainty                             | §4.6 — verifier failure routes to teacher |
| 10 | Curriculum as code                                | §1 architectural north star           |
| 11 | Teacher amplifier, not replacer                   | §4.4 + §11 milestones                 |
| 12 | No deceptive persona without legal review         | §10.1                                  |
| 13 | Human-auditable FERPA log from day one            | §4.7 + §8.4 ordering (step 1)         |
| 14 | Prevent Cognitive Debt                            | Lesson-author concern, surfaced via `min_responses_per_student` slot field |
| 15 | Verify math before students see it                | §4.6 Math Verifier                    |
| 16 | Document everything                               | This document, plus existing project docs |

---

## Appendix B. Glossary

- **`.lesson` file** — JSON artifact conforming to the `bluebonnet-runtime` spec; the executable form of one lesson day
- **Slot** — a typed unit inside a `.lesson` file; what the runtime dispatches
- **Lesson run** — one execution of a `.lesson` file against one classroom on one day
- **Evidence quality** — one of `mention_only | stem_completion | structured_answer | verified_correct`; tagged on every recorded student response
- **Verbatim slot** — a slot whose content must be posted byte-identical to TEA source; enforced by the fidelity eval
- **Teacher Radar** — the private DM channel between the teacher and the bot
- **CAS** — content-addressable store, the sha256-keyed blob store backing `content_ref`
