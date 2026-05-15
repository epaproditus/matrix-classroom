# Matrix Classroom — Vision Document

> **Last updated:** 2026-05-14
> **Author:** Brittany (Hermes AI) + Claude Sonnet (Anthropic) + Claude Opus (Anthropic) + Gemini 3.1 Pro (Google) + GPT-5.5 (Cursor/OpenAI)
> **Purpose:** Self-contained vision reference for any context-free agent joining this project

---

## 🎯 The Core Vision

The Matrix Classroom is **not** a chat platform for students.
It is a **new way of instruction delivery** that uses the Matrix protocol as the delivery medium, the Bluebonnet Learning (TEA OER) pedagogical model as the instructional methodology, and an AI bot as the facilitator that runs the campus lesson cycle.

**One-sentence vision:**
> "A self-running, data-aware, TEKS-aligned instructional delivery platform that digitizes the Bluebonnet pedagogical model through Matrix chat rooms — where an AI bot facilitates the complete campus lesson cycle and tracks per-student understanding."

---

## 🏗️ Current Infrastructure

### Stack
| Layer | Technology | Port | Status |
|-------|-----------|------|--------|
| Homeserver | Synapse | 8010 | ✅ Live |
| Database | PostgreSQL | — | ✅ Live |
| Student Client | Cinny | 8012 | ✅ Live |
| AI Bot | Hermes (classroom-bot profile) | — | ✅ Live |
| Moderation | Draupnir (planned) | — | ⏳ Not started |
| Reverse Proxy | Cloudflare Tunnel | — | ✅ Live |
| Auth | Google SSO (OIDC) | — | ✅ Configured |
| Memory Layer | Honcho (pgvector + Redis) | 8020 | ✅ Healthy |
| Room Blocker | Custom Synapse module | — | ✅ Deployed |

### Two-Profile Hermes Architecture
- **Main Profile** (`~/.hermes/`): Discord, CLI, email, personal assistant
- **Classroom Profile** (`~/.hermes/profiles/classroom-bot/`): Matrix-only, E2EE, isolated memory
- Both run simultaneously, zero memory pollution between them

### Users
- 10 accounts: admin, @bot (AI), @aromero (teacher), 8 students
- Students are `user_type: support` — cannot create rooms
- Teacher account also `support` type — simulates student restrictions
- SSO via Google Workspace OIDC

### Security Model
- Room blocker prevents non-admin room creation
- Students cannot DM each other (only @bot)
- E2EE enabled for classroom-bot profile
- Room directory disabled by default
- All 8 students deactivated until Phase 3 (Draupnir) is ready

### Phases
| Phase | Name | Status |
|-------|------|--------|
| 0 | Research | ✅ Complete |
| 0.5 | COPPA/FERPA Compliance | ⏳ In progress |
| 1 | Infrastructure | ✅ Complete (tech debt pending) |
| 2 | Classroom Setup | ✅ Pilot done (tech debt pending) |
| 3 | Draupnir Moderation | 🔜 **Next** |
| 4 | Hermes Bot Features | ✅ Done (warm-up cron pending) |
| 4.5 | Attendance Check-in | ✅ Done — `!here`/`!roll`, watchdog |
| 5 | Teacher Dashboard | 🔮 Future |
| 6 | Badges/Gamification | 🔮 Future |

---

## 📚 The Bluebonnet Learning Model

Bluebonnet Learning ("Secondary Mathematics, Grade 7/8" and "Algebra I", Edition 1) is a Texas Education Agency (TEA) Open Education Resource (OER) math curriculum.

### Design Philosophy
- **Three Phases instruction:** Before (activate/prep), During (activity/discourse), After (reflect/assess)
- **Productive struggle** — students persist through challenging problems
- **Mathematical coherence** — concepts build logically across modules/ grades
- **Problem-Solving Model Graphic Organizer:** Notice patterns → Organize/Represent → Analyze/Predict → Share results

### Lesson Structure
- **Learning Together days** — collaborative, peer discussion in class
- **Learning Individually days** — Skills Practice, independent work
- **The "Crew"** — fictional peer characters (Sofia, Marcus, Jayden, etc.) who model productive struggle and mathematical thinking in the student edition
- **Academic Glossary** — built-in math vocabulary for ELL students
- **ELPS alignment** — English Language Proficiency Standards embedded

### Resource Inventory (all at ~/Bluebonnet/)
- **Grade 7:** 43 files (modules 1-5)
- **Grade 8:** 42 files (modules 1-5) + 50 TEA lesson PPTX slides
- **Algebra I:** 47 lesson PPTX + 50 support PDFs
- **Facilitation Notes:** Extracted JSON for all lessons with "Before/During/After" scripts, discourse questions, common misconceptions
- **Protocols:** Teacher/Coach internalization guides, observation tools, student work analysis rubrics
- **Skills Practice:** Extra problem sets per topic for independent practice

### Key Documents
| File | Path | Purpose |
|------|------|---------|
| Scope & Sequence | `~/Bluebonnet/Grade8/Eighth Grade Math Scope and Sequence 150-day.pdf` | Day-by-day pacing, primary planning doc |
| TEKS Summary | `~/Bluebonnet/Grade8/Eighth Grade Math TEKS Summary.pdf` | Lesson → TEKS crosswalk |
| Facilitation Notes | `~/Bluebonnet/Grade8/facilitation-notes.json` | 51 lessons (600KB): scripts, questions, misconceptions |
| Golden Checklist | `~/Bluebonnet/GOLDEN-CHECKLIST.md` | District compliance rubric for slide decks |
| Campus Lesson Cycle | `~/Bluebonnet/CAMPUS-LESSON-CYCLE.md` | 5-step cycle guide + Bluebonnet mapping |

