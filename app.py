import discord

from discord.ext import commands

import os

from dotenv import load_dotenv

# Lade .env Datei
load_dotenv()

intents = discord.Intents.default()

intents.members = True  # Wichtig für on_member_join

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event

async def on_ready():

    print(f"✅ Bot ist online als {bot.user}.")
    
    # Custom Status setzen
    custom_status = discord.Activity(
        type=discord.ActivityType.custom,
        name="v2.0.4"
    )
    await bot.change_presence(activity=custom_status)

# Lade alle Cogs

for filename in os.listdir("./cogs"):

    if filename.endswith(".py"):

        bot.load_extension(f"cogs.{filename[:-3]}")

# Lade Token aus .env Datei
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ Fehler: DISCORD_TOKEN nicht in .env Datei gefunden!")
    exit(1)

bot.run(TOKEN)