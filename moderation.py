# moderation.py
import datetime

class ModerationActions:
    """Handles user moderation actions like kick, ban, and timeout."""
    def __init__(self, bot):
        self.bot = bot

    async def kick_user(self, user_id):
        await self._moderation_action(user_id, "kick")

    async def ban_user(self, user_id):
        await self._moderation_action(user_id, "ban")

    async def timeout_user(self, user_id, timeout_duration=5):
        await self._moderation_action(user_id, "timeout", timeout_duration)

    async def _moderation_action(self, user_id, action, duration=None):
        channel = self.bot.client.get_channel(int(self.bot.channel_ids[self.bot.gui.current_channel]))
        guild = channel.guild
        member = await guild.fetch_member(int(user_id))
        try:
            if action == "kick":
                await member.kick()
                self.bot.gui.status_updated.emit(f"User {user_id} kicked successfully")
            elif action == "ban":
                await member.ban()
                self.bot.gui.status_updated.emit(f"User {user_id} banned successfully")
            elif action == "timeout":
                await member.timeout(datetime.timedelta(minutes=duration))
                self.bot.gui.status_updated.emit(f"User {user_id} timed out successfully")
        except Exception as e:
            self.bot.gui.status_updated.emit(f"Failed to {action} user: {str(e)}")
