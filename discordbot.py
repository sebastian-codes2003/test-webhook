import discord
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = str(os.getenv("TOKEN"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # mejor en .env

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


# class MyView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
#     @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="😎") # Create a button with the label "😎 Click me!" with color Blurple
#     async def button_callback(self, button, interaction):
#         await interaction.response.send_message("You clicked the button!") # Send a message when the button is clicked

# @bot.slash_command(name="button2", description="Sends a message with a button")
# async def button(ctx: discord.ApplicationContext):
#     await ctx.respond("This is a button!", view=MyView()) # Send a message with our View class that contains the button

# === Función que server.py puede usar para mandar mensajes ===
# async def notify_issue(title: str, url: str):
#     channel = bot.get_channel(CHANNEL_ID)
#     if channel:
#         await channel.send(f"📌 Nueva issue creada: **{title}**\n🔗 {url}")

# === Función que server.py puede usar para mandar mensajes (Pull request) ===


class PullRequestViewButtons(discord.ui.View):
    def __init__(self, pr_url: str):
        super().__init__()
        self.pr_url = pr_url

    @discord.ui.button(label="Ver Pull Request", style=discord.ButtonStyle.link)
    async def pr_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        button.url = self.pr_url

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
    bot.run(TOKEN)