---

## 🏫 The Campus Lesson Cycle (How Instruction Is *Delivered*)

Every lesson day follows this 5-step cycle:

| # | Step | Timing | What Happens |
|---|------|--------|-------------|
| 1 | **Bell Ringer** | 5 min | Spiral review (NOT in TEA slides — sourced from Skills Practice) |
| 2 | **Hook** | 2-5 min | Dramatic question, video, real-world provocation to engage |
| 3 | **DI + 3A Talk** | 15-20 min | Direct Instruction with student discourse every ~8 min. Teacher presents content, then stops for structured talk with sentence stems |
| 3B | **Participation** | 5-10 min | Lead4Ward strategy (≥1x/week): Four Corners, Card Sort, Gallery Walk |
| 4 | **Practice** | 15-20 min | Collaborative (Learning Together) or Independent (Learning Individually) |
| 5 | **Closure** | — | Essential Question revisited + Exit Ticket |

### 12-Slide Daily Format
Each lesson day = 12 slides on blank layout, 13.33" × 7.50" widescreen. Numbered cycle step circles in top-right corner. Verbatim TEA content only (no paraphrasing). Speaker notes embedded from facilitation notes.

### 3A Talk (Critical Component)
The "Ask Yourself" prompts from TEA slides + teacher-written sentence stems. Students turn-and-talk with a structured stem like:
> *"I think the trend line will ______ because ______."*

---

## 🌉 The Bridge: Matrix Classroom × Bluebonnet

### Current State
Students join team rooms, bot facilitates discussion, answers questions. Fine, but it's "Discord but self-hosted."

### The Reframed Vision
The bot doesn't just *chat* — it **runs the complete Bluebonnet lesson cycle** through Matrix rooms:

#### Instructional Flow
```
Before Class         ──→ Bot posts Bell Ringer in team rooms
Hook                 ──→ Bot posts dramatic question + media
DI Block 1           ──→ Bot posts activity steps + screen-grabs from TEA slides
3A Talk (Embedded)   ──→ Bot posts "Ask Yourself" prompt + sentence stem
                         → Students reply in-room discourse
                         → Bot posts peer responses to spark discussion
DI Block 2           ──→ Bot posts next activity
3B Participation     ──→ Bot runs poll / Four Corners / Card Sort via Matrix reactions
Practice             ──→ Bot assigns problems, students submit in-room
Closure              ──→ Bot posts Essential Question + Exit Ticket (DM or poll)
After Class          ──→ Honcho per-student memory tracks:
                         • Who participated? Who didn't?
                         • Common misconceptions from responses
                         • Which students need reteach/follow-up
```

#### Feature Mapping

| Bluebonnet Element | Matrix Translation | Value |
|---|---|---|
| **Crew characters** | Bot plays the Crew — models productive struggle in-room | Students see thinking modeled |
| **3A Discourse** | Structured talk prompts at timed intervals | Every student *must* respond in writing |
| **Learning Together** | Team rooms as collaborative space | Peer discussion *visible to teacher* |
| **Learning Individually** | DM bot for tutoring + Skills Practice | Personalized pacing |
| **Facilitation Notes** | Speaker notes baked into bot's behavior | Teacher fidelity without the teacher present |
| **Problem-Solving Model** | Bot scaffold: "Notice → Organize → Analyze → Share" | Metacognitive structure |
| **Exit Ticket** | Bot DM at end of class → Honcho records | Formative assessment data |
| **Differentiation** | Honcho profiles → bot adjusts prompts per student | Actual adaptive instruction |
| **TEKS alignment** | Bot knows which TEKS each lesson maps to | Standards tracking |
| **Common misconceptions** | Bot catches errors and asks probing questions | Real-time intervention |

---

## 🧠 Brainstorming Session (2026-05-14)

### Key Insights from Abraham
- The vision is **bigger than a chat app** — it's a new instructional delivery medium
- The Bluebonnet pedagogy (Three Phases, Learning Together/Individually, Crew, Problem-Solving Model) is the instructional methodology
- The campus 5-step cycle is the delivery format
- The bot is the facilitator that runs the cycle

### Key Insights from Claude (Anthropic)
1. **"Structured pedagogy as protocol"** — encoding the instructional model into automated orchestration is the real innovation
2. **Risks:** Pacing rigidity, math notation barriers, engagement theater (fake participation), ops burden, content pipeline
3. **Blind spot:** The **async classroom** — absent students could replay the entire lesson cycle 1:1 with the bot. Also unlocks flipped classroom + cross-period analytics
4. **Verdict:** "Legitimately transformative — if scoped correctly." High-potential prototype territory
5. **💥 Boldest idea:** "The Crew comes alive" — make the Bluebonnet Crew characters actual Matrix bot accounts that post in rooms, make mistakes, model sentence stems, and "remember" prior lessons through Honcho

