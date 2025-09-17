import discord
import os
from dotenv import load_dotenv
from github import Github


load_dotenv()
TOKEN_DISCORD = str(os.getenv("TOKEN_DISCORD"))
CHANNEL_ID_PULL_REQUEST = int(os.getenv("CHANNEL_ID_PULL_REQUEST"))
TOKEN_GITHUB = str(os.getenv("TOKEN_GITHUB"))
ADMINS_REVIEWER = list(map(int, os.getenv("ADMINS_REVIEWER", "").split(",")))
ADMINS_MERGE = list(map(int, os.getenv("ADMINS_MERGE", "").split(",")))
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
        pr_number: int,
        repo_full: str,
    ):
        super().__init__(timeout=None)

        self.pr_url = pr_url
        self.pr_number = pr_number
        self.repo_full = repo_full
        self.message_id = None
        self.channel_id = None

        self.add_item(
            discord.ui.Button(
                label="🔗 Ver Pull Request",
                style=discord.ButtonStyle.link,
                url=self.pr_url,
            )
        )

    async def validate_pr(self, interaction: discord.Interaction, action: str) -> bool:

        if not has_permission(interaction.user.id, action=action):
            await interaction.response.send_message(
                f"🚫 No tienes permisos para {action.lower()} este PR.",
                ephemeral=False,
            )
            return False

        repo = gh.get_repo(self.repo_full)
        pr = repo.get_pull(self.pr_number)

        if pr.state == "closed" or pr.state == "merged":
            await interaction.response.send_message(
                f"⚠️ El PR #{self.pr_number} ya está cerrado o mergeado.",
                ephemeral=False,
            )
            return False

        reviews = pr.get_reviews()
        for review in reviews:
            if (
                action == "APPROVE" or action == "REJECT"
            ) and review.state == "APPROVED":
                await interaction.response.send_message(
                    f"⚠️ Este PR #{self.pr_number} ya fue aprobado por **{review.user.login}**.",
                    ephemeral=False,
                )
                return False

        return True

    @discord.ui.button(
        label="✅ Aprobar",
        style=discord.ButtonStyle.success,
        custom_id="approve_pr_button",
    )
    async def approve_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if not await self.validate_pr(interaction, action="APPROVE"):
            return

        await interaction.response.send_modal(
            ReviewPullRequestModal(
                self.pr_number,
                self.repo_full,
                action="APPROVE",
                channel_id=self.channel_id,
                message_id=self.message_id,
            )
        )

    @discord.ui.button(
        label="❌ Rechazar",
        style=discord.ButtonStyle.danger,
        custom_id="reject_pr_button",
    )
    async def reject_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if not await self.validate_pr(interaction, action="REJECT"):
            return

        await interaction.response.send_modal(
            ReviewPullRequestModal(
                self.pr_number,
                self.repo_full,
                action="REJECT",
                channel_id=self.channel_id,
                message_id=self.message_id,
            )
        )


async def notify_new_pull_request(pr_data: dict):
    channel = bot.get_channel(CHANNEL_ID_PULL_REQUEST)
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
            pr_data["number"],
            pr_data["repository_full"],
        )

        message = await channel.send(embed=embed, view=view)
        view.message_id = message.id
        view.channel_id = channel.id


