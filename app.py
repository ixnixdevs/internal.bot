import discord
from discord.ext import commands
import json
import os
import aiohttp

# --- Konfiguration ---
TOKEN = "DEIN_BOT_TOKEN"  # <-- Hier deinen Token einfügen
DATA_PATH = "webhooks.json"
TEAM_ROLE_ID = 1376222576082419793  # Team-Rolle (für Webhook-Liste & Webhook-Senden)
REQUIRED_ROLE_ID = 1376222576082419793  # Rolle, die /send nutzen darf
LOGO_EMOJI = "<a:29821lightbulb:1395720203274289162>"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# --- Hilfsfunktionen für Webhook-Datei ---
def load_webhooks():
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w") as f:
            json.dump({}, f)
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save_webhooks(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

# --- Webhook Validierung (async) ---
async def is_valid_webhook(url: str) -> bool:
    if not url.startswith("https://discord.com/api/webhooks/"):
        return False
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                return resp.status == 200
        except:
            return False

# --- View mit Button zum Webhook Versand ---
class WebhookSendView(discord.ui.View):
    def __init__(self, message_content, heading, description, ping, image_url, user_id):
        super().__init__(timeout=300)
        self.message_content = message_content
        self.heading = heading
        self.description = description
        self.ping = ping
        self.image_url = image_url
        self.user_id = user_id

    @discord.ui.button(label="An Webhooks senden", style=discord.ButtonStyle.green)
    async def send_webhooks(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Nur Team darf senden
        if not any(role.id == TEAM_ROLE_ID for role in interaction.user.roles):
            await interaction.response.send_message("🚫 Du hast keine Berechtigung, Webhooks zu nutzen.", ephemeral=True)
            return
        
        data = load_webhooks()
        all_webhooks = []
        # Alle Webhooks aller User sammeln
        for user_webhooks in data.values():
            all_webhooks.extend(user_webhooks)

        if not all_webhooks:
            await interaction.response.send_message("⚠️ Es sind keine Webhooks hinterlegt.", ephemeral=True)
            return
        
        valid_webhooks = []
        removed_count = 0
        async with aiohttp.ClientSession() as session:
            for url in all_webhooks:
                json_payload = {
                    "content": self.message_content,
                    "embeds": [{
                        "title": self.heading,
                        "description": self.description,
                        "footer": {"text": f"{LOGO_EMOJI} Informationen bereitgestellt von 𝙞𝙭𝙣𝙞𝙭𝙙𝙚𝙫𝙨"},
                        "fields": [{"name": "Ping", "value": self.ping}]
                    }],
                    "attachments": []
                }
                try:
                    async with session.post(url, json=json_payload) as resp:
                        if resp.status in (200, 204):
                            valid_webhooks.append(url)
                        else:
                            removed_count +=1
                except:
                    removed_count += 1

        # Ungültige Webhooks aus Daten entfernen
        data = load_webhooks()
        changed = False
        for user, hooks in list(data.items()):
            new_hooks = [h for h in hooks if h in valid_webhooks]
            if len(new_hooks) != len(hooks):
                data[user] = new_hooks
                changed = True
            if len(new_hooks) == 0:
                del data[user]
                changed = True
        if changed:
            save_webhooks(data)

        await interaction.response.send_message(
            f"✅ Nachricht wurde an {len(valid_webhooks)} Webhook(s) gesendet. "
            f"{removed_count} ungültige Webhooks wurden entfernt.",
            ephemeral=True
        )
        self.stop()

# --- Slash Commands ---

@bot.slash_command(name="webhook", description="Verwalte deine Webhooks")
async def webhook(ctx: discord.ApplicationContext):
    pass  # Nur Subcommands

@webhook.sub_command(name="add", description="Füge einen neuen Webhook hinzu")
async def webhook_add(ctx: discord.ApplicationContext, url: str):
    await ctx.defer(ephemeral=True)
    if not url.startswith("https://discord.com/api/webhooks/"):
        await ctx.respond("❌ Ungültige Webhook-URL.", ephemeral=True)
        return
    if not await is_valid_webhook(url):
        await ctx.respond("❌ Webhook-URL ist nicht erreichbar oder ungültig.", ephemeral=True)
        return

    data = load_webhooks()
    user_id = str(ctx.user.id)
    if user_id not in data:
        data[user_id] = []
    if url in data[user_id]:
        await ctx.respond("ℹ️ Dieser Webhook ist bereits gespeichert.", ephemeral=True)
        return

    data[user_id].append(url)
    save_webhooks(data)
    await ctx.respond("✅ Webhook erfolgreich hinzugefügt.", ephemeral=True)

@webhook.sub_command(name="remove", description="Entferne einen deiner Webhooks")
async def webhook_remove(ctx: discord.ApplicationContext, url: str):
    user_id = str(ctx.user.id)
    data = load_webhooks()
    if user_id not in data or url not in data[user_id]:
        await ctx.respond("❌ Diese Webhook-URL gehört nicht zu dir oder existiert nicht.", ephemeral=True)
        return

    data[user_id].remove(url)
    if len(data[user_id]) == 0:
        del data[user_id]
    save_webhooks(data)
    await ctx.respond("✅ Webhook erfolgreich entfernt.", ephemeral=True)

@webhook.sub_command(name="list", description="Zeige alle gespeicherten Webhooks (Team only)")
async def webhook_list(ctx: discord.ApplicationContext):
    if not any(role.id == TEAM_ROLE_ID for role in ctx.user.roles):
        await ctx.respond("🚫 Du hast keine Berechtigung.", ephemeral=True)
        return

    data = load_webhooks()
    if not data:
        await ctx.respond("ℹ️ Es sind keine Webhooks gespeichert.", ephemeral=True)
        return

    embed = discord.Embed(title="Gespeicherte Webhooks pro User")
    for user_id, hooks in data.items():
        member = ctx.guild.get_member(int(user_id))
        name = member.display_name if member else user_id
        embed.add_field(name=name, value="\n".join(hooks), inline=False)

    await ctx.respond(embed=embed, ephemeral=True)

@bot.slash_command(name="send", description="Sende UI-Komponenten mit Button zur Webhook-Freigabe")
async def send(
    ctx: discord.ApplicationContext,
    heading: str,
    description: str,
    ping: str,
    image: discord.Attachment,
    channel: discord.Option(discord.abc.GuildChannel, name="channel", description="Zielkanal auswählen"),
    experiment_news: bool = False
):
    # Rollenprüfung
    if not any(role.id == REQUIRED_ROLE_ID for role in ctx.user.roles):
        await ctx.respond("🚫 Du hast keine Berechtigung, diesen Befehl zu nutzen.", ephemeral=True)
        return

    # Bildprüfung
    if not image.content_type or not image.content_type.startswith("image/"):
        await ctx.respond("❌ Nur Bilddateien sind erlaubt!", ephemeral=True)
        return

    # Kanal sendbar prüfen
    if not hasattr(channel, "send"):
        await ctx.respond("❌ Dieser Kanaltyp unterstützt keine Nachrichten!", ephemeral=True)
        return

    await ctx.defer(ephemeral=True)

    closing_text = f"{LOGO_EMOJI} Informationen bereitgestellt von [𝙞𝙭𝙣𝙞𝙭𝙙𝙚𝙫𝙨](https://discord.ixnix.dev)"
    if experiment_news:
        closing_text += "\n-# Alle Daten können sich ändern und sind möglicherweise nicht mehr aktuell."

    components = [
        discord.ui.Container(
            discord.ui.TextDisplay(content=f"# {heading} - {ping}\n> {description}"),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(url=f"attachment://{image.filename}")
            ),
            discord.ui.Separator(divider=True, spacing=discord.SeparatorSpacingSize.small),
            discord.ui.TextDisplay(content=closing_text),
        )
    ]
    view = discord.ui.View(*components)

    sent_message = await channel.send(view=view, file=await image.to_file())

    preview_text = (
        f"✅ Nachricht erfolgreich gesendet in {channel.mention}.\n"
        "Klicke unten, um diese Nachricht an alle Webhooks zu senden."
    )

    webhook_view = WebhookSendView(
        message_content=f"**{heading}**\n{description}\nPing: {ping}",
        heading=heading,
        description=description,
        ping=ping,
        image_url=f"attachment://{image.filename}",
        user_id=ctx.user.id
    )

    await ctx.respond(preview_text, view=webhook_view, ephemeral=True)

bot.run(TOKEN)
