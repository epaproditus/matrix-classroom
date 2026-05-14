# Matrix Classroom AI 🏫🤖

A **self-hosted classroom discussion platform** powered by Matrix with Hermes Agent as an AI facilitator, Draupnir as the moderation bot, and Cinny as the student client.

## Current Stack 🎯

| Layer | Choice | Status |
|-------|--------|--------|
| 🏠 **Homeserver** | [Synapse](https://github.com/element-hq/synapse) | ✅ Running (:8010) |
| 📊 **Admin GUI** | [Ketesa](https://github.com/etkecc/ketesa) | ✅ Running (:8011) |
| 👩‍🎓 **Student Client** | [Cinny](https://cinny.in/) | ✅ Running (:8012) |
| 🤖 **AI Bot** | [Hermes Agent](https://hermes-agent.nousresearch.com/) | ✅ Running (main + classroom-bot profiles) |
| 🧠 **Memory Layer** | [Honcho](https://github.com/plastic-labs/honcho) (self-hosted) | ✅ Running (:8020) |
| 🛡️ **Moderation Bot** | [Draupnir](https://github.com/the-draupnir-project/Draupnir) | ⏳ Planned (Phase 3) |
| 🏅 **Badge Bot** | Hermes (no separate bot) | 🔮 Future |

## Why This Stack?

- **Synapse** is the only Matrix homeserver with an admin GUI ecosystem (Ketesa). Conduit and Dendrite have no admin dashboards — every task requires terminal/curl. For a classroom, being able to manage students from a web UI is essential.
- **Ketesa** is the evolution of Synapse-Admin — a polished, modern dashboard for managing users, rooms, media, and moderation from the browser.
- **Cinny** is the cleanest Matrix client for students — minimal, Discord-like UI, no clutter. Students just open a browser, log in, and chat.
- **Hermes** handles AI facilitation, tutoring, warm-ups, and discussion management.
- **Draupnir** handles auto-moderation: word filters, auto-kick, ban propagation, abuse reports.

## What This Is

A project to run a fully self-hosted Matrix classroom where:
- Students log in via **Cinny** (browser, no install)
- Class splits into **team rooms** for daily discussions
- **Hermes** lives in every room — posting warm-ups, facilitating, tutoring
- **Draupnir** keeps things clean — word filters, auto-kick
- Students can **DM Hermes** for 1:1 tutoring
- All student interactions remembered via **Honcho** (per-student memory workspace)
- You manage everything via **Ketesa** web dashboard

## What We're NOT Using

- ❌ **Conduit** — No admin GUI
- ❌ **Dendrite** — No admin GUI, forked, confusing status
- ❌ **Rocket.Chat** — Not Matrix protocol, Hermes can't connect

## Project Structure

```
matrix-classroom/
├── README.md              # ← You are here
├── TRACKER.md             # Progress tracker & checklist
├── plan.md                # Implementation plan & architecture decisions
├── SNAPSHOT.md            # Current state snapshot
├── memory-architecture.md # Honcho memory provider architecture
├── compliance.md          # COPPA/FERPA compliance tracking
├── honcho-fix-log.md      # Honcho integration issue log
├── user-cleanup-plan.md   # Test account cleanup plan
├── comparison.md          # Synapse vs Conduit vs Dendrite deep dive
├── clients.md             # Cinny vs Element vs Hydrogen comparison
├── claude-feedback.md     # External audit from Claude Code
├── feature-ownership.md   # Server vs Client vs Bot feature map
└── student-creds.md       # Student credentials (deactivated accounts)
```

## Status

🚀 **Infrastructure deployed and running.** Synapse + Cinny + Ketesa + Honcho are all operational behind Cloudflare Tunnel at class.mr-romero.com (also accessible via class.epaphrodit.us for school-access). Hermes running in two profiles (main + classroom-bot) connected via Matrix and Discord gateways. Honcho memory layer storing conversations in two workspaces.

**Next:** Phase 3 Draupnir moderation, then reopening student accounts.
