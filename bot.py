import discord
from discord.ext import commands
from discord.ui import View
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================
# КНОПКА ВЕРИФИКАЦИИ
# =========================

class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Пройти верификацию",
        style=discord.ButtonStyle.green,
        emoji="🔐"
    )
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🔐 Для получения доступа введите:\n\n"
            "`!verify ID Ник`\n\n"
            "Пример:\n"
            "`!verify 12345 ARENA_Player`",
            ephemeral=True
        )

# =========================
# СОБЫТИЯ
# =========================

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

# =========================
# КОМАНДЫ
# =========================

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command()
@commands.has_permissions(administrator=True)
async def setupverify(ctx):

    embed = discord.Embed(
        title="🔐 Верификация",
        description=(
            "Для получения доступа к серверу нажмите кнопку ниже.\n\n"
            "После нажатия бот покажет инструкцию."
        ),
        color=discord.Color.green()
    )

    await ctx.send(
        embed=embed,
        view=VerifyView()
    )

@bot.command()
async def verify(ctx, player_id, nickname):

    if ctx.channel.name != "получение-доступа":
        await ctx.send(
            "❌ Верификацию можно проходить только в канале #получение-доступа"
        )
        return

    role = discord.utils.get(ctx.guild.roles, name="Игрок")

    if role is None:
        await ctx.send(
            "❌ Создай роль с названием 'Игрок'"
        )
        return

    await ctx.author.add_roles(role)

    await ctx.send(
        f"✅ {ctx.author.mention}, верификация успешно пройдена!\n"
        f"🆔 ID: {player_id}\n"
        f"👤 Ник: {nickname}"
    )

# =========================
# ОШИБКИ
# =========================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Недостаточно прав.")
        return

    print(error)

# =========================

bot.run(TOKEN)