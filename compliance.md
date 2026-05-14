# 📋 Compliance Documentation — Matrix Classroom AI

## Parental Consent Status

| Item | Status | Date |
|------|--------|------|
| **Parental permission obtained** | ✅ **YES** | 2026-05-12 |
| Consent method | Verbal/granted via Abraham | 2026-05-12 |
| Documentation | Parental consent forms on file (Abraham maintains) | 2026-05-12 |
| COPPA compliance | ✅ Cleared — consent obtained | 2026-05-12 |
| FERPA compliance | ⚠️ Data retention policy needed (in progress) | 2026-05-12 |

## Data Handling

- **Storage**: All student data remains on Abraham's private server (self-hosted PostgreSQL + Honcho API)
- **External APIs**: 
  - Hermes calls LLM providers (OpenCode Go + kimi-k2.6) — student conversations processed externally
  - Honcho embeddings via Cohere API (embed-v4.0) — message content sent for embedding
- **Retention**: Student accounts/messages will be deleted at end of semester
- **Right to be forgotten**: Parents can request data deletion at any time
- **Discord conversations**: Also stored in Honcho workspace `hermes-main` (Abraham's personal assistant data only)

## Memory Isolation

Student conversations are handled by a **separate Hermes profile** (`classroom-bot`), not the main assistant profile.

- **Student memory lives at** Honcho workspace `vanguard-25_26-7th` — per-student peer models
- **Main profile memory** at Honcho workspace `hermes-main` — Abraham's personal assistant data
- **Both served by** self-hosted Honcho API on local Docker (same server, separate workspaces)
- **No cross-profile contamination** — Honcho's workspace isolation prevents any data leakage
- **Right to be forgotten** — delete the Honcho workspace via API or wipe the Honcho database
- **End-of-semester offboarding** — delete workspace `vanguard-25_26-7th`, recreate next semester

## Policy Notes

**To fully close compliance (Claude Code recommendation, see `claude-feedback.md`):**
1. [x] Document what data Honcho stores and where → **Self-hosted PostgreSQL on private server** (see `memory-architecture.md`)
2. [ ] Create data retention/deletion policy document
3. [x] Determine if Hermes calls external or local LLM → **OpenCode Go + kimi-k2.6 (external API)**, Cohere embeddings (external API)
4. [ ] Plan end-of-semester student offboarding → **Delete Honcho workspace** (pending documented procedure)
5. [ ] Document all of this for district IT if requested

---

*This file exists to track compliance items. Abraham maintains the actual consent forms.*
