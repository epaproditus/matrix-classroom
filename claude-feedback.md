# 🤖 Claude's Review — External Audit of Our Plan

We asked [Claude Code](https://code.claude.com/) (Anthropic's autonomous coding agent) to review the Matrix Classroom AI plan on 2026-05-12. Here's their full feedback.

---

## ✅ What Claude Liked

- **Well-structured phases** — clear ownership, experiment→replicate pattern
- **Feature ownership map** is mostly correct (server vs client vs bot)
- **Stack choices are solid** — Synapse for admin GUI, Cinny for students, Draupnir for mod
- **80% there** — the core architecture is sound

---

## ⚠️ Critical Gaps

### 1. COPPA/FERPA Compliance 🏛️

**This is the elephant in the room.** These are middle school minors. Self-hosted Matrix with AI bots processing student data triggers serious compliance questions:

- **Parental consent documentation** needed
- **Data retention/deletion policies** needed
- **What does Mem0 store and where?** Student conversations could hit external LLM APIs (OpenAI, Anthropic) unless Hermes is pointed at a local model
- **Right to be forgotten** — what happens when a student asks to delete their data?

**🛠️ Fix:** Add compliance review before any student data enters the system.

### 2. Mem0 is Underspecified 🧠

Plan mentions Mem0 once but doesn't define:
- Where does it run? (Container? Separate DB?)
- What does it store? (Conversation summaries? Raw messages?)
- How is it queried? (Hermes calls it automatically?)
- What happens when a student asks to be forgotten?
- Would a simple CSV export be better for the teacher?

**🛠️ Fix:** Design Mem0 interaction model before Phase 4.

> **🟢 Resolved (2026-05-13):** Replaced Mem0 with **self-hosted Honcho**. See `memory-architecture.md` and ADR-003 in `plan.md`. Honcho's workspace + peer model maps 1:1 to the classroom, and self-hosting keeps student data on-premises.

### 3. No Backup Plan 💾

Home lab + PostgreSQL + student data = **automated backups from day one.** Not "later."

**🛠️ Fix:** Add pg_dump cron job to Phase 1.

### 4. No Authentication Hardening 🔐

Middle schoolers will:
- Share passwords
- Try each other's accounts
- Forget credentials weekly

No password reset flow, no 2FA, no session management strategy.

**🛠️ Fix:** Add password reset workflow and account recovery plan.

---

## 🕳️ Key Pitfalls

| Pitfall | Details | Mitigation |
|---------|---------|------------|
| **Synapse RAM** | Synapse + PostgreSQL + Draupnir + Hermes = 2-4GB+ on a home lab | Test under load early. Monitor with Uptime Kuma |
| **Draupnir config complexity** | Policy lists are powerful but not intuitive. False positives on middle school slang will erode trust fast | Budget real tuning time. Start with small word list |
| **Hermes too noisy** | If Hermes responds to every message in a 4-person team room, it dominates conversation | Define trigger rules: mention-only? cooldown timer? max messages per minute? |
| **Cron on weekends/holidays** | Trivial but easy to forget — warm-ups fire on Saturday | School-calendar-aware scheduler or manual toggle |
| **E2EE + Bots = Pain** | If rooms are E2EE (Cinny defaults to this), bots struggle with key verification. Draupnir especially | **Disable E2EE for classroom rooms** — these aren't private conversations |
| **Version pin everything** | A breaking update on a school night is a nightmare | Pin Synapse, Draupnir, Cinny to specific Docker tags |

---

## 🔄 Priority Reorder (Claude's Suggestion)

Claude says our current phase order is off:

| Our Order | Claude's Order | Reason |
|-----------|----------------|--------|
| 1. Infrastructure | **1. Compliance/Legal** (NEW) | Parental consent, data policy, IT approval BEFORE building |
| 2. Student Client | **2. Infrastructure** | Same — need a server first |
| 3. Bots | **3. Classroom Structure** | Move this UP — rooms + students working first. Bots are additive |
| 4. Classroom Structure | **4. Draupnir Moderation** | Move UP — moderation must exist before students enter rooms |
| 5. Hermes Behaviors | **5. Hermes AI** | Move DOWN — AI facilitation can wait a week |
| 6. Badges | **6. Badges** | Same — optional future |

**Key insight from Claude:** "A classroom that works without bots is useful; bots without a classroom structure aren't."

---

## 💡 Recommendations

### Pilot First 🧪
Start with **3 students, not a full class.** Pilot for 2 weeks. Find every UX papercut before 30 kids hit it simultaneously.

### Teacher Dashboard 📊
Ketesa manages Matrix infra, not classroom pedagogy. Abraham will want:
- "Who participated today?"
- "What did Hermes discuss?"
- "Any moderation events?"

This is a **custom view**, not Ketesa. Consider building a simple dashboard.

### Pin Hermes Behavior Precisely 🤖
Define in writing before implementing:
- When does Hermes speak unprompted? (only when mentioned? daily warm-up only?)
- Max messages per minute per room?
- What topics does it refuse? (Not just profanity — off-topic, homework answers)
- How does it handle wrong answers? (Scaffolding vs. correction vs. silence)

### Use Caddy for Reverse Proxy 🌐
Auto-HTTPS, simpler config than nginx for a home lab. Less maintenance.

### Version Pin Everything in Docker 🐳
```yaml
image: matrixdotorg/synapse:v1.150.0  # Not :latest
image: ghcr.io/etkecc/ketesa:v1.2.1   # Not :latest
```

### Add Monitoring
Even basic — **Uptime Kuma** or similar. If Synapse dies at 7am before class, Abraham needs to know before students tell him.

### Student Offboarding Plan 🚪
End of semester: what happens to accounts, messages, Mem0 data? **FERPA requires this answer.**

### Hydrogen is Dead 💀
Element archived it. Remove from client comparison.

### Drop Commet from Plan
Mentioned as teacher option but adds confusion. Pick Element for teacher, Cinny for students, done.

---

## Verdict

> **"Plan is 80% there. Biggest gaps: legal compliance for minors, Mem0 design, E2EE vs. bot compatibility, and Hermes behavior specification. Reorder to get moderation live before AI, and pilot small before full class rollout."**
>
> — Claude Code (Anthropic)
