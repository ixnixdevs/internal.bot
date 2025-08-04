import discord

from discord.ext import commands

import json

import os

LANGUAGE_FILE = "language.json"

def save_language(guild_id, lang):

    if not os.path.exists(LANGUAGE_FILE):

        with open(LANGUAGE_FILE, "w") as f:

            json.dump({}, f)

    with open(LANGUAGE_FILE, "r") as f:

        data = json.load(f)

    data[str(guild_id)] = lang

    with open(LANGUAGE_FILE, "w") as f:

        json.dump(data, f, indent=2)

class Language(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    @discord.slash_command(name="language", description="Setzt die Sprache für den Server")

    async def language(self, ctx: discord.ApplicationContext, selection: discord.Option(str, choices=["de", "eng"])):

        save_language(ctx.guild.id, selection)

        msg = "Sprache erfolgreich auf Deutsch gesetzt!" if selection == "de" else "Language set to English successfully!"

        await ctx.respond(f"✅ {msg}", ephemeral=True)

def setup(bot):

    bot.add_cog(Language(bot))