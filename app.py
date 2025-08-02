import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Lade Cogs
@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user}')
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

bot.run("DEIN_TOKEN")
