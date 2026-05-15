# 🏫 Matrix Classroom AI — Progress Tracker

**Current Phase:** 🔍 Research Complete — External Audit Done — Ready for Compliance + Infrastructure 🚀

---

## 📐 Chosen Stack

| Layer | Choice | Status |
|-------|--------|--------|
| 🏠 Homeserver | **Synapse** | ✅ Running (:8010) |
| 📊 Admin GUI | **Ketesa** | ✅ Running (:8011) |
| 👩‍🎓 Student Client | **Cinny** | ✅ Running (:8012 — via Cloudflare Tunnel) |
| 🔄 Reverse Proxy | **Cloudflare Tunnel** (not Caddy) | ✅ Configured |
| 🤖 **AI Bot** | **Hermes** | ✅ Running (main + classroom-bot profiles) |
| 🧠 **Memory Layer** | **Honcho** (self-hosted) | ✅ Running (:8020) |
| 🛡️ **Moderation Bot** | **Draupnir** | ⏳ Planned (Phase 3) |
| 🏅 Badges | Hermes posts badges (no separate bot) | 🔮 Future |
| 📊 Monitoring | **Uptime Kuma** | ❌ Not deployed |

---

## ✅ Phase 0: Research & Planning — COMPLETE

- [x] Project directory created (`~/projects/matrix-classroom/`)
- [x] `README.md` created
- [x] `TRACKER.md` created
- [x] `plan.md` created with implementation plan
- [x] `comparison.md` — Synapse vs Conduit vs Dendrite deep dive
- [x] `clients.md` — Cinny vs Element
- [x] `feature-ownership.md` — Server vs Client vs Bot feature map
- [x] `claude-feedback.md` — External audit from Claude Code
- [x] Three homeservers researched
- [x] Rocket.Chat researched — NOT Matrix ❌
- [x] Client options researched: Cinny (best for students) ✅
- [x] Moderation bots researched: Draupnir (modern Mjolnir) ✅
- [x] **Decision made:** Synapse + Ketesa + Cinny + Caddy + Hermes + Draupnir 🎯
- [x] External audit by Claude Code — 11 action items added
- [x] Phase order reordered per Claude (moderation before AI)
- [x] E2EE warning documented (disable for classroom rooms)
- [x] Config.yaml channel_prompt updated
- [x] Memory design documented → `memory-architecture.md` (Honcho, replaces Mem0)

---

## 🔒 Phase 0.5: Compliance & Legal (NEW — Claude's #1 recommendation)

- [ ] Research COPPA/FERPA requirements for self-hosted chat + AI
- [ ] Document what data Honcho will store and where (self-hosted PostgreSQL)
- [ ] Determine external vs local LLM provider for Hermes
- [ ] Create parental consent form template
- [ ] Draft data retention/deletion policy
- [ ] Plan student offboarding (end-of-semester)
- [ ] Get district IT approval if needed

---

## 🧱 Phase 1: Infrastructure — Synapse + Ketesa ✅ DONE

- [x] Domain chosen: **class.mr-romero.com** → also serving via **class.epaphrodit.us**
- [x] Docker Compose written (Synapse + PostgreSQL + Ketesa)
- [x] Synapse configured (E2EE allowed, federation off, admin API on)
- [x] E2EE alignment: removed `enable_room_encryption: false`, bot has `MATRIX_ENCRYPTION=true` with fresh crypto store (device `bot3`)
- [x] HTTPS via Cloudflare tunnel
- [x] Admin account: **@admin:class.mr-romero.com**
- [x] Test accounts: **@teststudent1**, **@teststudent2**
- [x] First room: **Team Alpha**
- [x] CLI tool: `deploy/matrix-cli.sh`
- [x] Compliance doc started (parental consent ✅)
- [ ] Version pin Docker images (tech debt)
- [ ] Backups (tech debt)

---

## 👥 Phase 2: Classroom Structure ✅ DONE (pilot)

- [x] Rooms created: **7th Period**, **8th Period**, **Team Alpha**
- [x] 8 test student accounts created
- [x] Students invited to their period rooms
- [x] Student credentials saved: `student-creds.md`
| 👥 User cleanup (test accounts removed) | ✅ Done | 2026-05-13 |
| - [ ] Create whole-class Space "Mr. Romero's Algebra I" (deferred)
- [ ] Set up password reset / account recovery (deferred)
- [ ] Verify team isolation (deferred — test first)

---

## 🛡️ Phase 3: Draupnir Moderation (moved UP per Claude)

