#!/usr/bin/env bash
# ──────────────────────────────────────────────
# Matrix Classroom — CLI Room Management Tool
# Usage: ./matrix-cli.sh <command> [args...]
# ──────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/.admin-token.env" 2>/dev/null || {
  echo "❌ No .admin-token.env found. Run: get-admin-token"
  exit 1
}
SYNAPSE_URL="http://localhost:8010"
HOMESERVER="class.mr-romero.com"

case "${1:-help}" in

  # ── Users ─────────────────────────────────
  create-user)
    USERNAME="$2"
    PASSWORD="${3:-changeme}"
    echo "👤 Creating user $USERNAME..."
    curl -s -X PUT "$SYNAPSE_URL/_synapse/admin/v2/users/@$USERNAME:$HOMESERVER" \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"password\":\"$PASSWORD\",\"displayname\":\"$USERNAME\",\"admin\":false}" \
      | python3 -c "import json,sys; d=json.load(sys.stdin); print('✅ Created @$USERNAME:$HOMESERVER' if d.get('name') else '❌ '+d.get('error','unknown'))"
    ;;

  create-admin)
    USERNAME="$2"
    PASSWORD="${3:-changeme}"
    echo "👑 Creating admin $USERNAME..."
    curl -s -X PUT "$SYNAPSE_URL/_synapse/admin/v2/users/@$USERNAME:$HOMESERVER" \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"password\":\"$PASSWORD\",\"displayname\":\"$USERNAME\",\"admin\":true}" \
      | python3 -c "import json,sys; d=json.load(sys.stdin); print('✅ Created admin @$USERNAME:$HOMESERVER' if d.get('name') else '❌ '+d.get('error','unknown'))"
    ;;

  list-users)
    echo "👥 Users:"
    curl -s "$SYNAPSE_URL/_synapse/admin/v2/users?limit=100" \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      | python3 -c "
import json,sys
d=json.load(sys.stdin)
for u in d.get('users',[]):
    name = u['name'].lstrip('@')
    admin = '👑' if u.get('admin') else '  '
    print(f' {admin} @{name}')
print(f'\nTotal: {len(d.get(\"users\",[]))} users')
"
    ;;

  reset-password)
    USERNAME="$2"
    PASSWORD="${3:-changeme}"
    echo "🔑 Resetting password for $USERNAME..."
    curl -s -X POST "$SYNAPSE_URL/_synapse/admin/v1/reset_password/@$USERNAME:$HOMESERVER" \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"new_password\":\"$PASSWORD\"}" \
      | python3 -c "import json,sys; d=json.load(sys.stdin); print('✅ Password reset' if d == {} else '❌ '+d.get('error','unknown'))"
    ;;

  deactivate-user)
    USERNAME="$2"
    echo "🗑️ Deactivating $USERNAME..."
    curl -s -X POST "$SYNAPSE_URL/_synapse/admin/v1/deactivate/@$USERNAME:$HOMESERVER" \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{}' > /dev/null
    echo "✅ $USERNAME deactivated"
    ;;

  # ── Rooms ─────────────────────────────────
  create-room)
    NAME="$2"
    ALIAS="${3:-$2}"
    echo "🏠 Creating room \"$NAME\"..."
    curl -s -X POST "$SYNAPSE_URL/_matrix/client/r0/createRoom" \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"name\":\"$NAME\",\"room_alias_name\":\"$ALIAS\",\"preset\":\"public_chat\",\"initial_state\":[{\"type\":\"m.room.encryption\",\"state_key\":\"\",\"content\":{\"algorithm\":null}}]}" \
      | python3 -c "import json,sys; d=json.load(sys.stdin); print('✅ Created! Room ID: '+d.get('room_id','❌ '+d.get('error','unknown')))"
    ;;

  list-rooms)
    echo "🏠 Rooms:"
    curl -s "$SYNAPSE_URL/_synapse/admin/v1/rooms?limit=50" \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      | python3 -c "
import json,sys
d=json.load(sys.stdin)
for r in d.get('rooms',[]):
    enc = '🔒' if r.get('encryption') else '  '
    name = r.get('name') or r.get('room_id','?')[:20]
    print(f' {enc} {name}  [{r[\"room_id\"][:12]}...]')
print(f'\nTotal: {len(d.get(\"rooms\",[]))} rooms')
"
    ;;

  # ── Invites ───────────────────────────────
  invite)
    ROOM_ID="$2"
    USERNAME="$3"
    echo "📨 Inviting @$USERNAME:$HOMESERVER to room $ROOM_ID..."
    curl -s -X POST "$SYNAPSE_URL/_matrix/client/r0/rooms/$ROOM_ID/invite" \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"user_id\":\"@$USERNAME:$HOMESERVER\"}" \
      | python3 -c "import json,sys; d=json.load(sys.stdin); print('✅ Invited' if d == {} else '❌ '+d.get('error','unknown'))"
    ;;

  # ── Batch: Create team ────────────────────
  create-team)
    TEAM_NAME="$2"
    shift 2
    echo "🏗️  Creating team \"$TEAM_NAME\" with members: $@"
    
    # Create the room
    ROOM_RESP=$(curl -s -X POST "$SYNAPSE_URL/_matrix/client/r0/createRoom" \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"name\":\"$TEAM_NAME\",\"room_alias_name\":\"team-$TEAM_NAME\",\"preset\":\"public_chat\",\"initial_state\":[{\"type\":\"m.room.encryption\",\"state_key\":\"\",\"content\":{\"algorithm\":null}}]}")
    ROOM_ID=$(echo "$ROOM_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('room_id','ERROR'))")
    
    if [ "$ROOM_ID" = "ERROR" ]; then
      echo "❌ Failed to create room"
      exit 1
    fi
    echo "✅ Room created: $TEAM_NAME"
    
    # Invite each member
    for USER in "$@"; do
      curl -s -X POST "$SYNAPSE_URL/_matrix/client/r0/rooms/$ROOM_ID/invite" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"user_id\":\"@$USER:$HOMESERVER\"}" > /dev/null
      echo "   📨 Invited @$USER"
    done
    echo "🎉 Team $TEAM_NAME ready!"
    ;;

  # ── Help ──────────────────────────────────
  *)
    echo "Matrix Classroom CLI"
    echo "────────────────────"
    echo "Users:"
    echo "  create-user <name> [password]    Create a student account"
    echo "  create-admin <name> [password]   Create an admin account"
    echo "  list-users                       List all users"
    echo "  reset-password <name> [pass]     Reset a user's password"
    echo "  deactivate-user <name>           Deactivate a user"
    echo ""
    echo "Rooms:"
    echo "  create-room <name> [alias]       Create a room (E2EE OFF)"
    echo "  list-rooms                       List all rooms"
    echo "  invite <room_id> <username>      Invite user to room"
    echo ""
    echo "Batch:"
    echo "  create-team <name> <user1> [user2...]  Create room + invite all"
    echo ""
    echo "Examples:"
    echo "  ./matrix-cli.sh create-user jose"
    echo "  ./matrix-cli.sh create-room \"Team Alpha\" team-alpha"
    echo "  ./matrix-cli.sh create-team \"Team Beta\" maria jose sara"
    ;;
esac
