import httpx
from langchain.tools import tool
@tool
def getUserData(username:str):
    """
    Returns data about a user from 
    the official ev.io game's endpoint.
    It has data related to player's kills,
    account creation date and time, last seen
    date and time, skins, crosshairs etc.,
    
    """
    
    with httpx.Client() as client:
        response = client.get(f"https://ev.io/stats-by-un/{username}", timeout=30)
        if response.status_code != 200:
            return "Server returned an error, could be due to a wrong username!"
        data = response.json()
        
        # Ignore achievements as it's unreadable and a huge chunk of useless text
        data[0]['field_field_achievements']=[]
        
        return data[0] if data else data

async def getClanData(UID=903):
    async with httpx.AsyncClient() as client:
        data= (await client.get(f"https://ev.io/group/{UID}?_format=json"))
    return data.json()

