import discord

from discord.ext import commands

import json

import os

SETTINGS_FILE = "settings.json"

def load_settings():

    if os.path.exists(SETTINGS_FILE):

        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:

            return json.load(f)

    return {}

class WelcomeCog(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    @commands.Cog.listener()

    async def on_member_join(self, member: discord.Member):

        settings = load_settings()

        guild_id = str(member.guild.id)

        if guild_id not in settings:

            return  # Keine Konfiguration vorhanden

        config = settings[guild_id]

        channel_id = config.get("welcome_channel_id")

        language = config.get("language", "de")  # Fallback zu Deutsch

        if not channel_id:

            return

        channel = member.guild.get_channel(int(channel_id))

        if not channel:

            return

        # 📦 Container-Komponenten vorbereiten

        placeholders = {

            "%userMention%": member.mention,

            "%ServerName%": member.guild.name,

            "%MemberCount%": str(len(member.guild.members))

        }

        if language == "de":

            welcome_text = "## Willkommen %userMention%\nWillkommen auf dem **%ServerName%** Discord Server! Du bist das **%MemberCount%** Mitglied! Wir sind sehr erfreut, dich zu sehen!"

        else:

            welcome_text = "## Welcome %userMention%\nWelcome to the **%ServerName%** Discord server! You are the **%MemberCount%**th member! We’re happy to have you here!"

        for key, value in placeholders.items():

            welcome_text = welcome_text.replace(key, value)

        components = [

            discord.ui.Container(

                discord.ui.TextDisplay(content=welcome_text),

                discord.ui.Separator(divider=True, spacing=discord.SeparatorSpacingSize.small),

                discord.ui.MediaGallery(

                    discord.MediaGalleryItem(

                        url="https://cdn.discordapp.com/attachments/1376218935954771998/1401582464262082661/welcome.png?ex=6890cce3&is=688f7b63&hm=90d565492f2aa0ae21430c3a671fb7fd88eb140f8656560f0cf7fe8d86479639&"

                    )

                )

            )

        ]

        view = discord.ui.View(*components)

        try:

            await channel.send(view=view)

        except Exception as e:

            print(f"[❌] Fehler beim Senden der Willkommensnachricht: {e}")

def setup(bot):

    bot.add_cog(WelcomeCog(bot))