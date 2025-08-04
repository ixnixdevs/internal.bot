import discord

from discord.ext import commands

TEAM_ROLE_ID = 1376222576082419793

LOGO_EMOJI = "<a:29821lightbulb:1395720203274289162>"

class Send(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    @discord.slash_command(name="send", description="Sende UI-Komponenten mit Bild und Text")

    async def send(

        self,

        ctx: discord.ApplicationContext,

        heading: str,

        description: str,

        ping: str,

        image: discord.Attachment,

        channel: discord.Option(discord.abc.GuildChannel, name="channel", description="Zielkanal"),

        experiment_news: bool = False

    ):

        # Rollenprüfung

        if not any(role.id == TEAM_ROLE_ID for role in ctx.user.roles):

            await ctx.respond("🚫 Du hast keine Berechtigung, diesen Befehl zu nutzen.", ephemeral=True)

            return

        # Bildprüfung

        if not image.content_type or not image.content_type.startswith("image/"):

            await ctx.respond("❌ Nur Bilddateien sind erlaubt!", ephemeral=True)

            return

        # Sicherstellen, dass Kanal Nachrichten senden kann

        if not hasattr(channel, "send"):

            await ctx.respond("❌ Dieser Kanaltyp unterstützt keine Nachrichten!", ephemeral=True)

            return

        await ctx.defer(ephemeral=True)

        closing_text = f"{LOGO_EMOJI} Informationen bereitgestellt von [𝙞𝙭𝙣𝙞𝙭𝙙𝙚𝙫𝙨](https://discord.ixnix.dev)"

        if experiment_news:

            closing_text += "\n-# Alle Daten können sich ändern und sind möglicherweise nicht mehr aktuell."

        components: list[discord.ui.Item[discord.ui.View]] = [

            discord.ui.Container(

                discord.ui.TextDisplay(content=f"## {heading} - {ping}\n> {description}"),

                discord.ui.MediaGallery(

                    discord.MediaGalleryItem(url=f"attachment://{image.filename}")

                ),

                discord.ui.Separator(divider=True, spacing=discord.SeparatorSpacingSize.small),

                discord.ui.TextDisplay(content=closing_text),

            )

        ]

        view = discord.ui.View(*components)

        await channel.send(view=view, file=await image.to_file())

        await ctx.respond(f"✅ Nachricht wurde erfolgreich in {channel.mention} gesendet.", ephemeral=True)

def setup(bot):

    bot.add_cog(Send(bot))