import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_importcogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("_"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Geladen: {filename}")
            except Exception as e:
                print(f"❌ Fehler beim Laden von {filename}: {e}")

@bot.event
async def on_ready():
    print(f"Bot ist online als {bot.user}!")

async def main():
    async with bot:
        await load_cogs()
        await bot.start("TOKEN_HERE")  # Ersetze 

asyncio.run(main())
