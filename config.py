import os
import sys
import logging
from dotenv import load_dotenv

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


def parse_env_list(key: str) -> list[int]:
    val = os.getenv(key, "")
    return [int(i.strip()) for i in val.split(",") if i.strip().isdigit()]


# Environment variables
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME", "cosmosrp-2.5")

ALLOWED_CHANNEL_IDS = parse_env_list("ALLOWED_CHANNEL_IDS")
ADMIN_ROLE_IDS = parse_env_list("ADMIN_ROLE_IDS")

MAX_CONTEXT_MESSAGES = 50
MAX_DISCORD_CHARS = 2000
MAX_API_RETRIES = 3


ALLOWED_MODELS=[
    "gpt-oss-20b",
    "cosmosrp-2.1",
    "cosmosrp-2.5"
]