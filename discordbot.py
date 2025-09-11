import discord
import os
from dotenv import load_dotenv
from github import Github

load_dotenv()
TOKEN_DISCORD = str(os.getenv("TOKEN_DISCORD"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
TOKEN_GITHUB = str(os.getenv("TOKEN_GITHUB"))
# GITHUB_OWNER = str(os.getenv("GITHUB_OWNER"))

intents = discord.Intents.default()
intents.members = True

bot = discord.Bot(intents=intents)
gh = Github(TOKEN_GITHUB)


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
class NotificationNewPullRequestButtons(discord.ui.View):
    def __init__(
        self,
        pr_url: str,
        author_repo: str,
        pr_number: int,
        repo_full: str,
        is_merged: bool,
    ):
        super().__init__(timeout=None)

        # Guardar datos para usarlos en callbacks
        self.pr_url = pr_url
        self.author_repo = author_repo
        self.pr_number = pr_number
        self.repo_full = repo_full
        self.is_merged = is_merged

        # Botón directo a GitHub
        self.add_item(
            discord.ui.Button(
                label="🔗 Ver Pull Request",
                style=discord.ButtonStyle.link,
                url=self.pr_url,
            )
        )

    @discord.ui.button(
        label="✅ Aprobar",
        style=discord.ButtonStyle.success,
        custom_id="approve_pr_button",
    )
    async def approve_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if self.is_merged:
            await interaction.response.send_message(
                "⚠️ Este PR ya está mergeado.", ephemeral=True
            )
            return

        await interaction.response.send_modal(
            ReviewPullRequestModal(self.pr_number, self.repo_full, action="APPROVE")
        )

    @discord.ui.button(
        label="❌ Rechazar",
        style=discord.ButtonStyle.danger,
        custom_id="reject_pr_button",
    )
    async def reject_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if self.is_merged:
            await interaction.response.send_message(
                "⚠️ Este PR ya está mergeado.", ephemeral=True
            )
            return

        await interaction.response.send_modal(
            ReviewPullRequestModal(
                self.pr_number, self.repo_full, action="REQUEST_CHANGES"
            )
        )


async def notify_new_pull_request(pr_data: dict):
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
            name=pr_data["author_pr"],
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

        view = NotificationNewPullRequestButtons(
            pr_data["url"],
            pr_data["author_repository"],
            pr_data["number"],
            pr_data["repository_full"],
            pr_data["is_merged"],
        )

        await channel.send(embed=embed, view=view)


# === Función para aceptar el pull request ===
class ReviewPullRequestModal(discord.ui.Modal):
    def __init__(self, pr_number: int, repo_full: str, action: str):
        super().__init__(title=f"Revisar Pull Request #{pr_number}")
        self.pr_number = pr_number
        self.repo_full = repo_full
        self.action = action

        self.add_item(
            discord.ui.InputText(
                label="Comentarios",
                style=discord.InputTextStyle.long,
                placeholder="Explica por qué apruebas/rechazas este PR",
                required=True,
                max_length=1000,
            )
        )

        print(f"Modal initialized for PR #{pr_number} in repo {repo_full} with action {action}")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            repo = gh.get_repo(self.repo_full)
            pr = repo.get_pull(self.pr_number)
            print(pr)
            body_pull_request = self.children[0].value

            if self.action == "APPROVE":
                pr.create_review(body=body_pull_request, event="APPROVE")
                await interaction.response.send_message(
                    f"✅ Has aprobado el PR #{self.pr_number}.", ephemeral=True
                )
                print("PR approved")
            elif self.action == "REQUEST_CHANGES":
                pr.create_review(body=body_pull_request, event="REQUEST_CHANGES")
                await interaction.response.send_message(
                    f"❌ Has solicitado cambios en el PR #{self.pr_number}.",
                    ephemeral=True,
                )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error al revisar el PR: {e}", ephemeral=False
            )


async def accept_pull_request(pr_data: dict):
    # Aquí puedes implementar la lógica para aceptar el pull request
    pass


def run_bot():
    bot.run(TOKEN_DISCORD)