### Key Insights from Gemini 3.1 Pro (Google)
1. **"State-Machine Pedagogy"** — the bot as an active orchestrator enforcing pacing, structure, and curriculum fidelity, transforming AI from a "homework helper" into a digital lesson plan that executes itself
2. **Risks:**
   - **Math Input Problem** — typing fractions/graphing/geometry in a linear chat is cognitively taxing for middle schoolers
   - **Pacing Collisions** — fire drills, stuck concepts, the bot blindly pushing phases while the room is confused
   - **Chat Clutter** — 21 students + bot + Crew bots = cognitive overload, instructional steps buried in scrollback
3. **Blind spot: Dynamic Real-Time Breakout Grouping** — Honcho tracks per-student understanding during "Before" and "During" phases, so the bot can dynamically create Matrix sub-rooms for Practice: reteach groups vs extension groups, auto-grouped by Bell Ringer performance
4. **Verdict:** "Highly Ambitious Prototype." Infrastructure is rock-solid, but forcing visual/spatial math into a linear chat client is the major bottleneck
5. **💥 Boldest idea: "Teacher Radar" (Real-Time Copilot)** — Create a private DM channel between the teacher and the bot. While the bot runs the lesson in student rooms, it DMs the teacher real-time alerts:
   - *"Team 2 is completely stuck on the Hook — go walk over there."*
   - *"Marcus just nailed the concept but used the wrong vocabulary — call on him and ask him to use 'coefficient'."*
   - *"Sofia hasn't typed anything in 12 minutes."*
   > Instead of replacing the teacher's presence, the bot processes the noise of 21 typing students and gives the teacher superhuman situational awareness.
6. **To level up:** Solve the Input Problem (snap-photo of handwritten work + vision model grading) + Teacher God-Mode (Pause/Extend/Skip Step override in real-time)

### Key Insights from GPT-5.5 (Cursor/OpenAI)
1. **"Every lesson has an operating system"** — the Matrix room becomes the runtime environment for instruction. Bluebonnet is the curriculum source. Honcho is the longitudinal student model. The bot is the orchestrator. The AI is not replacing the teacher's judgment — it's automating the repetitive, timing-sensitive, easy-to-forget parts of lesson delivery
2. **Risks:**
   - **Classroom chaos** — middle schoolers will meme, spam, test the bot, ignore stems, derail polls, turn Crew accounts into punchlines. Needs classroom management primitives, not just good prompts
   - **Cognitive overload for teacher** — monitoring Matrix + slides + timers + behavior + misconceptions + tech issues simultaneously could become more burden than help
   - **False confidence from memory tracking** — a student can write a sentence stem without understanding the math. Honcho needs evidence quality levels, not just activity logs
   - **Curriculum fidelity vs adaptation** — verbatim TEA content is safe for compliance, but excellent teaching requires compression/extension/rephrasing. Preserve source fidelity while giving controlled adaptation tools
   - **Privacy ops** — hardest part isn't the tech (COPPA/FERPA, E2EE, room restrictions) — it's the operational side: exports, logs, bot memories, moderation review, parent requests, data deletion, who can inspect what
   - **Equity of access** — chat-first participation misreads quiet or language-developing students. Voice, drawings, paper artifacts, teacher observations need a path into the model
   - **Bot authority** — students may treat the bot as the final answer source. It needs to model uncertainty, defer to the teacher, ask students to reason instead of answering
3. **Blind spot: Live Misconception Routing** — not just "track who needs reteach after class," but *during* the lesson: the bot watches responses during 3A Talk and Practice, clusters misconceptions in real-time, and quietly tells the teacher: *"Team 2 is treating proportional relationships as additive. Ask them to compare ratios before moving on."* This is a 90-second teacher move, not a full intervention
4. **Verdict:** "Promising Instructional Infrastructure Prototype" — above "cool side project," below "transformative tool." Becomes transformative when three things are true: (1) it improves live teacher decision-making, (2) it reduces workload instead of adding orchestration burden, (3) it produces reusable lesson packages (a complete Bluebonnet lesson = portable executable artifact)
5. **💥 Boldest idea: "Lesson Playback Studio"** — every class session becomes a replayable instructional artifact: timeline of bot posts/teacher interventions/student discourse, heatmap of misconceptions by TEKS/student/team, "critical moment" markers, absent-student replay generated from the *actual* class, teacher reflection prompts, auto-generated small group plans. Over time, this becomes a local teaching intelligence layer that learns which hooks work, which prompts produce productive discourse, and how this specific class learns math

### Key Insights from Claude Opus (Anthropic)

> *Note: Opus specifically disagreed with Claude Sonnet in several places. This is the most critical, highest-rigor take in the entire brainstorm.*

1. **"Curriculum as Code" — the real thesis.** Not "The Crew comes alive." That's a demo, not a thesis. The durable insight: Bluebonnet exists as PDFs, slide decks, and facilitation notes. Abraham is accidentally building the **first executable version of a state curriculum** — where a lesson isn't a document, it's a runnable program with timers, branching, peer-discourse hooks, and per-student memory. The three ingredients are: content (free OER), control flow (5-Step cycle), and memory (Honcho). Everything else (Matrix, the bot, the Crew, async replay) is implementation detail. **"Curriculum as code"** is the framing to hold onto.

