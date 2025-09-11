import discord
import os
from dotenv import load_dotenv
from github import Github

load_dotenv()
TOKEN_DISCORD = str(os.getenv("TOKEN"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID")) 
TOKEN_GITHUB = str(os.getenv("TOKEN_GITHUB"))

intents = discord.Intents.default()
intents.members = True

bot = discord.Bot(intents=intents)


# === Eventos ===
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(
            f"Bienvenido al servidor, {member.mention}! Siéntete libre de presentarte."
        )


@bot.event
async def on_ready():
    print(f"{bot.user} ha iniciado sesión!")
    await bot.sync_commands()


# === Comandos ===
@bot.slash_command(name="saludo", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    try:

        await ctx.respond(f"Hola, {ctx.author.mention}! 👋")
    except Exception as e:
        await ctx.respond(f"Error: {str(e)}")

# === Función que server.py puede usar para mandar mensajes (Pull request) ===

class PullRequestViewButtons(discord.ui.View):
    def __init__(self, pr_url: str):
        super().__init__(timeout=None)
        # Botón tipo link (sin callback, directo)
        self.add_item(
            discord.ui.Button(
                label="Ver Pull Request", style=discord.ButtonStyle.link, url=pr_url
            )
        )

    @discord.ui.button(label="Aprobar", style=discord.ButtonStyle.success, emoji="✅")
    async def approve_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await interaction.response.send_message(
            "Pull Request aprobado!", ephemeral=True
        )

    @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.danger, emoji="❌")
    async def reject_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await interaction.response.send_message(
            "Pull Request rechazado!", ephemeral=True
        )


async def notify_pull_request(pr_data: dict):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title=f"🔀 Pull Request #{pr_data['number']}: {pr_data['title']}",
            description=pr_data["description"],
            url=pr_data["url"],
            color=discord.Color.blurple(),
        )

        # Autor con avatar
        embed.set_author(
            name=pr_data["author"],
            icon_url=pr_data.get(
                "author_avatar",
                "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
            ),
        )

        # Campos adicionales
        embed.add_field(
            name="Ramas",
            value=f"`{pr_data['head_branch']}` → `{pr_data['base_branch']}`",
            inline=False,
        )
        embed.add_field(name="Creado en", value=pr_data["created_at"], inline=False)

        # Icono GitHub
        embed.set_thumbnail(
            url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
        )

        # Footer
        embed.set_footer(text="GitHub Bot 🤖")

        # embed button
        embed.add_field(
            name="Acciones",
            value="Para más información, presiona el botón:",
            inline=False,
        )
        embed.set_footer(text="GitHub Bot 🤖")

        view = PullRequestViewButtons(pr_data["url"])
        await channel.send(embed=embed, view=view)


def run_bot():
    bot.run(TOKEN_DISCORD)
