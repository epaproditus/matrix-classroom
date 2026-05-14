# 🏫 Matrix Homeserver Comparison — Classroom Edition

**Context:** Self-hosted classroom discussion platform with Hermes AI bot.
**Priority:** Lowest barrier to entry, admin GUI, moderation, student management.

---

## 📊 At a Glance

| Feature | Synapse | Conduit | Dendrite |
|---------|---------|---------|----------|
| **Language** | 🐍 Python + Rust | 🦀 Rust | 🏃 Go |
| **License** | AGPL-3.0 / Commercial | Apache-2.0 | AGPL-3.0 / Commercial |
| **Stability** | ✅ Stable | ✅ Beta | ✅ Beta |
| **Market Share** | **85.8%** | 4.1% | 3.1% |
| **RAM (idle)** | ~500MB–2GB | **~32–150MB** | ~200–500MB |
| **Database** | PostgreSQL (required) | **SQLite** (no extra DB!) | PostgreSQL |
| **Setup Time** | ~30 min (many options) | **~5 min** (single binary) | ~20 min |
| **Admin GUI** | ✅ Synapse-Admin (rich) | ❌ None built-in | ⚠️ Minimal API |
| **Docker Image** | ✅ Official | ✅ Community | ✅ Official |
| **Runs on Pi?** | ⚠️ Barely (4GB+) | ✅ Easily (2GB Pi) | ⚠️ 4GB recommended |

---

## 🔍 Deep Dive

### 1️⃣ Synapse — The Reference Standard

```

         Synapse Homeserver
  ┌──────────────────────────────────┐
  │  Python / Twisted / Rust         │
  │  PostgreSQL DB                   │
  │                                  │
  │  ┌──────────────────────┐        │
  │  │   Synapse-Admin UI   │        │
  │  │   (React Dashboard)  │        │
  │  │  ┌────┐ ┌────┐ ┌───┐│        │
  │  │  │Users│ │Rooms│ │Mod││        │
  │  │  └────┘ └────┘ └───┘│        │
  │  └──────────────────────┘        │
  │                                  │
  │  ┌──────────────────────┐        │
  │  │   Mjolnir Mod Bot    │        │
  │  │  (ban/kick/protect)  │        │
  │  └──────────────────────┘        │
  └──────────────────────────────────┘
         ↕ Matrix Protocol ↕
  ┌──────────────────────────────────┐
  │   Element Web (student client)   │
  └──────────────────────────────────┘
```

**✅ Pros (for a classroom):**
- **Best admin GUI** — Synapse-Admin gives you a web dashboard for managing users, rooms, bans, etc. No terminal needed for day-to-day.
- **Mjolnir** — A Matrix bot specifically for moderation (ban, kick, protect rooms). Great for classroom control.
- **Most community support** — 85% of Matrix servers run Synapse. If you Google a problem, you'll find answers.
- **Most feature-complete** — Spaces, threads, E2EE, bridges, read receipts, typing indicators all work perfectly.
- **Best bridge support** — Want to connect your Matrix rooms to Discord? Synapse does this best with matrix-appservice-discord.
- **Lots of setup guides** — The ansible playbook, Docker Compose examples, Yunohost, etc.

**❌ Cons (for a classroom):**
- **RAM hungry** — Idle at ~500MB+, can spike to 2GB. On your home server, this competes with everything else you run.
- **PostgreSQL dependency** — You need to run a Postgres container too. More moving parts.
- **Complex config** — `homeserver.yaml` has hundreds of options. Can be overwhelming.
- **Python perf** — Known for CPU spikes during large room syncs (less relevant for small class though).
- **Heavier Docker Compose** — Synapse + Postgres + optionally Synapse-Admin + optionally Mjolnir.

**💡 Verdict:** *You know it'll work, but it's overkill unless you want the admin GUI badly.*

---

### 2️⃣ Conduit — The Lightweight Champion