2. **Risks nobody else flagged:**
   - **Curriculum fidelity drift (silent killer).** Bluebonnet specifies verbatim TEA content, never summarized. First time a kid says "I don't get it" and the bot helpfully paraphrases a worked example, you've broken curriculum fidelity. Need an eval suite that catches violations.
   - **Discourse loop may be self-defeating.** 3A Talk works because of social pressure in a physical room. Replacing peer turn-taking with "type in Matrix" risks replacing the interaction the protocol is trying to produce. If the bot seeds fake peer responses, kids will sniff it out within two weeks.
   - **The Crew is dangerous, not clever.** Bot accounts that "make mistakes" to model productive struggle is ethically fraught. (1) When students figure out Sofia is a bot, *every* bot output loses authority — including correct answers. (2) Parents will read "the AI lied to my kid." COPPA cleared a chat platform; it didn't clear deceptive persona design.
   - **What does Abraham actually do?** If the bot runs everything, Abraham is a classroom monitor — worse pedagogy than what he's replacing. Reframe as **teacher amplifier**: bot handles logistics and memory, teacher owns the moments that require a human.
   - **Honcho is a FERPA landmine.** Vector embeddings of a student's struggles are an educational record. When a parent invokes FERPA, you must produce everything in human-readable form. Need a parallel auditable log from day one.
   - **Single point of failure.** class.mr-romero.com is one Cloudflare TOS complaint from going dark mid-period. Need documented failover-to-printed-PDF plan.
   - **Async replay oversells.** A bot-only replay is a worksheet with a chatbot. The lesson's value came from peer discourse and group productive struggle. Name it honestly.
   - **Engagement decay.** Week 1: bot is cool. Week 8: another assignment. 3B strategies work because they're physical/kinesthetic. A Matrix poll is neither.
   - **OER licensing limits.** Crew characters and trademarked materials may not be relicensable for derivative bot personas. Talk to TEA before scaling.

3. **Blind spot: Per-TEKS STAAR early-warning system.** Honcho tracks per-TEKS mastery across 51 lessons. By February you have a per-student STAAR projection more accurate than Renaissance/NWEA ($15-40/student/year). That's a **budget line item districts will fight for** — the artifact that converts "interesting tech" into "principal goes to bat at the budget meeting."

   Runner-up capabilities:
   - **Live misconception heatmap** — bot sees every 3A Talk response and tells Abraham: "8 of 21 have this slope misconception — reteach now or queue for Bell Ringer?"
   - **Silent differentiation for IEP/504/ELL** — Honcho knows who struggles with reading load. Bot serves simplified syntax or Spanish glossary *quietly via DM*, without singling the kid out.

4. **Verdict:** "Ambitious side project with unusually serious infrastructure." Top 5% of "teacher built something." Not yet transformative. Needs evidence.

   Four things to move tiers, **in order**:
   1. One full lesson end-to-end, for real — whole 5-Step cycle, real classroom, one team, one day
   2. Equivalence, not superiority — learning outcomes at least as good as teacher-led
   3. A second teacher running it without Abraham in the room
   4. Honcho data that changes Abraham's next-day plan

   Hit all four = "legitimately transformative for Texas middle school math" (~400K 7th graders). Hit two = strong portfolio piece.

5. **💥 Boldest idea: Publish a bluebonnet-runtime spec.** Define an open spec for what an executable Bluebonnet lesson is — a state machine for the 5-Step cycle, with typed slots for TEA-verbatim content, Lead4Ward 3B strategies, 3A Talk stems, exit tickets with TEKS tags, and a memory protocol. Publish under a permissive license. Author 51 lessons as `.lesson` files.

   Then:
   - Your Matrix bot is one **reference implementation**. Others can build different runtimes (Chromebook app, Google Classroom plugin, etc.).
   - TEA can adopt the spec. They have no executable distribution today — they have PDFs. You're offering the format they didn't know they needed.
   - The Crew, async replay, Honcho all become *runtime features*, not the product.
   - Portable to other state OERs (Oklahoma, Louisiana).

   This stops being "Abraham's classroom bot" and becomes **infrastructure that survives Abraham being hit by a bus.** You're not "automating teachers" — you're "shipping the curriculum in a runnable form, which teachers run."

   **Concrete next step:** Write the spec for *one* lesson — Step 1 through Step 5 — as a JSON document that someone else could implement against. The other 50 become mechanical.

   > **Bottom line:** The most exciting thing here isn't the AI, the Crew, or the memory. It's that Abraham is in a position to define what an executable state curriculum is, and Bluebonnet's free-OER status means he can do it without asking permission. Don't undersell that by calling it a chat platform.

### 🔮 Synthesis: The Unifying Thread

All four AIs converge on the same insight:

> **The AI's highest value is teacher-facing, not student-facing.**

The bot isn't a tutor. It's a **situational awareness system** that tells the teacher what's happening in the room, in real-time, so the teacher can make better decisions.

| Theme | Claude Sonnet | Gemini | GPT-5.5 | Claude Opus |
|-------|--------|--------|---------|--------|
| **Pedagogy insight** | "Structured pedagogy as protocol" | "State-machine pedagogy" | "Every lesson has an operating system" | **"Curriculum as code" — lesson is a runnable program** |
| **Core thesis** | Bot orchestrates pedagogy | Bot enforces curriculum fidelity | Bot automates repetitive delivery | **You're building the first executable state curriculum** |
| **Math input** | ❌ Missed | ✅ Snap-photo + vision grading | ✅ Equity concern | ❌ Missed |
| **Classroom chaos** | ❌ Missed | ✅ Chat clutter risk | ✅ Meme/spam realism | ✅ Discourse self-defeating, Crew dangerous |
| **Breakout groups** | ❌ Missed | ✅ Dynamic Honcho→sub-rooms | ✅ Live misconception routing | ✅ Per-TEKS STAAR early warning system |
| **Teacher copilot** | ❌ Missed | ✅ Teacher Radar DM channel | ✅ Live misconception routing | ✅ Teacher amplifier (not monitor) |
| **Boldest idea** | Crew as live accounts | Teacher Radar alerts | Lesson Playback Studio | **Publish bluebonnet-runtime spec** |
| **Absent students** | ✅ Async replay | ❌ Missed | ✅ Replay from actual class | ❌ Calls it oversold — honest labeling needed |
| **Scale verdict** | "Transformative if scoped" | "Highly ambitious prototype" | "Promising infra prototype" | **"Ambitious side project, serious infra"** |

