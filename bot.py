import discord
from discord.ext import commands
from discord.ui import View
import os

TOKEN = os.getenv("TOKEN")

VERIFY_CHANNEL_ID = 1514680391745667082
VERIFIED_ROLE_ID = 1514679192321658950

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================
# ФОРМА ВЕРИФИКАЦИИ
# =========================

class VerifyModal(discord.ui.Modal, title="Верификация"):

    player_id = discord.ui.TextInput(
        label="Ваш ID",
        placeholder="Введите ваш игровой ID",
        required=True
    )

    nickname = discord.ui.TextInput(
        label="Ваш ник",
        placeholder="Введите ваш ник",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):

        role = interaction.guild.get_role(
            VERIFIED_ROLE_ID
        )

        if role:
            await interaction.user.add_roles(role)

        await interaction.response.send_message(
            f"✅ Верификация успешно пройдена!\n\n"
            f"🆔 ID: {self.player_id}\n"
            f"👤 Ник: {self.nickname}",
            ephemeral=True
        )

# =========================
# КНОПКА
# =========================

class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Пройти верификацию",
        emoji="🔐",
        style=discord.ButtonStyle.green
    )
    async def verify_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            VerifyModal()
        )

# =========================
# СОБЫТИЯ
# =========================

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

    bot.add_view(VerifyView())

    channel = bot.get_channel(
        VERIFY_CHANNEL_ID
    )

    if channel:

        found = False

        async for msg in channel.history(limit=20):

            if (
                msg.author == bot.user
                and msg.components
            ):
                found = True
                break

        if not found:

            embed = discord.Embed(
                title="🔐 Верификация",
                description=(
                    "Для получения доступа к серверу "
                    "нажмите кнопку ниже."
                ),
                color=discord.Color.green()
            )

            await channel.send(
                embed=embed,
                view=VerifyView()
            )

# =========================
# КОМАНДЫ
# =========================

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

# =========================
# ОШИБКИ
# =========================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):
        return

    print(error)

# =========================

bot.run(TOKEN)