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


async def notify_pull_request(title: str, url: str):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        # Crear un embed bonito
        embed = discord.Embed(
            title="🔀 Nuevo Pull Request",
            description=title,  # aquí le pasas el "formatted_title"
            url=url,  # hace que el título sea clickeable
            color=discord.Color.blurple(),  # color del borde
        )

        # Puedes agregar un footer
        embed.set_footer(text="GitHub Bot 🤖")

        # Enviar mensaje con embed
        await channel.send(embed=embed)

def run_bot():
    bot.run(TOKEN)