### Key Divergences
- **Claude Sonnet** was most creatively provocative — the Crew as live bot personas was the most imaginative single idea
- **Gemini** was most architecturally practical — photo-based math input and Teacher Radar are immediately feasible
- **GPT-5.5** was most teacher-reality grounded — classroom chaos, cognitive load, privacy ops, equity concerns
- **Claude Opus** was the hardest critic and the most strategically ambitious — "curriculum as code" reframes the entire project from a bot to an open standard. Also the only one to flag: curriculum fidelity drift, Crew ethics, FERPA landmine with vector embeddings, discourse loop self-defeat, SPOF risk, and engagement decay

### Updated Risks (From All Four AIs)
- **Math input problem** — typing fractions/graphing in Cinny doesn't work. Solution: snap-photo + vision model grading (Gemini)
- **Pacing collisions** — fire drills, stuck concepts. Solution: Teacher God-Mode DM for Pause/Extend/Skip (Gemini)
- **Chat clutter** — 21+ bots flooding rooms. Solution: careful room design, thread-based discourse (Gemini)
- **Classroom chaos** — memes, spam, bot-testing. Solution: moderation primitives, not just good prompts (GPT-5.5)
- **Cognitive overload for teacher** — too many things to monitor. Solution: Teacher Radar as a *reduction* layer, not an *addition* (GPT-5.5)
- **False confidence from Honcho** — participation ≠ understanding. Solution: evidence quality levels in memory (GPT-5.5)
- **Bot authority** — students treat bot as final answer. Solution: bot models uncertainty, defers to teacher (GPT-5.5)
- **Privacy operations** — exports, deletion, parent requests, moderation logs. The hardest part isn't the tech (GPT-5.5)
- **Equity of access** — chat-first participation biases against quiet/slow/language-developing students. Solution: multiple input paths (GPT-5.5)
- **Ops burden** — teacher maintaining self-hosted Synapse is real (Claude Sonnet)
- **Content pipeline** — 180 days of lessons to digitize (Claude Sonnet)
- **Engagement theater** — typing sentence stems ≠ mathematical understanding (Claude Sonnet)
- **NEW — Curriculum fidelity drift** — bot paraphrasing TEA content instead of verbatim. Silent killer. Solution: eval suite that catches violations (Claude Opus) 🔴
- **NEW — Discourse self-defeat** — 3A Talk in chat replaces the social pressure that makes it work. Bot-seeded peer responses sniffed out in 2 weeks (Claude Opus) 🔴
- **NEW — The Crew is ethically fraught** — students discover bot personas → all bot outputs lose authority. Parents read "AI lied to my kid." COPPA didn't clear deceptive persona design (Claude Opus) 🔴
- **NEW — Teacher becomes a monitor** — if bot runs everything, Abraham is a classroom monitor doing worse pedagogy. Solution: reframe as teacher amplifier (Claude Opus) 🔴
- **NEW — Honcho as FERPA landmine** — vector embeddings are educational records. Must produce human-readable output on parent request. Need parallel auditable log from day one (Claude Opus) 🔴
- **NEW — Single point of failure** — Cloudflare TOS complaint takes class dark mid-period. Need failover-to-printed-PDF plan (Claude Opus) 🔴
- **NEW — Async replay oversells** — bot-only replay = worksheet with chatbot. Missing peer discourse value (Claude Opus)
- **NEW — Engagement decay** — Week 1 bot is cool, Week 8 another assignment. 3B strategies work because physical/kinesthetic (Claude Opus)
- **NEW — OER licensing limits** — Crew characters/trademarked assets may not be relicensable. Talk to TEA before scaling (Claude Opus)
- **NEW — Cognitive Debt (MIT study)** — 83% of students using ChatGPT couldn't recall a single sentence they wrote minutes earlier, vs 11% without AI. The bot must force student effort, not replace thinking (Gemini Research - MIT/Prague School study) 🔴
- **NEW — E2EE "Unable to Decrypt" errors** — In large Matrix rooms with many devices, session keys can desync, causing UTD errors and lost history. Must test at scale (Gemini Research) 🟡
- **NEW — LLM math verification gap** — LLMs are weak in symbolic computation and multi-step reasoning. A wrong answer from the bot destroys trust. Need a verification framework like ValiMath (Gemini Research) 🔴

