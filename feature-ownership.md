# 🗺️ Feature Ownership Map — Server vs Client vs Bot

Not every feature comes from the same place. Here's what you need to know:

---

## The Three Layers

```
┌────────────────────────────────────────────────────────┐
│                    CLIENTS                              │
│  What students see & interact with                     │
│  ┌──────┐ ┌──────┐ ┌────────┐ ┌────────┐              │
│  │Cinny │ │Element│ │Commet  │ │Hydrogen│              │
│  └──────┘ └──────┘ └────────┘ └────────┘              │
├────────────────────────────────────────────────────────┤
│                    BOTS                                 │
│  Automated accounts that do things in rooms            │
│  ┌──────────┐ ┌──────────┐ ┌─────────────┐            │
│  │ Hermes   │ │ Draupnir │ │ Badge Bot   │            │
│  │ (AI)     │ │ (Mod)    │ │ (Gamificat) │            │
│  └──────────┘ └──────────┘ └─────────────┘            │
├────────────────────────────────────────────────────────┤
│                    HOMESERVER                           │
│  The engine — stores messages, auth, federation         │
│  ┌─────────┐ ┌──────────┐ ┌──────────────┐            │
│  │Synapse  │ │PostgreSQL│ │Synapse-Admin │            │
│  └─────────┘ └──────────┘ └──────────────┘            │
└────────────────────────────────────────────────────────┘
```

---

## ✅ What's Built Into Every Matrix Server

These are **protocol-level features** — any server (Synapse, Conduit, Dendrite) supports them:

| Feature | How it works |
|---------|-------------|
| **Reactions (👍)** | Matrix protocol supports `m.reaction` events. ✅ Works on all servers |
| **Kick users** | Standard room power levels — admins can kick/ban ✅ |
| **Ban users** | Full ban API ✅ |
| **Room redaction** | Delete any message in a room ✅ |
| **Power levels** | Control who can speak, invite, kick, ban ✅ |
| **Multiple bots** | Each bot is just a user account. Add as many as you want ✅ |
| **Admin API** | REST API for user management, room management ✅ |

**Every homeserver does all of these.** Synapse, Conduit, Dendrite — doesn't matter.

---

## ⚠️ What DEPENDS on the Client

Whether students can *see* and *use* these features depends on which client they open:

| Feature | Cinny | Element | Commet | Hydrogen |
|---------|-------|---------|--------|----------|
| **Emoji Reactions** | ✅ Custom emoji packs | ⚠️ Limited | ✅ Yes | ❌ No |
| **Threads** | ✅ | ✅ | ✅ | ❌ No |
| **Custom Emoji/Stickers** | ✅ Emoji packs | ⚠️ Limited | ✅ Emoji packs | ❌ No |
| **File Preview** | ✅ | ❌ | ❌ | ❌ No |
| **Voice/Video** | ❌ No | ✅ Yes | ✅ Yes | ❌ No |
| **Multi-Account** | ❌ No | ❌ No | ✅ Yes | ❌ No |
| **GIF Search** | ❌ No | ❌ No | ✅ Yes | ❌ No |
| **💬 Text Chat** | ✅ | ✅ | ✅ | ✅ Bare |

**Key insight:** Reactions exist in the protocol but *display* depends on client. Cinny supports custom emoji packs. Element supports reactions. Hydrogen is barebones.

---

## 🔧 What Requires a BOT (Add-On)

These are NOT built into the server or client — you need a bot:

| Feature | Bot Needed | How |
|---------|-----------|-----|
| **Auto-kick for bad words** | **Draupnir** (or Hermes) | Word-based policy lists → auto-kick |
| **Censor / redact messages** | **Draupnir** (or Hermes) | Policy server auto-redacts |
| **Badges / roles / points** | **Custom Badge Bot** (or Hermes) | Bot assigns roles in room state |
| **AI discussion facilitation** | **Hermes** 🤖 | Your AI bot in every team room |
| **DM tutoring** | **Hermes** 🤖 | AI answers student questions 1:1 |
| **Auto-kick new users** | **Draupnir** | Policy server + trust scoring |
| **Report review** | **Draupnir** | Review + act on abuse reports |
| **Ban propagation** | **Draupnir** | Subscribe to shared ban lists |
| **Daily warm-ups** | **Hermes** 🤖 | Cron → Hermes posts to rooms |

