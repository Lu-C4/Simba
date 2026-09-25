import httpx
from langchain.tools import tool
import cloudscraper
import random
import json
import asyncio
import re

BUNDLE_URL = "https://ev.io/dist/1-7-0/public/bundle.js"

def get_count(url: str) -> str:
    """Fetch the current player count for a lobby."""
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(
            f"{url}players{random.random()}",
            timeout=5,
        )

        return str(json.loads(response.text)["playerCount"])

    except Exception:
        return "N/A"

@tool
async def fetch_lobby_links():
    """
    Fetch active lobbies and their player counts.

    Returns:
        List of dictionaries containing:
        region, url, player_count, id, gamemode
    """

    BUNDLE_URL = "https://ev.io/dist/1-7-0/public/bundle.js"

    # ---------------------------
    # Fetch lobby list
    # ---------------------------

    async with httpx.AsyncClient() as client:
        r = await client.get(BUNDLE_URL)

    match = re.search(
        r'(\[\s*\{"id":"lobby-.*?\}\s*\])',
        r.text,
        re.DOTALL
    )

    if not match:
        return []

    data = json.loads(match.group(1))

    # ---------------------------
    # Prepare connection URLs
    # ---------------------------

    connection_urls = [
        game["connectionUrl"].replace("wss", "https")
        for game in data
    ]

    # ---------------------------
    # Fetch player counts
    # ---------------------------

    semaphore = asyncio.Semaphore(16)

    async def fetch_count(url):
        async with semaphore:
            return await asyncio.to_thread(
                get_count,
                url
            )

    counts = await asyncio.gather(
        *(fetch_count(url) for url in connection_urls)
    )

    # ---------------------------
    # Return lobby information
    # ---------------------------

    return [
        {
            "region": game["region"],
            "url": f"https://ev.io/?game={game['id']}",
            "player_count": count,
            "id": game["id"],
            "gamemode": game["gamemode"],
        }
        for game, count in zip(data, counts)
    ]
   
@tool
def getUserData(username:str):
    """
    Returns data about a user from 
    the official ev.io game's endpoint.
    It has data related to player's kills,
    account creation date and time, last seen
    date and time, skins, crosshairs etc.,
    
    """
    
    try:
            with httpx.Client(timeout=30) as client:
                response = client.get(f"https://ev.io/stats-by-un/{username}")
                response.raise_for_status()

                try:
                    data = response.json()
                except ValueError:
                    return "Server returned invalid JSON."

    except httpx.TimeoutException:
        return "Request timed out while contacting the server."

    except httpx.HTTPStatusError as e:
        return f"Server returned HTTP {e.response.status_code}."

    except httpx.RequestError:
        return "Could not connect to the server."

    # Validate the JSON structure
    if not isinstance(data, list):
        return "Server returned an unexpected response format."

    if not data:
        return "No player data found."

    player = data[0]

    if not isinstance(player, dict):
        return "Server returned invalid player data."

    # Remove achievements safely
    player["field_field_achievements"] = []

    return player

