import discord

from discord.ext import commands, tasks

from discord.commands import slash_command

import datetime

AD_CHANNEL_ID = 1376465522211946496  # Dein Werbe-Channel (hardcodiert)

class Advertising(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.auto_advertisement.start()

    def cog_unload(self):

        self.auto_advertisement.cancel()

    # --- Komponente: Werbung anzeigen ---

    def get_ad_view(self) -> discord.ui.View:

        components: list[discord.ui.Item[discord.ui.View]] = [

            discord.ui.Container(

                discord.ui.TextDisplay(content=(

                    "### 🇩🇪 𝙞𝙭𝙣𝙞𝙭𝙙𝙚𝙫𝙨 – Dein Ort für coole Projekte!\n"

                    "Bei 𝙞𝙭𝙣𝙞𝙭𝙙𝙚𝙫𝙨 dreht sich alles um Discord-Bots, Webseiten-Codes, eigene Tools und kreative Ideen.\n"

                    "Wir arbeiten mit vielen großen Partnern zusammen, betreiben eigene Projekte wie einen Minecraft-Server "

                    "und veranstalten regelmäßig spannende Events.\n"

                    "➜ Starte jetzt dein Projekt mit uns!\n"

                    "⤷ Egal ob Anfänger oder Fortgeschrittener – hier wirst du unterstützt."

                )),

                discord.ui.Separator(divider=True, spacing=discord.SeparatorSpacingSize.small),

                discord.ui.TextDisplay(content=(

                    "### 🇺🇸 𝙞𝙭𝙣𝙞𝙭𝙙𝙚𝙫𝙨 – Your place for awesome projects!\n"

                    "At 𝙞𝙭𝙣𝙞𝙭𝙙𝙚𝙫𝙨, it's all about Discord bots, website code, custom tools, and creative ideas.\n"

                    "We collaborate with many big partners, run our own projects like a Minecraft server, and regularly host exciting events.\n"

                    "➜ Start your project with us today!\n"

                    "⤷ Whether you're a beginner or advanced – you'll get the support you need."

                )),

                discord.ui.Button(

                    url="https://discord.ixnix.dev",

                    style=discord.ButtonStyle.link,

                    label="Discord Server",

                ),

                discord.ui.Button(

                    url="https://dash.ixnix.dev",

                    style=discord.ButtonStyle.link,

                    label="Dashboard",

                ),

            )

        ]

        return discord.ui.View(*components)

    # --- Slash Command ---

    @slash_command(name="ad", description="Zeigt die ixnixdevs-Werbung an.")

    async def ad(self, ctx: discord.ApplicationContext):

        await ctx.respond(view=self.get_ad_view(), ephemeral=False)

    # --- Auto-Werbung jeden Tag um 00:01 Uhr ---

    @tasks.loop(minutes=1)

    async def auto_advertisement(self):

        now = datetime.datetime.utcnow()

        if now.hour == 0 and now.minute == 1:

            channel = self.bot.get_channel(AD_CHANNEL_ID)

            if channel:

                try:

                    message = await channel.send(view=self.get_ad_view())

                    try:

                        await message.publish()  # Wenn Channel ein Announcement Channel ist

                    except discord.HTTPException:

                        pass  # Nicht schlimm, wenn kein Announcement-Channel

                except Exception as e:

                    print(f"[AutoAd] Fehler beim Senden: {e}")

    @auto_advertisement.before_loop

    async def before_auto_ad(self):

        await self.bot.wait_until_ready()

# --- Setup ---

def setup(bot):

    bot.add_cog(Advertising(bot))