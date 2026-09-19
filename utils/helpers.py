import discord
from collections import deque
from config import MAX_DISCORD_CHARS, ADMIN_ROLE_IDS


def split_message(text: str, limit: int = MAX_DISCORD_CHARS) -> list[str]:
    return [text[i:i + limit] for i in range(0, len(text), limit)]


async def format_message_with_reply(message: discord.Message) -> str:
    username = message.author.display_name

    if message.reference and isinstance(message.reference.resolved, discord.Message):
        replied = message.reference.resolved
        return (
            f"{username} (replying to {replied.author.display_name}): "
            f"{replied.content}\n→ {message.content}"
        )

    return f"{username}: {message.content}"


def is_admin(member: discord.Member) -> bool:
    if not isinstance(member, discord.Member):
        return False
    return any(role.id in ADMIN_ROLE_IDS for role in member.roles)


def get_context(channel_id: int, contexts: dict, max_len: int) -> deque:
    if channel_id not in contexts:
        contexts[channel_id] = deque(maxlen=max_len)
    return contexts[channel_id]