```

        Conduit Homeserver
  ┌──────────────────────────────────┐
  │  Rust / Single Binary            │
  │  SQLite (file-based DB)          │
  │                                  │
  │  ┌──────────────────────┐        │
  │  │  No built-in admin UI │        │
  │  │  Manage via Element   │        │
  │  │  or Admin API (curl)  │        │
  │  └──────────────────────┘        │
  │                                  │
  │  Total RAM: ~32MB idle           │
  └──────────────────────────────────┘
        ↕ Minimal config ↕
  ┌──────────────────────────────────┐
  │   Element Web (student client)   │
  └──────────────────────────────────┘
```

**✅ Pros (for a classroom):**
- **Incredibly lightweight** — ~32MB RAM at idle. Can run on a Raspberry Pi 3 alongside other containers.
- **No PostgreSQL!** — SQLite only. Zero database setup. The whole server is like 3 config lines.
- **Single binary** — Download, run, done. No dependencies to install.
- **Rust performance** — Fast, memory-safe, no GC pauses.
- **Perfect for your setup** — You're already running Docker containers; Conduit adds almost zero resource overhead.
- **Matrix spec compliant** — Core features all work (E2EE, spaces, threads, typing).

**❌ Cons (for a classroom):**
- **No admin GUI** — You manage users via curl/admin API or Element client directly. Want to create accounts? `curl -X POST ...` or do it in Element.
- **Beta maturity** — Minor bugs may pop up. Active development but smaller team.
- **Smaller community** — Fewer guides, less help available if something breaks.
- **Missing federation features** — Outgoing read receipts/typing/presence over federation don't work yet (might not matter for a closed classroom).
- **No Mjolnir** — Moderation is manual via admin API, no bot ecosystem.

**💡 Verdict:** *Lowest barrier to entry. One Docker container, one config, done. Trade-off: no admin dashboard.*

---

### 3️⃣ Dendrite — The Middle Ground

```

       Dendrite Homeserver
  ┌──────────────────────────────────┐
  │  Go / Multi-component            │
  │  PostgreSQL DB                   │
  │                                  │
  │  ┌──────────────────────┐        │
  │  │  Admin API (no GUI)  │        │
  │  │  curl-based mgmt     │        │
  │  └──────────────────────┘        │
  │                                  │
  │  Total RAM: ~200-500MB           │
  └──────────────────────────────────┘
        ↕ Matrix Protocol ↕
  ┌──────────────────────────────────┐
  │   Element Web (student client)   │
  └──────────────────────────────────┘
```

**✅ Pros (for a classroom):**
- **Lighter than Synapse** — ~200-500MB RAM is a nice middle ground.
- **Go performance** — Good concurrency, fast startup.
- **Future-proof architecture** — Designed to scale better than Synapse long-term.
- **Official Matrix project** — Built by the same team as Synapse (Element).
- **PostgreSQL** — More robust than SQLite for multi-user, but still needs management.

**❌ Cons (for a classroom):**
- **No admin GUI** — Like Conduit, you're using curl/admin API.
- **Not spec-complete** — Missing some client features. Threads are experimental.
- **Bridges not well-tested** — If you ever want Discord bridging, this is riskier.
- **Fork situation** — Element forked Dendrite in 2023. The Matrix Foundation version and Element-HQ version are diverging. Confusing for new users.
- **Smallest community** — 3.1% market share, least community support.
- **PostgreSQL needed** — Not as simple as Conduit's SQLite.

**💡 Verdict:** *Stuck in the middle. Not as powerful as Synapse, not as simple as Conduit. Hardest to recommend for a classroom.*

---

## 🖥️ Admin GUI Comparison

This might be the deciding factor. Here's what managing users/rooms looks like:

