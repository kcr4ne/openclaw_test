import discord
import logging
import asyncio
from typing import Optional
from discord.ext import commands
# In real scenario: from core.agent import HybridAgent

logger = logging.getLogger("jarvis.skill.discord_bot")

class JarvisDiscordBot:
    def __init__(self, token: str, agent: 'HybridAgent'):
        self.token = token
        self.agent = agent
        # Intents needed for reading message content
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = commands.Bot(command_prefix="!", intents=intents)
        
        self.setup_events()

    def setup_events(self):
        @self.client.event
        async def on_ready():
            logger.info(f"Discord Bot connected as {self.client.user}")

        @self.client.event
        async def on_message(message):
            if message.author == self.client.user:
                return

            # Only respond to DMs or mentions for security/noise reduction
            if not (isinstance(message.channel, discord.DMChannel) or self.client.user in message.mentions):
                return

            user_query = message.content.replace(f"<@{self.client.user.id}>", "").strip()
            logger.info(f"Discord command received: {user_query}")
            
            # Use Hybrid Agent to process intent
            # Simplified for PoC - in real app would get context from system
            response = self.agent.process_input("Discord Remote Command", user_query)
            
            reply_text = response.get("reply", "I'm sorry, I couldn't process that.")
            action = response.get("action")
            
            if action:
                # Mock execution result
                reply_text += f"\n✅ Action `{action}` queued."
            
            await message.channel.send(reply_text)

    async def start(self):
        if not self.token:
            logger.warning("No Discord Token provided. Bot disabled.")
            return
        try:
            await self.client.start(self.token)
        except Exception as e:
            logger.error(f"Failed to start Discord Bot: {e}")
            
    async def stop(self):
        await self.client.close()
