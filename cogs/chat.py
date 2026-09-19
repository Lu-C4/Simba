import asyncio
import discord
from discord.ext import commands
from collections import deque
from openai import AsyncOpenAI
from agent.agent import agent

from config import (
    logger,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    MODEL_NAME,
    MAX_API_RETRIES,
    MAX_CONTEXT_MESSAGES,
)
from utils.helpers import split_message, format_message_with_reply, get_context


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = AsyncOpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
        )
        self.contexts: dict[int, deque] = {}
        self.chat_active = True
        self.api_lock = asyncio.Lock()
        self.global_active = True
        self.guild_active: dict[int, bool] = {}
        
    def _get_context_key(self, message: discord.Message) -> int:
        if message.guild is None:
            return message.author.id   
        return message.channel.id      

    def is_chat_enabled(self, guild_id: int | None) -> bool:
        if not self.global_active:
            return False

        if guild_id is None:
            print("Got a DM")
            return True  # DMs

        print("Got a DM here")
        return self.guild_active.get(guild_id, True)

    async def handle_ai_chat(self, message: discord.Message):
        if not self.is_chat_enabled(message.guild.id if message.guild else None):
            return

        async with self.api_lock:
            key = self._get_context_key(message)

            context = get_context(
                key,
                self.contexts,
                MAX_CONTEXT_MESSAGES,
            )

            formatted = await format_message_with_reply(message)

            logger.info(f"CH {message.channel.id} | {formatted}")

            # Store the incoming user message
            context.append({
                "role": "user",
                "content": formatted,
            })

            async with message.channel.typing():
                for attempt in range(1, MAX_API_RETRIES + 1):
                    try:
                        # Async LangChain agent invocation
                        result = await agent.ainvoke({
                            "messages": list(context)
                        })

                        # Get the agent's final response
                        final_message = result["messages"][-1]
                        reply = final_message.content

                        # Store only the final assistant response
                        context.append({
                            "role": "assistant",
                            "content": reply,
                        })

                        logger.info(
                            "AI reply | ch=%s | len=%d | preview=%r",
                            message.channel.id if message.guild
                            else f"DM:{message.author.id}",
                            len(reply),
                            reply,
                        )

                        # Send the response to Discord
                        for chunk in split_message(reply):
                            await message.channel.send(chunk)

                        return

                    except Exception:
                        logger.exception(
                            "Agent error attempt %d", attempt
                        )
                        await asyncio.sleep(1.5)

                await message.channel.send(
                    "⚠️ Failed to generate a response."
                )
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return

        if ctx.prefix is not None:
            await message.channel.send("Command not found")
            return

        if (message.channel.id in self.bot.allowed_channels) or message.guild is None:
            await self.handle_ai_chat(message)
        
            