- [ ] Deploy Draupnir Docker container
- [ ] Create Draupnir bot account
- [ ] Invite to all team rooms
- [ ] Configure word-filter policy lists (start small)
- [ ] Test auto-kick / censor
- [ ] Tune filter — avoid false positives on slang
- [ ] Set up moderation alert channel (DM)

---

## 🤖 Phase 4: Hermes Bot Integration — DONE ✅

Uses a **separate Hermes profile** for memory isolation. See ADR-001 and ADR-002 in plan.md. Memory via **self-hosted Honcho** per ADR-003.

| Component | Status |
|-----------|--------|
| Profile created (`classroom-bot`) | ✅ Done |
| E2EE dependencies installed | ✅ Done |
| Matrix gateway connected | ✅ Done |
| DMs working (student ↔ Hermes) | ✅ Done |
| E2EE enabled for classroom-bot profile (fresh keys) | ✅ Done |
| Channel prompts & behavior spec | ✅ Done |
| SOUL.md rewritten (calm facilitator) | ✅ Done |
| Room_blocker dm_allowed_users configured | ✅ Done (2026-05-14) |
| Room_blocker admin_users configured (@admin + @bot) | ✅ Done (2026-05-14, @aromero intentionally excluded) |
| Room_blocker module deployed (Synapse custom module) | ✅ Done (2026-05-14) |
| Room_blocker callback registration fixed | ✅ Done (2026-05-14 — was silently not registering callbacks) |
| Room_blocker tested (5/5 scenarios pass) | ✅ Done (2026-05-14) |
| All empty rooms deleted | ✅ Done (2026-05-14) |

| Name: Brittany → Hermes | ✅ Done |
| SOUL.md scenario section added | ✅ Done |
| API keys synced from main profile | ✅ Done |
| Honcho deployed (Cohere embed-v4.0) | ✅ Done | |
| Honcho configured (both profiles) | ✅ Done | 2026-05-13 |
| Honcho DNS fix (localhost→127.0.0.1) | ✅ Done | 2026-05-13 |
| Honcho dialectic fixed (env vars + API key + model) | ✅ Done | 2026-05-13 |
| User cleanup (test accounts removed) | ✅ Done | 2026-05-13 |
| Honcho peers synced | ⏳ Pending |
| Per-student memory verified | ⏳ Pending |
| Warm-up via cron | ⏳ Pending |
| Participation tracking | ⏳ Pending |

### Hook + Plugin Architecture (2026-05-15) ✅
| Component | Status |
|-----------|--------|
| `!here`/`!roll` gateway hook (`classroom-attendance`) | ✅ Done — deterministic check-in + warm-up DM |
| DM room auto-creation on `!here` | ✅ Done — fire-and-forget via Matrix API |
| Bell Ringer problem pool (4 problems, TEKS 8.5A–8.5I) | ✅ Done — deterministic per-student/day rotation |
| Active warmup context seeding (`active_warmups.json`) | ✅ Done — send-and-seed pattern (ADR-004) |
| `matrix-warmup-context` plugin (`pre_llm_call` hook) | ✅ Done — injects warm-up context before every LLM call |
| Warm-up greeting (no raw username) | ✅ Done — "Hey there!" generic greeting |
| Attendance clearing/reset | ✅ Done — CLI-cleanable state files |

### Bug Fixes (2026-05-15)
| Bug | Root Cause | Fix |
|-----|-----------|-----|
| Context injection never fired | Plugin looked for `user_id` kwarg, gateway passes `sender_id` | Changed to `sender_id` with `user_id` fallback |
| Context file not found | Plugin used profile-scoped `HERMES_HOME`, hook hardcoded `~/.hermes` | Both now use `Path.home() / ".hermes"` |
| LLM hallucinated student name | Greeting used ugly username, context had no identity info | Generic greeting + user_id in context |
| `!here` ignored by bot | `require_mention: true` | Set to `false` |
| Config pointed to deleted rooms | Old room IDs from deleted test rooms | Updated to current Playground room |

---

## 🔊 Phase 5: Teacher Dashboard (NEW per Claude)

- [ ] Design dashboard views (participation, moderation, warm-up responses)
- [ ] Determine data source (Honcho queries / logs)
- [ ] Build simple web view or report script

---

## 🏅 Phase 6: Badges & Gamification

- [ ] Design badge system (via Hermes, no separate bot)
- [ ] Implement Hermes-based badge announcements

---

## 💭 Future / Out of Scope

- [ ] Grading integration (Google Classroom)
- [ ] SSO / Google login (manual accounts via Ketesa is fine)
- [ ] Mobile apps (Cinny web works everywhere)
- [ ] Federation with other Matrix servers
