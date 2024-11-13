# bot.py
import discord
import json

class DiscordBot:
    """Handles all interactions with the Discord API."""
    def __init__(self, token, gui):
        self.client = None
        self.token = token
        self.gui = gui
        self.channel_ids = [None] * 5
        self.channel_names = ["Unknown"] * 5

    def setup_client(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.moderation = True
        intents.message_content = True
        self.client = discord.Client(intents=intents)

        @self.client.event
        async def on_ready():
            self.gui.status_updated.emit(f"Logged in as {self.client.user}")
            await self.update_channel_names()

        return self.client

    async def update_channel_names(self):
        for i, channel_id in enumerate(self.channel_ids):
            if channel_id:
                try:
                    channel = await self.client.fetch_channel(int(channel_id))
                    self.channel_names[i] = channel.name
                    self.gui.channel_name_updated.emit(i, channel.name)
                except:
                    pass

    async def send_message_async(self, message, channel_id):
        channel = self.client.get_channel(int(channel_id))
        if channel:
            await channel.send(message)
            self.gui.status_updated.emit("Message sent!")
        else:
            self.gui.status_updated.emit(f"Channel with ID {channel_id} not found.")
