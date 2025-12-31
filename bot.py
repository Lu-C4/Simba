import os
import sys
import logging
import discord
import asyncio
from collections import deque
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Local import
from system_prompt import system_prompt

# -------------------------------
# INITIALIZATION & CONFIG
# -------------------------------
load_dotenv()

LOG_FILE = "simba.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("Simba")

# Environment Variables
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

def parse_env_list(key: str) -> list[int]:
    val = os.getenv(key, "")
    return [int(i.strip()) for i in val.split(",") if i.strip().isdigit()]

ALLOWED_CHANNEL_IDS = parse_env_list("ALLOWED_CHANNEL_IDS")
ADMIN_ROLE_IDS = parse_env_list("ADMIN_ROLE_IDS")

MAX_CONTEXT_MESSAGES = 50
MAX_DISCORD_CHARS = 2000
MAX_API_RETRIES = 3
CHAT_ACTIVE = True

# Ensures only one AI request is processed at a time
api_lock = asyncio.Lock()

# -------------------------------
# CLIENT SETUP
# -------------------------------
client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
)

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

channel_contexts: dict[int, deque] = {}

# -------------------------------
# HELPERS
# -------------------------------

def get_context(channel_id: int) -> deque:
    if channel_id not in channel_contexts:
        channel_contexts[channel_id] = deque(
            system_prompt,
            maxlen=MAX_CONTEXT_MESSAGES,
        )
    return channel_contexts[channel_id]

def is_admin(member: discord.Member) -> bool:
    if not isinstance(member, discord.Member):
        return False
    return any(role.id in ADMIN_ROLE_IDS for role in member.roles)

async def format_message_with_reply(message: discord.Message) -> str:
    username = message.author.display_name

    if message.reference and isinstance(message.reference.resolved, discord.Message):
        replied = message.reference.resolved
        return (
            f"{username} (replying to {replied.author.display_name}): "
            f"{replied.content}\n→ {message.content}"
        )

    return f"{username}: {message.content}"

def split_message(text: str, limit: int = MAX_DISCORD_CHARS) -> list[str]:
    """
    Splits text into chunks <= limit characters
    """
    return [text[i:i + limit] for i in range(0, len(text), limit)]

# -------------------------------
# CORE LOGIC
# -------------------------------

async def handel_ai_chat(message: discord.Message):
    """
    Main orchestrator for AI interactions and admin commands.
    """
    global CHAT_ACTIVE

    # 1. Handle Admin Commands
    if message.content.startswith("!"):
        if not is_admin(message.author):
            await message.channel.send(
                "❌ Only Moderators are allowed to run commands!"
            )
            return

        reply = ""
        if message.content == "!clearcontext":
            channel_contexts.clear()
            reply = "🧠 Context cleared. I’ve forgotten everything."
        elif message.content == "!deactivate":
            CHAT_ACTIVE = False
            reply = "🔕 Chat deactivated."
        elif message.content == "!activate":
            CHAT_ACTIVE = True
            reply = "🔔 Chat activated. I’m listening again."

        if reply:
            logger.info(
                f"Admin Command: {message.content} | Response: {reply}"
            )
            await message.channel.send(reply)

        return

    # 2. Check Global Toggle
    if not CHAT_ACTIVE:
        return

    # 3. Process AI Response (FIFO via Lock)
    async with api_lock:
        context = get_context(message.channel.id)
        formatted_content = await format_message_with_reply(message)

        logger.info(
            f"CH {message.channel.id} | Processing: {formatted_content}"
        )

        # Store user message
        context.append({
            "role": "user",
            "content": formatted_content,
        })

        async with message.channel.typing():
            last_exception = None

            for attempt in range(1, MAX_API_RETRIES + 1):
                try:
                    logger.info(f"OpenAI attempt {attempt}/3")

                    response = await client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=list(context),
                        temperature=0.7,
                        max_tokens=600,  # ~2000 chars
                    )

                    reply_text = response.choices[0].message.content.strip()

                    # Store assistant response in context
                    context.append({
                        "role": "assistant",
                        "content": f"{bot.user.name}: {reply_text}",
                    })

                    # Split and send safely
                    chunks = split_message(reply_text)

                    for chunk in chunks:
                        await message.channel.send(chunk)

                    logger.info("AI response sent successfully")
                    return

                except Exception as e:
                    
                    logger.exception(
                        f"OpenAI error on attempt {attempt}"
                        f"\n\n{e}\n\n"
                    )
                    await asyncio.sleep(1.5)  # small backoff

            
            logger.error("All OpenAI retries failed")
            await message.channel.send(
                "⚠️ Failed to generate a response after multiple attempts."
            )

# -------------------------------
# EVENTS
# -------------------------------

@bot.event
async def on_ready():
    logger.info(
        f"✅ Logged in as {bot.user} ({bot.user.id})"
    )

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.channel.id in ALLOWED_CHANNEL_IDS:
        return await handel_ai_chat(message)

    return None

# -------------------------------
# ENTRY POINT
# -------------------------------

if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        logger.critical(
            "No DISCORD_BOT_TOKEN found in environment variables."
        )
        sys.exit(1)

    bot.run(DISCORD_BOT_TOKEN)
