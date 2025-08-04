import discord

from discord.ext import commands

import os

intents = discord.Intents.default()

intents.members = True  # Wichtig für on_member_join

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event

async def on_ready():

    print(f"✅ Bot ist online als {bot.user}.")

# Lade alle Cogs

for filename in os.listdir("./cogs"):

    if filename.endswith(".py"):

        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run("TOKEN_HERE")