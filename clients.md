# 🖥️ Student-Facing Clients — What your students see

This matters more than the homeserver! Here's what your kids would actually open in their browser.

---

## 1️⃣ Element Web — The Default Choice

```
┌──────────────────────────────────────────────────────────┐
│  Element                                    [👤] [⚙️]   │
├──────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────────────────────────────────┐  │
│  │ 📁 Rooms │  │  🟢 Team Alpha                      │  │
│  │          │  │                                      │  │
│  │ 🔴 Team  │  │  🤖 Hermes Bot: Good morning! Today's │  │
│  │   Alpha  │  │  warm-up: If 3x + 7 = 22, what's x?  │  │
│  │          │  │                                      │  │
│  │ 🔵 Team  │  │  Maria: x = 5 right?                 │  │
│  │   Beta   │  │                                      │  │
│  │          │  │  Jose: yeah 3(5)+7=22 👍             │  │
│  │ 🟢 Class │  │                                      │  │
│  │   Space  │  │  ┌──────────────────────────────────┐ │  │
│  │          │  │  │  Type a message...       [📎] 📤 │  │
│  │ 💬 DM    │  │  └──────────────────────────────────┘ │  │
│  │   Hermes │  │                                      │  │
│  └──────────┘  └──────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

| Feature | What it means for your class |
|---------|------------------------------|
| **URL** | `https://app.element.io/` or self-hosted on your server |
| **Setup** | Open browser → type your homeserver address → log in → done |
| **Vibe** | Professional, polished, feature-rich — like Slack/Discord |
| **Room list** | Left sidebar shows all rooms — students click to switch |
| **DMs** | Click a username → DM opens — Hermes tutoring works naturally |
| **Spaces** | Can group all team rooms under a "Mr. Romero's Class" space |
| **👍 for classroom** | Most familiar layout (chat app), everything works |
| **👎 for classroom** | Can feel busy, lots of buttons a 7th grader won't need |

**Best for:** Students who've used Discord/Slack before. Clean pro look.

---

## 2️⃣ Cinny — The Simpler, Cleaner Choice

```
┌──────────────────────────────────────────────────────────┐
│  ←  Team Alpha                               ⬇️ 4 msgs  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  🤖 Hermes Bot                     Today 8:00 AM        │
│  Today's warm-up: Solve for x: 3x + 7 = 22              │
│                                                          │
│  Maria                                  8:01 AM         │
│  x = 5 right?                                            │
│                                                          │
│  Jose                                   8:02 AM          │
│  yeah 3(5)+7=22 👍                                       │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Type a message...                         [➡️]  │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

| Feature | What it means for your class |
|---------|------------------------------|
| **URL** | `https://app.cinny.in/` or self-hosted |
| **Setup** | Open browser → enter homeserver → log in |
| **Vibe** | Minimalist, elegant, modern — like iMessage/WhatsApp Web |
| **Room switching** | Click room name at top, dropdown shows all rooms |
| **Complexity** | Much less cluttered than Element — fewer buttons |
| **👍 for classroom** | Cleanest, most intuitive UI. No overwhelming menus. |
| **👎 for classroom** | Slightly fewer power features (no Spaces explorer, no widgets) |

**Best for:** Middle schoolers who just want to chat. Cleanest experience.

---

## 3️⃣ Hydrogen — The Lightweight Choice

```
┌──────────────────────────────────────────────────────────┐
│  ☰ Team Alpha                               ⋮           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  🤖 Hermes Bot                          08:00           │
│  Solve: 3x + 7 = 22                                     │
│                                                          │
│  Maria                                08:01             │
│  x = 5?                                                  │
│                                                          │
│  Jose                                 08:02             │
│  yeah 👍                                                 │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Message                               [Send]    │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

| Feature | What it means for your class |
|---------|------------------------------|
| **URL** | `https://hydrogen.element.io/` or self-hosted |
| **Setup** | Open browser → enter homeserver → log in |
| **Vibe** | Ultra-minimal, basic, fast — like SMS |
| **Perf** | Tiny bundle, loads instantly even on slow connections |
| **👍 for classroom** | Works on old Chromebooks, slow WiFi, ANY browser |
| **👎 for classroom** | No emoji reactions, no threads, no voice/video, no file preview |

**Best for:** Low-end devices, rural internet, Chromebooks from 2015.

---

## 🏆 Classroom Client Recommendation

For your classroom specifically:

```
                  Complex ←───────→ Simple

    Element Web           Cinny              Hydrogen
    ┌──────────┐     ┌────────────┐     ┌──────────────┐
    │ Slack-ish│     │ WhatsApp-   │     │ SMS-basic    │
    │ Pro feel │     │ ish clean   │     │ Ultra-light  │
    │ Lots of  │     │ Minimal     │     │ No frills    │
    │ features │     │ Just enough │     │ Just text    │
    └──────────┘     └────────────┘     └──────────────┘

    ⭐ RECOMMENDED: Cinny — cleanest for 7th/8th graders
```

### Why Cinny wins for your class:
- **No account needed** — just type your homeserver address and credentials
- **Clean interface** — no distracting buttons, just the conversation
- **Works on any device** — web app, no install
- **E2EE** — all messages encrypted
- **Lightweight** — loads fast on school Chromebooks

### The combo I'd recommend:
- **Homeserver:** Synapse (admin GUI for you)
- **Client:** Cinny (simple for students)
- **Desktop app (optional):** Element Desktop for you as the teacher (more power features)
- **Hermes:** Already supports Matrix, connects to any homeserver

---

## 🔗 Quick Links to Try Right Now

| Client | URL | Open in browser? |
|--------|-----|-----------------|
| **Element Web** | [app.element.io](https://app.element.io/) | ✅ Just works |
| **Cinny** | [app.cinny.in](https://app.cinny.in/) | ✅ Just works |
| **Hydrogen** | [hydrogen.element.io](https://hydrogen.element.io/) | ✅ Just works |

All three let you try them right now against any Matrix homeserver — even the public matrix.org one!
