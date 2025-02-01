import discord
from discord.ext import commands
import requests
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True

bot=commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree
def getUserData(username):
    data=requests.get(f"https://ev.io/stats-by-un/{username}").json()
    if not len(data):
        return None
    return data[0]


@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}!")
    try:
        # Sync commands with Discord
        await tree.sync()
        print("Slash commands synced!")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@tree.command(name="greet", description="Greet someone.")
async def greet(interaction: discord.Interaction, name: str):
    """Sends a personalized greeting."""
    await interaction.response.send_message(f"Hello, {name}! 👋")


@tree.command(name="checkplayerstats", description="Display the stats of a player from a Username.")
async def checkplayerstats(interaction: discord.Interaction, username: str):
    data=getUserData(username)
    if not data:
        await interaction.response.send_message("Player not found\n*Roars*")
        return


    skin_data=requests.get(f'https://ev.io/node/{data["field_eq_skin"][0]["target_id"]}?_format=json').json()
    
    
    image=discord.Embed(color=discord.Color.yellow())
    image.add_field(name="Username", value=data["name"][0]["value"] + "\n", inline=False)
    image.set_image(url=skin_data["field_large_thumb"][0]["url"])
    image.set_thumbnail(url=skin_data["field_profile_thumb"][0]["url"])
    
    stats=discord.Embed(color=discord.Color.yellow())
    stats.add_field(name="Kills", value=data["field_kills"][0]["value"], inline=False)
    stats.add_field(name="Deaths", value=data["field_deaths"][0]["value"], inline=False)
    stats.add_field(name="K/D", value=data["field_k_d"][0]["value"], inline=False)
    stats.add_field(name="Kills Per Game", value=round(data["field_kills"][0]["value"] / data["field_total_games"][0]["value"],2), inline=False)
    

    #DATE CREATED AND NUMBER OF DAYS PASSED SINCE
    datetime_string = data["created"][0]["value"]
    parsed_datetime = datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S%z')
    current_datetime = datetime.now(parsed_datetime.tzinfo)  # Use the same timezone as parsed_datetime
    days_past = (current_datetime - parsed_datetime).days
    formatted_date = parsed_datetime.strftime('%d/%m/%Y')
    stats.add_field(name="Date of account creation", value=formatted_date, inline=False)
    stats.add_field(name="Days past", value=days_past, inline=False)

    await interaction.response.send_message(embeds=[image,stats])
    
@tree.command(name="getcrosshair", description="Get the crosshair of a user from username")
async def crosshair(interaction: discord.Interaction, username: str):
    data=getUserData(username)
    if not data:
        await interaction.response.send_message("Player not found\n*Roars*")
        return
    crosshair=discord.Embed(color=discord.Color.yellow())
    crosshair.set_image(url=data["field_custom_crosshair"][0]["url"])
    await interaction.response.send_message("*Roars*", embed=crosshair)

@tree.command(name="peekskins", description="Checkout the skins equipped by players.")
async def peek(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
 

    data=getUserData(username)
    if not data:
        await interaction.response.send_message(content="Player not found\n*Roars*")
        return
    

    AssaultRifle=discord.Embed(description=f'[Assault Rifle](https://ev.io{data["field_auto_rifle_skin"][0]["url"]})',color=discord.Color.yellow())
    AssaultRifle.set_image(url=requests.get(f'https://ev.io{data["field_auto_rifle_skin"][0]["url"]}?_format=json').json()["field_weapon_skin_thumb"][0]["url"])

    LaserRifle=discord.Embed(description=f'[Laser Rifle](https://ev.io{data["field_laser_rifle_skin"][0]["url"]})',color=discord.Color.yellow())
    LaserRifle.set_image(url=requests.get(f'https://ev.io{data["field_laser_rifle_skin"][0]["url"]}?_format=json').json()["field_weapon_skin_thumb"][0]["url"])

    Sweeper=discord.Embed(description=f'[Sweeper](https://ev.io{data["field_sweeper_skin"][0]["url"]}?_format=json)',color=discord.Color.yellow())
    Sweeper.set_image(url=requests.get(f'https://ev.io{data["field_sweeper_skin"][0]["url"]}?_format=json').json()["field_weapon_skin_thumb"][0]["url"])

    BurstRifle=discord.Embed(description=f'[Burst Rifle](https://ev.io{data["field_burst_rifle_skin"][0]["url"]})',color=discord.Color.yellow())
    BurstRifle.set_image(url=requests.get(f'https://ev.io{data["field_burst_rifle_skin"][0]["url"]}?_format=json').json()["field_weapon_skin_thumb"][0]["url"])

    HandCannon=discord.Embed(description=f'[Hand Cannon](https://ev.io{data["field_hand_cannon_skin"][0]["url"]})',color=discord.Color.yellow())
    HandCannon.set_image(url=requests.get(f'https://ev.io{data["field_hand_cannon_skin"][0]["url"]}?_format=json').json()["field_weapon_skin_thumb"][0]["url"])

    Sword=discord.Embed(description=f'[Sword](https://ev.io{data["field_sword_skin"][0]["url"]})',color=discord.Color.yellow())
    Sword.set_image(url=requests.get(f'https://ev.io{data["field_sword_skin"][0]["url"]}?_format=json').json()["field_weapon_skin_thumb"][0]["url"])


    await interaction.followup.send(embeds=[AssaultRifle,LaserRifle,Sweeper,BurstRifle,HandCannon,Sword])

@tree.command(name="survivalscores", description="Get Survival highscores of a player by map")
async def survival(interaction: discord.Interaction, username: str):
    data=getUserData(username)
    if not data:
        await interaction.response.send_message("Player not found\n*Roars*")
        return
    data['field_survival_high_scores'][0]['value'].pop('caption')
    data['field_survival_high_scores'][0]['value'].pop('0')
    
    sstat=discord.Embed(color=discord.Color.yellow())
    for value in data['field_survival_high_scores'][0]['value'].values():
        sstat.add_field(name=value[0], value=value[1], inline=True)
    await interaction.response.send_message( embed=sstat)
   

bot.run("MTMzNDUzOTM1MDQ1MjYwNDk1OQ.G1Qnix.PNO0mIpmyX0rCqDqDRp2EVVi4MCQF3wINB-Lzg")
