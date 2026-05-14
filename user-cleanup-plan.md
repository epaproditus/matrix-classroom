# 🧹 Matrix User Cleanup Plan

**Date:** 2026-05-13
**Context:** We're moving from pre-SSO test accounts to the real Google SSO setup. Most student accounts were test data and need to go. Only real users stay.

---

## Current Users (13 total)

| # | User | Type | Display Name | Keep? | Why |
|---|------|------|-------------|-------|-----|
| 1 | **@admin** | admin | — | ✅ **KEEP** | Abraham (server admin) |
| 2 | **@aromero** | support | — | ✅ **KEEP** | Abraham (teacher) |
| 3 | **@hermes** | bot | "Hermes AI Assistant" | ✅ **KEEP** | Main Hermes profile (me!) |
| 4 | **@bot** | bot | "Hermes" | ✅ **KEEP** | Classroom bot profile connects as @bot |
| 5 | ~~@classroom-bot~~ | bot | "Brittany 🤖" | ❌ **REMOVE** | Unused old account, not connected to any profile |
| 6 | @alekk | support | — | ❌ REMOVE | Test student |
| 7 | @annette | support | — | ❌ REMOVE | Test student |
| 8 | @emma | support | — | ❌ REMOVE | Test student |
| 9 | @fernanda | support | — | ❌ REMOVE | Test student |
| 10 | @jacklynn | support | — | ❌ REMOVE | Test student |
| 11 | @josue | support | — | ❌ REMOVE | Test student |
| 12 | @leo | support | — | ❌ REMOVE | Test student |
| 13 | @maria | support | — | ❌ REMOVE | Test student |

## Summary

| Action | Count |
|--------|-------|
| ✅ Keep | **4** (admin, aromero, hermes, bot) |
| ❌ Remove | **9** (8 test students + @classroom-bot) |

## Removal Method

Use Synapse admin API: `POST /_synapse/admin/v1/deactivate/<user_id>`
This kicks users from all rooms and marks them deactivated.
Accounts can be reactivated if needed (soft deactivation).

## Next Steps After Removal

1. Update SNAPSHOT.md, TRACKER.md, student-creds.md
2. Clean up empty rooms (#team-7-1, #team-7-2, #team-7-3)
3. Rebuild with real SSO students when ready
