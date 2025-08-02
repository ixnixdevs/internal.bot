import discord
from discord.ext import commands

class SendCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="send", description="Send a custom container with parameters.")
    async def send(
        self, 
        ctx: discord.ApplicationContext, 
        heading: str, 
        ping: str, 
        description: str, 
        image: discord.Attachment
    ) -> None:
        # Erstellen des Containers mit den Parametern
        components = [
            discord.ui.Container(
                discord.ui.TextDisplay(content=f"# {heading} - {ping}\n> {description}"),
                discord.ui.MediaGallery(
                    discord.MediaGalleryItem(url=image.url)
                ),
                discord.ui.Separator(divider=True, spacing=discord.SeparatorSpacingSize.small),
                discord.ui.TextDisplay(
                    content="%logo_emoji% Informationen bereitgestellt von [𝙞𝙭𝙣𝙞𝙭𝙙𝙚𝙫𝙨](https://discord.ixnix.dev)\n-# Alle Daten können sich ändern und sind möglicherweise nicht mehr aktuell."
                ),
            ),
        ]

        # View erstellen und Antwort senden
        view = discord.ui.View(*components)
        await ctx.respond("Here are your components:", view=view, ephemeral=True)

# Cog zum Bot hinzufügen
async def setup(bot):
    await bot.add_cog(SendCog(bot))
