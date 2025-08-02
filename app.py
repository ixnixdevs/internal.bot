import discord
import ezcord
import os
import asyncio
from dotenv import load_dotenv

# Intents festlegen
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

# Bot-Instanz erstellen
bot = ezcord.Bot(intents=intents)

# Lade Umgebungsvariablen
load_dotenv()

@bot.event
async def on_ready():
    print(f"Bot ist online als {bot.user}")

    # Benutzerdefinierter Status
    custom_status = discord.Game("ROONIÎž")  # Dein Status hier
    await bot.change_presence(status=discord.Status.online, activity=custom_status)

async def main():
    try:
        await bot.load_extension("cogs.send_cog")  # Passe ggf. den Pfad zum Cog an
    except Exception as e:
        print(f"Fehler beim Laden der Cogs: {e}")

    await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())