# === Función para aceptar / rechazar el pull request ===
class ReviewPullRequestModal(discord.ui.Modal):
    def __init__(
        self,
        pr_number: int,
        repo_full: str,
        action: str,
        channel_id=None,
        message_id=None,
    ):
        super().__init__(title=f"Revisar Pull Request #{pr_number}", timeout=None)
        self.pr_number = pr_number
        self.repo_full = repo_full
        self.action = action
        self.channel_id = channel_id
        self.message_id = message_id

        self.add_item(
            discord.ui.InputText(
                label="Comentarios",
                style=discord.InputTextStyle.long,
                placeholder="Explica por qué apruebas/rechazas este PR",
                required=True,
                max_length=1000,
            )
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)

            repo = gh.get_repo(self.repo_full)
            pr = repo.get_pull(self.pr_number)
            body_pull_request = str(self.children[0].value)

            if not self.channel_id or not self.message_id:
                print("No se proporcionaron channel_id o message_id.")
                return

            if self.action == "APPROVE":
                pr.create_review(body=body_pull_request, event="APPROVE")

                print("PR approved")

                try:
                    channel = bot.get_channel(self.channel_id)
                    msg = await channel.fetch_message(self.message_id)

                    merge_embed = discord.Embed(
                        title=f"🔔 Solicitud de Merge para PR #{self.pr_number}",
                        description=f"El PR #{self.pr_number} en el repositorio **{self.repo_full}** ha sido aprobado y está listo para ser mergeado.",
                        color=discord.Color.green(),
                    )
                    merge_embed.set_thumbnail(
                        url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
                    )
                    merge_embed.set_footer(text="GitHub Bot 🤖")

                    merge_view = RequestToMergeButtons(
                        self.pr_number, self.repo_full, self.channel_id, self.message_id
                    )

                    await msg.edit(embed=merge_embed, view=merge_view)

                except Exception as e:
                    print("Error al editar mensaje para merge:", e)

            elif self.action == "REJECT":
                pr.create_review(body=body_pull_request, event="REQUEST_CHANGES")
                pr.edit(state="closed")
                print("PR rejected and closed")

                try:
                    channel = bot.get_channel(self.channel_id)
                    msg = await channel.fetch_message(self.message_id)

                    new_embed = discord.Embed(
                        title=f"❌ Pull Request #{self.pr_number} Rechazado",
                        description=f"El PR en **{self.repo_full}** fue rechazado y cerrado.",
                        color=discord.Color.red(),
                    )
                    new_embed.set_footer(text="GitHub Bot 🤖")

                    await msg.edit(embed=new_embed, view=None)
                except Exception as e:
                    print("Error al editar mensaje:", e)

        except Exception as e:
            await interaction.followup.send(
                f"❌ Error al revisar el PR: {e}", ephemeral=True
            )
            print("Error al revisar el PR:", e)


# === Funcion para fusionar el pull request ===
class RequestToMergeButtons(discord.ui.View):
    def __init__(
        self, pr_number: int, repo_full: str, channel_id=None, message_id=None
    ):
        super().__init__(timeout=None)
        self.pr_number = pr_number
        self.repo_full = repo_full
        self.channel_id = channel_id
        self.message_id = message_id

    @discord.ui.button(
        label="🔀 Mergear Pull Request",
        style=discord.ButtonStyle.primary,
        custom_id="merge_pr_button",
    )
    async def merge_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        # 1. Permisos
        if not has_permission(interaction.user.id, action="MERGE"):
            await interaction.response.send_message(
                "🚫 No tienes permisos para mergear este PR.", ephemeral=False
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            repo = gh.get_repo(self.repo_full)
            pr = repo.get_pull(self.pr_number)

            # 2. Estado del PR
            if pr.state in ("closed", "merged"):
                await interaction.followup.send(
                    f"⚠️ El PR #{self.pr_number} ya está cerrado o mergeado.",
                    ephemeral=True,
                )
                return

            # 4. Editar mensaje original del canal con embed final
            channel = bot.get_channel(self.channel_id)
            msg = await channel.fetch_message(self.message_id)

            pr.merge()
            merged_embed = discord.Embed(
                title=f"🎉 Pull Request #{self.pr_number} Mergeado",
                description=f"El PR en **{self.repo_full}** fue mergeado exitosamente por {interaction.user.mention}.",
                color=discord.Color.blue(),
            )
            merged_embed.set_thumbnail(
                url="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            )
            merged_embed.set_footer(text="GitHub Bot 🤖")

            await msg.edit(embed=merged_embed, view=None)  # ❌ se quitan los botones

            print("PR merged")

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error al mergear: {e}", ephemeral=True
            )


# === Funcion para verificar permisos ===
def has_permission(user_id: int, action: str) -> bool:
    if action == "APPROVE":
        return user_id in ADMINS_REVIEWER
    elif action == "MERGE":
        return user_id in ADMINS_MERGE
    elif action == "REJECT":
        return user_id in ADMINS_REVIEWER
    return False


def run_bot():
    bot.run(TOKEN_DISCORD)
