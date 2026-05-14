"""
Room Creation Blocker — Synapse custom module

Blocks room creation for non-admin users, except for DMs with allowed bots.

Config (in homeserver.yaml):
    modules:
      - module: room_blocker.RoomCreationBlocker
        config:
          admin_users:
            - "@admin:class.mr-romero.com"
            # Users listed here can create any rooms/spaces.
            # Synapse server admins (admin: true) auto-bypass the spam
            # check entirely — this list is for non-admin users who
            # should be allowed to create rooms (e.g., bot accounts).
          dm_allowed_users:
            - "@bot:class.mr-romero.com"
            # Users listed here can receive DMs from non-admin users.
            # When a non-admin creates a room inviting ONLY users from
            # this list, the creation is treated as a DM and allowed.
"""

import logging
from typing import Optional

from synapse.api.errors import Codes
from synapse.module_api import ModuleApi, NOT_SPAM

logger = logging.getLogger(__name__)


class RoomCreationBlocker:
    def __init__(self, config: dict, api: ModuleApi) -> None:
        self._api = api
        self._admin_users = set(config.get("admin_users", []))
        self._dm_allowed_users = set(config.get("dm_allowed_users", []))

        # Register spam checker callbacks — WITHOUT THIS, SYNAPSE NEVER CALLS THEM
        api.register_spam_checker_callbacks(
            user_may_create_room=self.user_may_create_room,
            user_may_invite=self.user_may_invite,
        )

        logger.info(
            "RoomCreationBlocker loaded: %d admin_users, %d dm_allowed_users",
            len(self._admin_users),
            len(self._dm_allowed_users),
        )

    @staticmethod
    def parse_config(config: dict) -> dict:
        if not isinstance(config, dict):
            raise ValueError("config must be a dict")
        if "admin_users" not in config:
            raise ValueError("config must contain 'admin_users' list")
        if "dm_allowed_users" not in config:
            raise ValueError("config must contain 'dm_allowed_users' list")
        return config

    async def user_may_create_room(
        self,
        user_id: str,
        room_creation_config: Optional[dict] = None,
    ):
        """Check if a user may create a room.

        Returns NOT_SPAM (allowed) if:
          - The user is in `admin_users`, OR
          - The room is created as a DM inviting ONLY dm_allowed_users

        Returns Codes.FORBIDDEN (blocked) otherwise.

        Note: Synapse server admins (admin: true) bypass this callback
        entirely — the check is skipped at the handler level before
        the module is called.
        """
        # ── Admin users (from config) can always create rooms ────────────
        if user_id in self._admin_users:
            return NOT_SPAM

        # ── Check if this is a DM/conversation with an allowed bot ──────
        # Two scenarios:
        #   1. Client set is_direct: true and invites only dm_allowed_users
        #   2. Client invites only dm_allowed_users (some clients skip
        #      is_direct, but the intents is clearly a DM/conversation)
        if room_creation_config is not None:
            invites = room_creation_config.get("invite", [])

            if isinstance(invites, list) and len(invites) > 0:
                # Convert invites to set for easy comparison
                invite_set = set(invites)

                # ALL invitees must be dm_allowed_users — no sneaking
                # additional students into the room
                if invite_set.issubset(self._dm_allowed_users):
                    return NOT_SPAM

        # ── Everyone else is blocked ────────────────────────────────────
        return Codes.FORBIDDEN

    async def user_may_invite(
        self,
        inviter_userid: str,
        invitee_userid: str,
        room_id: str,  # pylint: disable=unused-argument
    ):
        """Check if a user may invite another user to a room.

        Returns NOT_SPAM if:
          - The inviter is in admin_users, OR
          - The invitee is in dm_allowed_users (e.g., inviting @bot)

        Returns Codes.FORBIDDEN otherwise.
        """
        # Admin users (from config) can invite anyone
        if inviter_userid in self._admin_users:
            return NOT_SPAM

        # Anyone can invite dm_allowed_users (e.g., students DMing @bot)
        if invitee_userid in self._dm_allowed_users:
            return NOT_SPAM

        # Block everything else (students can't invite each other)
        return Codes.FORBIDDEN