---

## 🤖 Multiple Bots — Yes, This is Normal!

Matrix handles multiple bots easily. Each bot is just a user account. You'd run:

```
Your Matrix Server
┌────────────────────────────────────────────────────┐
│                                                     │
│  Room: Team Alpha                                   │
│  ┌────────────────────────────────────────────┐     │
│  │  🤖 Hermes: "Warm-up: solve for x..."      │     │
│  │  👩 Maria: "x = 5"                         │     │
│  │  🤖 Draupnir: "⚠️ Watch your language, kid"│     │
│  │  🤖 Hermes: "Great job Maria!"             │     │
│  │  🤖 BadgeBot: "🏅 Maria earned the         │     │
│  │    'Quick Thinker' badge!"                 │     │
│  └────────────────────────────────────────────┘     │
│                                                     │
│  Bots running:                                      │
│  ├── Hermes    (AI facilitator)  ~200MB RAM         │
│  ├── Draupnir  (moderation)      ~50MB RAM          │
│  └── BadgeBot  (gamification)    ~30MB RAM          │
└────────────────────────────────────────────────────┘
```

**All three bots work in the same rooms simultaneously.** No conflicts.

---

## 🎯 Your Specific Wants — Mapped

| You said… | What handles it | Verdict |
|-----------|----------------|---------|
| **Reactions** | ✅ Protocol + Client (Cinny ✅, Element ✅) | Works on any server |
| **Badges** | 🔧 Need a custom bot | Not built-in, build w/ Hermes |
| **Bot kick kids** | 🤖 Draupnir bot | Battle-tested, Docker-ready |
| **Censor / filter** | 🤖 Draupnir policy lists | Word lists + auto-redact |
| **Multiple bots** | ✅ Matrix supports unlimited bots | Yes, no limit |
| **Admin GUI** | 📊 Synapse-Admin (for Synapse only) | Synapse exclusive |

---

## 🏆 So… Which Server?

Your questions actually **don't favor one server over another** for these features:

- ✅ Reactions = protocol
- ✅ Kicking/banning = protocol  
- ✅ Multiple bots = protocol
- ✅ Moderation = Draupnir bot (works with ALL servers)
- ❌ Badges = custom bot (works with ALL servers)

**The one thing that DOES depend on server choice:** 💊 **Admin GUI**

- **Synapse** → Synapse-Admin dashboard (web UI for managing users/rooms)
- **Conduit** → No admin GUI (curl/API only)
- **Dendrite** → No admin GUI (curl/API only)

So Synapse wins if you want a dashboard. Conduit wins if you want lightweight. Your *classroom features* work identically on either.

---

## 🧪 Full Recommended Stack

```
┌─────────────────────────────────────────────────────┐
│  YOUR SERVER                                         │
│                                                      │
│  ┌─── Homeserver ─────────────────────────────┐     │
│  │  Synapse (or Conduit)                      │     │
│  │  PostgreSQL (if Synapse) / SQLite (Conduit)│     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  ┌─── Admin (if Synapse) ──────────────────┐        │
│  │  Synapse-Admin — web dashboard for YOU  │        │
│  └─────────────────────────────────────────┘        │
│                                                      │
│  ┌─── Bots ─────────────────────────────────┐        │
│  │  Hermes    — AI facilitator + tutor      │        │
│  │  Draupnir  — Moderation (kick/censor)    │        │
│  │  [Optional] BadgeBot — Gamification      │        │
│  └──────────────────────────────────────────┘        │
│                                                      │
│  ┌─── Student Clients ──────────────────────┐        │
│  │  Cinny (recommended) — clean Discord-ish │        │
│  │  Element (backup) — more features        │        │
│  └──────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────┘
```

**Bottom line:** Everything you want works on any homeserver. Synapse gives you an admin dashboard. Conduit saves RAM. Pick based on that trade-off! 🎯
