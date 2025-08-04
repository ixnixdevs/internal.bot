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

class VerifyButton(discord.ui.Button):

    def __init__(self, role_id: int):

        super().__init__(label="Verifizieren", style=discord.ButtonStyle.success)

        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):

        role = interaction.guild.get_role(int(self.role_id))

        if not role:

            return await interaction.response.send_message("❌ Fehler: Rolle nicht gefunden.", ephemeral=True)

        try:

            await interaction.user.add_roles(role)

            await interaction.response.send_message("Du wurdest erfolgreich verifiziert!", ephemeral=True)

        except discord.Forbidden:

            await interaction.response.send_message("❌ Ich habe keine Berechtigung, dir diese Rolle zu geben.", ephemeral=True)

class VerifyView(discord.ui.View):

    def __init__(self, role_id: int):

        super().__init__(timeout=None)

        self.add_item(VerifyButton(role_id))

class VerifyCog(commands.Cog):

    def __init__(self, bot: commands.Bot):

        self.bot = bot

    async def send_verify_message(self, guild: discord.Guild):

        settings = load_settings()

        guild_id = str(guild.id)

        if guild_id not in settings:

            return

        data = settings[guild_id]

        channel_id = data.get("verify_channel_id")

        role_id = data.get("verify_role_id")

        if not channel_id or not role_id:

            return

        channel = guild.get_channel(int(channel_id))

        if not channel:

            return

        components: list[discord.ui.Item[discord.ui.View]] = [

            discord.ui.Container(

                discord.ui.TextDisplay(

                    content="## Verify\n> Mit einem Klick auf den Button, kannst du dich für diesen Server **verifizieren** und die restlichen Channels sehen!"

                )

            ),

        ]

        view = discord.ui.View(*components)

        view.add_item(VerifyButton(role_id))

        await channel.send(view=view)

    @commands.Cog.listener()

    async def on_ready(self):

        for guild in self.bot.guilds:

            await self.send_verify_message(guild)

    @discord.commands.slash_command(name="resend_verify", description="Sende die Verifizierungsnachricht erneut.")

    @discord.default_permissions(administrator=True)

    async def resend_verify(self, ctx: discord.ApplicationContext):

        await self.send_verify_message(ctx.guild)

        await ctx.respond("✅ Verifizierungsnachricht wurde erneut gesendet.", ephemeral=True)

def setup(bot: commands.Bot):

    bot.add_cog(VerifyCog(bot))