### Synapse + Synapse-Admin
```
┌───────────────────────────────────────────────┐
│  Synapse Admin  │  Dashboard                  │
├───────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌──────────────────┐ │
│  │ 👥 Users │ │ 🚪 Rooms │ │ 🔨 Moderation    │ │
│  │  24      │ │  12     │ │  Report Queue    │ │
│  └─────────┘ └─────────┘ └──────────────────┘ │
│                                                │
│  ┌─── User List ─────────────────────────────┐ │
│  │ ✅ 🟢 @student1:classroom.space           │ │
│  │ ✅ 🟡 @student2:classroom.space  [BAN]   │ │
│  │ ✅ 🟢 @student3:classroom.space           │ │
│  │ ❌ 🔴 @badactor:classroom.space           │ │
│  │    Create User  ⚡ Reset Password          │ │
│  └────────────────────────────────────────────┘ │
└───────────────────────────────────────────────┘
```
**You get:** Point-and-click user management, room listing, password resets, deactivation, ban/unban. Very intuitive for a teacher who doesn't want to use the terminal.

### Conduit / Dendrite
```
┌───────────────────────────────────────────────┐
│  Terminal (no admin GUI)                      │
├───────────────────────────────────────────────┤
│                                                │
│  $ curl -X POST https://matrix.server/... \   │
│    -H "Authorization: Bearer ..."            │
│    -d '{"username":"student1","password":"..."}'
│                                                │
│  # Or use Element client to:                  │
│  # - Invite users to rooms                     │
│  # - Change user power levels                  │
│  # - Kick/ban from room context menu           │
│                                                │
└───────────────────────────────────────────────┘
```
**You get:** Everything is via admin API (curl) or inside Element client. Creating accounts requires a terminal command or a script. Banning can be done via Element's room admin interface.

---

## 🏆 Recommendation Breakdown

Given your criteria — **lowest barrier of entry, classroom use, Hermes integration, student memory**:

### If you want: **"Set it and forget it, GUI for management"**
→ **Synapse** is your pick
- Docker Compose: Synapse + Postgres + Synapse-Admin + Hermes
- You get a web dashboard for managing students
- Mjolnir for automated moderation
- ~1GB RAM total for the whole stack

### If you want: **"Lightest, fastest setup, don't mind CLI"**
→ **Conduit** is your pick
- One Docker container, SQLite, done in 5 minutes
- ~32MB RAM — barely a blip on your home server
- Manage students via simple curl scripts (I can write those for you)
- Perfect for starting small and iterating

### If you want: **"Somewhere in between"**
→ Don't pick Dendrite. It's in an awkward spot — not spec-complete, no admin GUI, fork confusion.

---

## 📐 Estimated Docker Compose Footprint (per option)

### Option A: Synapse Stack
```
Container            │ RAM     │ Image Size
─────────────────────┼─────────┼───────────
Synapse              │ ~500MB  │ ~150MB
PostgreSQL 16        │ ~200MB  │ ~400MB
Synapse-Admin        │ ~80MB   │ ~50MB
Hermes (Matrix GW)   │ ~200MB  │ (existing)
Mjolnir (optional)   │ ~50MB   │ ~100MB
─────────────────────┼─────────┼───────────
TOTAL                │ ~1GB    │
```

### Option B: Conduit Stack
```
Container            │ RAM     │ Image Size
─────────────────────┼─────────┼───────────
Conduit              │ ~50MB   │ ~15MB  (Alpine!)
Hermes (Matrix GW)   │ ~200MB  │ (existing)
─────────────────────┼─────────┼───────────
TOTAL                │ ~250MB  │
```

---

## 🧪 My Personal Take

For a **classroom**, having an admin GUI really matters. You don't want to SSH in and curl every time a student forgets their password or needs to be moved to a different team.

**Synapse** gives you that GUI via Synapse-Admin. Yes, it's heavier. But your use case isn't "1000 users on a Pi" — it's a classroom of ~30 kids. Even Synapse will barely break a sweat.

**Conduit** is tempting for the simplicity, but every user management task becomes a terminal command or an Element client action. Great if you love the terminal, less great if you just want to teach.

**My vote: Start with Synapse.** You can always migrate to Conduit later if resource usage becomes an issue (migration is hard but possible). Starting with the GUI-first option means less friction day-to-day.

But if you want to try **Conduit first** because "lowest barrier of entry" and you're fine writing a few scripts for account management, I'll 100% support that too! 😄

---

## Next Step

Ready to pick one? I'll Docker Compose the whole thing and get you a working prototype! 🚀
