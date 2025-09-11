# bot.py
import os
import hmac
import hashlib
import threading
import asyncio

from dotenv import load_dotenv
from flask import Flask, request

import discord
from discord.ext import commands
from github import Github

# ------- Cargar variables -------
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_OWNER = os.getenv("GITHUB_OWNER", "")
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")  # recomendado

def _parse_ids(csv: str):
    if not csv:
        return []
    return [int(x.strip()) for x in csv.split(",") if x.strip().isdigit()]

ADMINS_APPROVE = _parse_ids(os.getenv("ADMINS_APPROVE", ""))
ADMINS_MERGE = _parse_ids(os.getenv("ADMINS_MERGE", ""))

PORT = int(os.getenv("PORT", "5000"))

# ------- Discord bot -------
intents = discord.Intents.default()  # no necesitamos message content
bot = commands.Bot(command_prefix="!", intents=intents)
gh = Github(GITHUB_TOKEN)

app = Flask(__name__)

# ========= Discord UI =========
class MergeView(discord.ui.View):
    def __init__(self, repo_name: str, pr_number: int, message_id: int, channel_id: int):
        super().__init__(timeout=None)
        self.repo_name = repo_name
        self.pr_number = pr_number
        self.message_id = message_id
        self.channel_id = channel_id

    @discord.ui.button(label="🔀 Merge", style=discord.ButtonStyle.primary)
    async def merge(self, interaction: discord.Interaction, _button: discord.ui.Button):
        if interaction.user.id not in ADMINS_MERGE:
            await interaction.response.send_message("❌ No tienes permisos para hacer merge.", ephemeral=True)
            return

        try:
            repo = gh.get_repo(f"{GITHUB_OWNER}/{self.repo_name}")
            pr = repo.get_pull(self.pr_number)
            result = pr.merge(commit_message=f"Merge desde Discord por {interaction.user} 🤖")
            if result.merged:
                # desactivar botones en el mensaje original
                channel = bot.get_channel(self.channel_id)
                msg = await channel.fetch_message(self.message_id)
                await msg.edit(content=f"{msg.content}\n\n🔀 Merge realizado por **{interaction.user}**", view=None)
                await interaction.response.send_message(f"✅ PR #{self.pr_number} mergeado correctamente.", ephemeral=False)
            else:
                await interaction.response.send_message(f"❌ No fue posible mergear: {result.message}", ephemeral=False)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error al mergear: {e}", ephemeral=True)


class ReviewModal(discord.ui.Modal):
    def __init__(self, repo_name: str, pr_number: int, message_id: int, channel_id: int, action: str):
        super().__init__(title=f"{action.capitalize()} PR #{pr_number}")
        self.repo_name = repo_name
        self.pr_number = pr_number
        self.message_id = message_id
        self.channel_id = channel_id
        self.action = action

        self.comment = discord.ui.TextInput(
            label="Comentario",
            style=discord.TextStyle.paragraph,
            placeholder="Explica por qué apruebas/rechazas este PR",
            required=True,
            max_length=1000,
        )
        self.add_item(self.comment)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            repo = gh.get_repo(f"{GITHUB_OWNER}/{self.repo_name}")
            pr = repo.get_pull(self.pr_number)
            body = str(self.comment)

            if self.action == "aprobar":
                pr.create_review(body=body, event="APPROVE")
                await interaction.response.send_message(f"✅ PR #{self.pr_number} aprobado con comentario.", ephemeral=False)

                # añadir botón de merge (si quien aprobó además puede mergear)
                channel = bot.get_channel(self.channel_id)
                msg = await channel.fetch_message(self.message_id)
                view = MergeView(self.repo_name, self.pr_number, self.message_id, self.channel_id)
                await msg.edit(view=view)

            else:  # rechazar
                pr.create_review(body=body, event="REQUEST_CHANGES")
                await interaction.response.send_message(f"❌ PR #{self.pr_number} rechazado con comentario.", ephemeral=False)

        except Exception as e:
            await interaction.response.send_message(f"❌ Error al procesar la review: {e}", ephemeral=True)


class PRButtons(discord.ui.View):
    def __init__(self, repo_name: str, pr_number: int):
        super().__init__(timeout=None)
        self.repo_name = repo_name
        self.pr_number = pr_number
        self.message_id = None
        self.channel_id = None

    @discord.ui.button(label="✅ Aprobar", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, _button: discord.ui.Button):
        if interaction.user.id not in ADMINS_APPROVE:
            await interaction.response.send_message("❌ No tienes permisos para aprobar.", ephemeral=True)
            return
        await interaction.response.send_modal(ReviewModal(self.repo_name, self.pr_number, self.message_id, self.channel_id, "aprobar"))

    @discord.ui.button(label="❌ Rechazar", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, _button: discord.ui.Button):
        if interaction.user.id not in ADMINS_APPROVE:
            await interaction.response.send_message("❌ No tienes permisos para rechazar.", ephemeral=True)
            return
        await interaction.response.send_modal(ReviewModal(self.repo_name, self.pr_number, self.message_id, self.channel_id, "rechazar"))


# ========= GitHub Webhook (Flask) =========
def verify_signature(secret: str, signature_header: str, body: bytes) -> bool:
    if not secret:
        return True  # si no configuraste secreto, omite validación (no recomendado)
    if not signature_header or "=" not in signature_header:
        return False
    algo, signature = signature_header.split("=", 1)
    if algo != "sha256":
        return False
    mac = hmac.new(secret.encode(), msg=body, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method != "POST":
        return "Method not allowed", 405

    # validar firma (si hay secreto)
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_signature(GITHUB_WEBHOOK_SECRET, signature, request.data):
        return "Invalid signature", 401

    data = request.json or {}
    action = data.get("action")
    pr = data.get("pull_request") or {}

    if action in ("opened", "reopened", "ready_for_review"):
        repo_name = data["repository"]["name"]
        pr_number = pr["number"]
        pr_title = pr.get("title") or "PR"
        pr_body = pr.get("body") or "Sin descripción"
        pr_url = pr["html_url"]
        author = pr["user"]["login"]

        embed = discord.Embed(
            title=f"📌 Nuevo PR en {repo_name}",
            description=pr_body,
            url=pr_url,
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Título", value=pr_title, inline=False)
        embed.add_field(name="Autor", value=author, inline=True)
        embed.add_field(name="Número", value=f"#{pr_number}", inline=True)

        async def send_embed():
            await bot.wait_until_ready()
            channel = bot.get_channel(DISCORD_CHANNEL_ID)
            if not channel:
                return
            view = PRButtons(repo_name, pr_number)
            msg = await channel.send(embed=embed, view=view)
            view.message_id = msg.id
            view.channel_id = channel.id

        bot.loop.create_task(send_embed())

    return "OK", 200


# ========= Arranque =========
def run_flask():
    # host 0.0.0.0 para ngrok / producción
    app.run(host="0.0.0.0", port=PORT)
######
#CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

@bot.event
async def on_ready():
    print(f"🤖 Bot conectado como {bot.user} (id: {bot.user.id})")
    ######
    '''
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("✅ ¡Hola! Estoy vivo y listo para procesar PRs 🚀")
    '''

if __name__ == "__main__":
    # Flask y Discord en paralelo
    threading.Thread(target=run_flask, daemon=True).start()
    bot.run(DISCORD_TOKEN)
    #bot.run(os.getenv("DISCORD_TOKEN"))