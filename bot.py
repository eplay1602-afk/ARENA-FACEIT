import discord
from discord.ext import commands
from discord.ui import View
from discord import app_commands
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
@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Синхронизировано {len(synced)} команд")
    except Exception as e:
        print(e)

    bot.add_view(VerifyView())

    # остальной твой код...
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
# =========================
# SLASH КОМАНДЫ
# =========================

@bot.tree.command(name="kick", description="Кикнуть пользователя")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Не указана"):
    await member.kick(reason=reason)
    await interaction.response.send_message(
        f"👢 {member.mention} был кикнут.\nПричина: {reason}"
    )


@bot.tree.command(name="ban", description="Забанить пользователя")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Не указана"):
    await member.ban(reason=reason)
    await interaction.response.send_message(
        f"🔨 {member.mention} был забанен.\nПричина: {reason}"
    )


@bot.tree.command(name="unban", description="Разбанить пользователя")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str):

    user = await bot.fetch_user(int(user_id))

    await interaction.guild.unban(user)

    await interaction.response.send_message(
        f"✅ Пользователь {user} разбанен."
    )


@bot.tree.command(name="mute", description="Выдать мут")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(
    interaction: discord.Interaction,
    member: discord.Member,
    minutes: int,
    reason: str = "Не указана"
):
    from datetime import timedelta

    await member.timeout(
        timedelta(minutes=minutes),
        reason=reason
    )

    await interaction.response.send_message(
        f"🔇 {member.mention} получил мут на {minutes} мин.\nПричина: {reason}"
    )


@bot.tree.command(name="unmute", description="Снять мут")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):

    await member.timeout(None)

    await interaction.response.send_message(
        f"🔊 Мут снят с {member.mention}"
    )


@bot.tree.command(name="grole", description="Выдать роль")
@app_commands.checks.has_permissions(manage_roles=True)
async def grole(
    interaction: discord.Interaction,
    member: discord.Member,
    role: discord.Role
):

    await member.add_roles(role)

    await interaction.response.send_message(
        f"✅ Роль {role.mention} выдана {member.mention}"
    )


@bot.tree.command(name="gnrole", description="Забрать роль")
@app_commands.checks.has_permissions(manage_roles=True)
async def gnrole(
    interaction: discord.Interaction,
    member: discord.Member,
    role: discord.Role
):

    await member.remove_roles(role)

    await interaction.response.send_message(
        f"❌ Роль {role.mention} забрана у {member.mention}"
    )


@bot.tree.command(name="clear", description="Очистить сообщения")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(
    interaction: discord.Interaction,
    amount: int
):

    await interaction.channel.purge(limit=amount)

    await interaction.response.send_message(
        f"🗑 Удалено сообщений: {amount}",
        ephemeral=True
    )
bot.run(TOKEN)