### Updated Open Questions
1. Does the bot eventually *replace* the slide deck as primary delivery, or *augment* it as an interactive layer?
2. Is this for live synchronous class or self-paced async (or both)?
3. What's the teacher's evolving role if the bot runs the cycle? (Opus: reframe as **teacher amplifier**, not monitor)
4. How to digitize physical Lead4Ward strategies (Four Corners, Gallery Walk) in a chat interface? (Opus: engagement decay risk — these work because physical/kinesthetic)
5. Should the Crew characters become live Matrix bot personas with Honcho memory? (Opus: **ethically fraught** — see risks)
6. Can Honcho data auto-generate "student work analysis protocol" output for PLCs?
7. **Math input:** Should students type math, snap photos of paper work, or draw on a whiteboard in-room?
8. **Teacher Radar DM:** Should the teacher get a private DM channel with the bot for real-time alerts during class?
9. **Lesson Playback:** Should every class session produce a replayable artifact (timeline, misconception heatmap, absent-student replay)?
10. **Privacy ops:** Who owns the data deletion workflow? What's the data retention schedule? Who handles parent data requests? (Opus: vector embeddings = educational records — need human-readable audit log)
11. **Evidence quality:** How does Honcho distinguish "wrote a sentence stem" from "understands the math"?
12. **NEW — Bluebonnet-runtime spec:** Should we define an open spec for executable Bluebonnet lessons (state machine + typed slots) and make the Matrix bot one reference implementation? (Opus: this is the boldest idea) 🟢
13. **NEW — Curriculum fidelity eval:** How do we prevent the bot from paraphrasing TEA content? Do we need an eval suite that catches violations? (Opus: silent killer) 🔴
14. **NEW — SPOF mitigation:** What's the failover plan if Cloudflare/Synapse goes down mid-class? (Opus: documented failover-to-printed-PDF plan needed) 🔴
15. **NEW — OER licensing:** Do we need to talk to TEA about licensing the Crew characters for derivative bot personas before building them? (Opus: yes, before not after scaling) 🟡

---

## 🧱 Architecture for the New Vision

### What Exists Today
```
main.hermes (Discord/CLI/email)
  └── classroom-bot profile (Matrix-only, E2EE)
       ├── Synapse homeserver (8010)
       ├── Cinny web client (8012)
       ├── Honcho memory layer (8020)
       └── room_blocker module
       └── **Attendance System** (deployed)
            ├── Gateway hook: `!here` / `!roll`
            ├── Plugin: registers commands
            ├── Data: JSON per day (`~/.hermes/classroom/attendance/`)
            └── Watchdog: no_agent cron → Discord notifications
```

