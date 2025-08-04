import discord

from discord.ext import commands

from discord.commands import slash_command

import json

import os

SETTINGS_FILE = "settings.json"

def load_settings():

    if os.path.exists(SETTINGS_FILE):

        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:

            return json.load(f)

    return {}

def save_settings(settings):

    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:

        json.dump(settings, f, indent=4)

def truncate_label(text, limit=100):

    return text[:limit] if len(text) > limit else text

# --- Auswahl für Willkommenskanal ---

class WelcomeChannelSelect(discord.ui.Select):

    def __init__(self, guild: discord.Guild):

        options = [

            discord.SelectOption(label=truncate_label(c.name), value=str(c.id))

            for c in guild.text_channels[:25]

        ] or [discord.SelectOption(label="Keine Kanäle verfügbar", value="none", default=True)]

        super().__init__(placeholder="Wähle Willkommenskanal...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):

        selected_id = self.values[0]

        if selected_id == "none":

            return await interaction.response.send_message("❌ Kein gültiger Kanal.", ephemeral=True)

        settings = load_settings()

        settings.setdefault(str(interaction.guild.id), {})["welcome_channel_id"] = selected_id

        save_settings(settings)

        await interaction.response.send_message(f"✅ Willkommenskanal ist nun <#{selected_id}>.", ephemeral=True)

class WelcomeChannelView(discord.ui.View):

    def __init__(self, guild):

        super().__init__(timeout=180)

        self.add_item(WelcomeChannelSelect(guild))

# --- Auswahl für Verify-Channel ---

class VerifyChannelSelect(discord.ui.Select):

    def __init__(self, guild: discord.Guild):

        options = [

            discord.SelectOption(label=truncate_label(c.name), value=str(c.id))

            for c in guild.text_channels[:25]

        ] or [discord.SelectOption(label="Keine Kanäle verfügbar", value="none", default=True)]

        super().__init__(placeholder="Wähle Verifizierungskanal...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):

        selected_id = self.values[0]

        if selected_id == "none":

            return await interaction.response.send_message("❌ Kein gültiger Kanal.", ephemeral=True)

        settings = load_settings()

        settings.setdefault(str(interaction.guild.id), {})["verify_channel_id"] = selected_id

        save_settings(settings)

        await interaction.response.send_message(f"✅ Verifizierungskanal ist nun <#{selected_id}>.", ephemeral=True)

class VerifyChannelView(discord.ui.View):

    def __init__(self, guild):

        super().__init__(timeout=180)

        self.add_item(VerifyChannelSelect(guild))

# --- Auswahl für Verify-Rolle (Seite 1 & 2) ---

class VerifyRoleSelect(discord.ui.Select):

    def __init__(self, guild: discord.Guild, page=0):

        roles = [r for r in guild.roles if not r.is_bot_managed() and not r.is_default()]

        start = page * 25

        paginated = roles[start:start + 25]

        options = [

            discord.SelectOption(label=truncate_label(r.name), value=str(r.id))

            for r in paginated

        ] or [discord.SelectOption(label="Keine Rollen verfügbar", value="none", default=True)]

        super().__init__(

            placeholder=f"Seite {page + 1}: Wähle Verifizierungsrolle...",

            min_values=1, max_values=1, options=options,

            custom_id=f"verify_role_select_{page}"

        )

    async def callback(self, interaction: discord.Interaction):

        selected_id = self.values[0]

        if selected_id == "none":

            return await interaction.response.send_message("❌ Keine gültige Rolle.", ephemeral=True)

        settings = load_settings()

        settings.setdefault(str(interaction.guild.id), {})["verify_role_id"] = selected_id

        save_settings(settings)

        await interaction.response.send_message(f"✅ Verifizierungsrolle gesetzt: <@&{selected_id}>", ephemeral=True)

class VerifyRoleView(discord.ui.View):

    def __init__(self, guild):

        super().__init__(timeout=180)

        self.add_item(VerifyRoleSelect(guild, page=0))

        if len(guild.roles) > 25:

            self.add_item(VerifyRoleSelect(guild, page=1))

# --- Button View für alles ---

class SettingsButtonView(discord.ui.View):

    def __init__(self, guild):

        super().__init__(timeout=180)

        self.guild = guild

    @discord.ui.button(label="Willkommensnachrichten", style=discord.ButtonStyle.primary, emoji="👋")

    async def welcome_button(self, button, interaction):

        await interaction.response.send_message(

            "Wähle den Kanal für Willkommensnachrichten:",

            view=WelcomeChannelView(interaction.guild),

            ephemeral=True

        )

    @discord.ui.button(label="Verifizierungsrolle", style=discord.ButtonStyle.success, emoji="✅")

    async def verify_button(self, button, interaction):

        await interaction.response.send_message(

            "Wähle die Rolle für verifizierte Nutzer:",

            view=VerifyRoleView(interaction.guild),

            ephemeral=True

        )

    @discord.ui.button(label="Verifizierungskanal", style=discord.ButtonStyle.secondary, emoji="🛡️")

    async def verify_channel_button(self, button, interaction):

        await interaction.response.send_message(

            "Wähle den Kanal, in dem der `/verify` Button angezeigt werden soll:",

            view=VerifyChannelView(interaction.guild),

            ephemeral=True

        )

# --- Cog ---

class SettingsCog(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    @slash_command(name="settings", description="Öffne das Konfigurationsmenü des Bots.")

    async def settings_ui(self, ctx: discord.ApplicationContext):

        embed = discord.Embed(

            title="⚙️ Einstellungen",

            description="Konfiguriere den Bot mit den folgenden Optionen:",

            color=discord.Color.blurple()

        )

        await ctx.respond(embed=embed, view=SettingsButtonView(ctx.guild), ephemeral=True)

def setup(bot):

    bot.add_cog(SettingsCog(bot))