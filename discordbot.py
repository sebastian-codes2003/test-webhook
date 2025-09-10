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


@bot.slash_command(name="saludo", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hola! ¿Cómo estás?")


class MyView(discord.ui.View):
    @discord.ui.button(label="A button", style=discord.ButtonStyle.primary, disabled=True) # pass `disabled=True` to make the button pre-disabled
    async def button_callback(self, button, interaction):
        await interaction.response.send_message("You clicked the button!")

@bot.command()
async def button(ctx):
    await ctx.send("Press the button!", view=MyView())

# @bot.slash_command(name="kick_user", description="Kick a user from the server")
# async def kick_user(ctx: discord.ApplicationContext, user: discord.User):
#     await ctx.guild.kick(user)
#     await ctx.respond(f"Usuario {user.mention} expulsado del servidor.")

# @bot.slash_command(
#     name="clear_chat_all",
#     description="Clear all messages in the channel"
# )
# async def clear_chat_all(ctx: discord.ApplicationContext):
#     await ctx.channel.purge()
#     await ctx.respond("Chat limpiado!", ephemeral=True)


@bot.event
async def on_ready():
    print(f"{bot.user} ha iniciado sesión!")
    await bot.sync_commands()


# === Función que server.py puede usar para mandar mensajes ===
async def notify_issue(title: str, url: str):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f"📌 Nueva issue creada: **{title}**\n🔗 {url}")


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
        embed.add_field(name="Acciones", value="Para más información, presiona el botón:", inline=False)
        embed.set_footer(text="GitHub Bot 🤖")

        await channel.send(embed=embed)


def run_bot():
    bot.run(TOKEN)