### What We Need to Build
```
classroom-bot (Hermes profile)
  ├── Lesson Orchestrator
  │   ├── Reads facilitation-notes.json for lesson content
  │   ├── Maps content to campus cycle steps
  │   ├── Posts timed prompts to team rooms
  │   ├── Collects student responses
  │   └── Teacher God-Mode DM (Pause/Extend/Skip override)
  ├── Discourse Engine
  │   ├── Sentence stem prompts
  │   ├── "Ask Yourself" triggers
  │   └── Peer response seeding
  ├── Participation Engine
  │   ├── Reactions / polls
  │   ├── Card Sort mechanics
  │   └── Response collection
  ├── Teacher Radar (NEW)
  │   ├── Private DM channel between teacher and bot
  │   ├── Real-time alerts: stuck teams, misconception spread, silent students
  │   ├── Suggested 90-second teacher interventions
  │   └── Live misconception clustering across teams
  ├── Math Input Handler (NEW)
  │   ├── Snap-photo of handwritten work → vision model grading
  │   ├── Whiteboard drawing in-room (future)
  │   └── Voice note input for ELL students
  ├── Honcho Integration
  │   ├── Per-student participation tracking
  │   ├── Misconception detection with evidence quality levels
  │   ├── Differentiation triggers
  │   ├── Absent-student async replay
  │   ├── Dynamic breakout grouping (reteach vs extension rooms)
  │   ├── **Forgetting Curve Spiral Review** — Tracks temporal decay per-TEKS, auto-inserts review items in Bell Ringer based on when student last demonstrated mastery (Gemini Research)
  │   └── **Per-TEKS STAAR Projection** — Longitudinal mastery model across 51 lessons → early-warning system more accurate than Renaissance/NWEA (Claude Opus + Gemini Research)
  ├── The Crew (future)
  │   ├── AI character bot accounts (Sofia, Marcus, Jayden)
  │   ├── Productive struggle modeling
  │   ├── Honcho memory per character
  │   └── **Synthetic Peer Swarm** (Gemini bold idea) — Dynamic transient peer personas generated per-team with specific logical misconceptions. Students "teach" the synthetic peer by correcting errors. Tutoring-by-teaching is one of the most effective consolidation strategies.
  ├── Lesson Playback Studio (future)
  │   ├── Session timeline (bot posts + teacher interventions + student discourse)
  │   ├── Misconception heatmap by TEKS/student/team
  │   ├── "Critical moment" markers
  │   ├── Absent-student replay from actual class data
  │   ├── Teacher reflection prompts
  │   └── Auto-generated small group plans for next day
  └── Content Pipeline
      ├── Bluebonnet facilitation-notes.json source
      ├── TEA slide deck content extraction
      └── Campus cycle step mapping

### The Bluebonnet-Runtime Spec (Opus Bold Idea)
Above the implementation layer, define an **open spec** for what an executable Bluebonnet lesson is:

```json
{
  "lesson": {
    "id": "G8_M3_T1_L2",
    "metadata": {
      "title": "Drawing Trend Lines",
      "teks": ["8.5D", "8.5I"],
      "days": 2,
      "source": "TEA Bluebonnet G8 M3 T1 L2"
    },
    "cycle": {
      "bell_ringer": { "source": "skills_practice", "problems": [...], "timer_min": 5 },
      "hook": { "type": "dramatic_question", "content": "..." },
      "di_blocks": [
        { "phase": "before", "content": "...", "talk_stems": [...] },
        { "phase": "during", "content": "...", "talk_stems": [...] }
      ],
      "participation": { "strategy": "four_corners", "prompts": [...] },
      "practice": { "problems": [...], "collaborative": true },
      "closure": { "essential_question": "...", "exit_ticket": {...} }
    },
    "memory": {
      "per_teks_tracking": true,
      "evidence_quality": "participation_vs_mastery"
    }
  }
}
```

The Matrix bot is one **reference implementation** of this spec. Others can build different runtimes (Chromebook native app, Google Classroom plugin, classroom display app). TEA can adopt the spec — they have no executable distribution today (only PDFs). Portable to other state OERs.

---

## 📦 Content Pipeline (How the Bot Knows What to Teach)

The facilitation-notes JSON files contain structured lesson data:

```json
{
  "lesson_number": 2,
  "lesson_title": "Drawing Trend Lines",
  "teks": ["8.5D", "8.5I"],
  "essential_ideas_summary": "Trend line (line of best fit)...",
  "common_misconceptions": ["Students may think..."],
  "facilitation_notes": {
    "before": "Facilitation Notes... QUESTIONS TO SUPPORT DISCOURSE...",
    "during": "Activity-specific discourse questions...",
    "after": "Talk the Talk / Essential Question wrap..."
  }
}
```

### What the Bot Mines From Each Field
| Field | Bot Use |
|-------|---------|
| `essential_ideas_summary` | Hook framing → dramatic question |
| `essential_ideas` | DI content + closure framing |
| `common_misconceptions` | 3B activity design + intervention triggers |
| `facilitation_notes.before` | Hook content + 3A sentence stems |
| `facilitation_notes.during` | DI structure + discourse questions |
| `facilitation_notes.after` | Closure content + exit ticket |

---

## 🚶 Next Steps (Prioritized)

### Immediate (Phase 3)
1. Deploy Draupnir Docker container for moderation
2. Finalize COPPA/FERPA data retention policy
3. Set up warm-up cron (school-calendar-aware)
4. **NEW — FERPA audit log:** Begin parallel human-readable per-student log alongside Honcho vector embeddings (Claude Opus — do not retrofit)

### Short-term (Prototype the Vision)
1. Pick **one lesson** — run the full campus cycle through bot in one class period
2. Wire bot to read facilitation-notes.json per lesson
3. Build Bell Ringer posting (pull from Skills Practice PDF)
4. Implement 3A Talk prompt with sentence stems
5. Implement Collect + store Exit Ticket responses in Honcho
6. **Teacher God-Mode:** Build DM channel for Pause/Extend/Skip override
7. **Math Input Pilot:** Test snap-photo → vision model grading with one lesson
8. **NEW — Write the bluebonnet-runtime spec for ONE lesson:** Define Step 1–Step 5 as a JSON state machine with typed slots (Claude Opus bold idea). Other 50 lessons become mechanical.

### Medium-term
1. Full lesson orchestration (all 5 steps)
2. Async classroom replay for absent students — label honestly as "worksheet with chatbot" not "lesson replay"
3. **Teacher Radar:** Private DM channel with real-time alerts (stuck teams, silent students, misconception spread)
4. Cross-period analytics dashboard
5. Dynamic breakout grouping by Honcho (reteach vs extension sub-rooms)
6. Re-evaluate Crew bot personas after TEA/legal review (Claude Opus: do not deploy without clearance)
7. **Evidence quality levels:** Honcho distinguishes "participated" from "understands"
8. **Curriculum fidelity eval suite:** Automated checks that catch bot paraphrasing TEA content. Test after every content pipeline change (Claude Opus: silent killer)
9. **NEW — Forgetting Curve Spiral Review:** Honcho tracks temporal decay per-TEKS, auto-inserts review in Bell Ringer (Gemini Research)
10. **NEW — Math verification framework:** Step-by-step answer validator (ValiMath pattern) to catch LLM math errors before they reach students (Gemini Research) 🔴

### Long-term
1. **Lesson Playback Studio:** Every session becomes a replayable artifact (timeline, heatmap, critical moments, absent replay)
2. Drag-and-drop lesson authoring
3. Multi-classroom deployment (portable to other Texas teachers)
4. **NEW — SPOF mitigation:** Documented failover plan (printed PDFs, offline mode) for days Cloudflare/Synapse goes dark (Claude Opus)
5. Per-TEKS STAAR early-warning system (Claude Opus blind spot — the "principal goes to bat" artifact)
6. **Synthetic Peer Swarm:** Dynamic transient peer personas with specific misconceptions. Students "teach" by correcting errors (Gemini Research bold idea)
7. **Digital Training Twin:** Async classroom replay as a full interactive recreation — not just transcript, but the 3A Talk, Lead4Ward, and practice phases (Gemini Research)
8. Distraction detection during 3B activities
9. Student-facing progress dashboards
10. Local teaching intelligence layer: System learns which hooks/prompts/problems work best for this specific class

---

## ⚡ Key Principles (Do Not Violate)

1. **Verbatim content only** — Never summarize Bluebonnet content. Extract exact text from TEA slides. Abraham will reject paraphrased content.
2. **The Crew stays** — Include all Crew content as-is from Bluebonnet materials. Never suggest removing them.
3. **One concept per slide** — Same applies to bot messages. One concept, 4-6 items max, 28pt equivalent.
4. **Scope guardrails** — Skills Practice mapping, Bell Ringer sheets, Grade 7 decks, 3A Google Docs = explicitly ruled out unless Abraham asks.
5. **Green theme (Algebra I) vs Purple theme (Grade 8)** — Badge colors must pop off the theme. Algebra I uses Gold for Talk, Orange for Practice.
6. **Math needs a non-typing path** — Students cannot be expected to type fractions, graphs, or geometry in a linear chat. Snap-photo + vision model grading is the primary solution. Whiteboard drawing and voice input are secondary paths.
7. **Teacher Radar is a reduction layer, not an addition** — Every alert the bot sends to the teacher should reduce cognitive load, not increase it. If a feature makes the teacher monitor more things, it fails.
8. **Evidence quality levels, not activity logs** — Honcho must distinguish "wrote a sentence stem" from "understands the concept." Participation is not understanding.
9. **Bot models uncertainty** — The bot is never the final answer source. It defers to the teacher, asks students to reason, and says "I'm not sure — what do you think?" when appropriate.
10. **Curriculum as code, not chat** — The core deliverable is an executable state curriculum, not a chatbot. The Matrix bot is one reference implementation of a curriculum runtime (Claude Opus).
11. **Teacher amplifier, not teacher replacer** — The bot handles logistics, timing, memory, and data collection. The teacher owns live reteach decisions, behavioral signal reading, and the human moments (Claude Opus).
12. **No deceptive persona design without legal review** — Bot accounts that simulate human students ("the Crew") are ethically fraught. Get TEA and legal clearance before deploying. COPPA cleared a chat platform, not deceptive personas (Claude Opus).
13. **Human-auditable FERPA log from day one** — Vector embeddings are educational records. Maintain a parallel human-readable per-student log that can be produced on parent request (Claude Opus).
14. **Prevent Cognitive Debt** — The bot must force student effort, not replace thinking. Every prompt should require the student to produce original reasoning before receiving feedback. If the bot makes thinking feel optional, it's harming learning (Gemini Research — MIT study: 83% vs 11% recall).
15. **Verify math before students see it** — LLMs make arithmetic and multi-step reasoning errors. Every math output must pass through a step-by-step verification framework (ValiMath pattern) before reaching students (Gemini Research).
16. **Document everything** — Any bot joining this project should first read VISION.md, SNAPSHOT.md, plan.md, and compliance.md.

---

## 📁 Project File Map

```
~/projects/matrix-classroom/
├── plan.md                 — Full implementation plan + ADRs
├── SNAPSHOT.md             — Current state snapshot
├── VISION.md               ← YOU ARE HERE
├── TRACKER.md              — Phase checklist
├── compliance.md           — COPPA/FERPA status
├── comparison.md           — Synapse vs Conduit vs Dendrite
├── clients.md              — Cinny vs Element vs Hydrogen
├── feature-ownership.md    — Server vs client vs bot feature map
├── student-creds.md        — Student credentials
├── claude-feedback.md      — External audit (11 action items)
├── gemini-research-analysis.md — Full research paper (32 cited sources) by Gemini — formal academic analysis of project architecture, pedagogy, risks, and emergent capabilities
├── infrastructure-design.md — 701-line buildable spec by Claude Opus — architecture, component designs, data flow, risk mitigations, phased build plan mapped to VISION milestones
├── deploy/
│   ├── synapse/            — Synapse config + modules
│   │   └── modules/
│   │       └── room_blocker.py  — Room creation blocker
│   ├── cinny/              — Cinny web client config
│   └── docker-compose.yml  — Container orchestration
└── ~/.hermes/profiles/classroom-bot/
    ├── config.yaml         — Bot config (Matrix-only gateway)
    ├── SOUL.md             — Bot personality (calm facilitator)
    ├── hooks/classroom-attendance/  — Attendance gateway hook
    │   ├── HOOK.yaml
    │   └── handler.py
    └── plugins/classroom-attendance/  — !here/!roll command plugin
        ├── plugin.yaml
        └── __init__.py

~/.hermes/
├── hooks/classroom-attendance/      — Mirror hook (main profile)
├── scripts/attendance_watch.py      — Watchdog script (no_agent cron)
└── classroom/attendance/            — Daily check-in JSON files
```

---

## 🔗 Quick Reference

| What | Where |
|------|-------|
| Matrix server | https://class.mr-romero.com / class.epaphrodit.us |
| Cinny client | https://class.epaphrodit.us (port 8012) |
| Bluebonnet resources | `~/Bluebonnet/` |
| Facilitation notes | `~/Bluebonnet/Grade8/facilitation-notes.json` |
|| Bot profile | `~/.hermes/profiles/classroom-bot/` |
|| `!here` command | Attendance check-in — any Matrix user (pre-reg not needed) |
|| `!roll` command | Teacher-only: show today's attendance |
|| Attendance data | `~/.hermes/classroom/attendance/YYYY-MM-DD.json` |
|| Honcho API | http://localhost:8020 |
| Herald (memory viewer) | http://localhost:8021 |
| This document | `~/projects/matrix-classroom/VISION.md` |
