import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View
from datetime import timedelta
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

# =====================================
# ВЕРИФИКАЦИЯ
# =====================================

class VerifyModal(discord.ui.Modal, title="Верификация"):

    player_id = discord.ui.TextInput(
        label="Ваш игровой ID",
        placeholder="Например: 12345",
        required=True
    )

    nickname = discord.ui.TextInput(
        label="Ваш ник",
        placeholder="Например: Arena_Player",
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
            f"🆔 ID: {self.player_id.value}\n"
            f"👤 Ник: {self.nickname.value}",
            ephemeral=True
        )

class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Пройти верификацию",
        emoji="🔐",
        style=discord.ButtonStyle.green,
        custom_id="verify_button"
    )
    async def verify_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            VerifyModal()
        )

# =====================================
# СОБЫТИЯ
# =====================================

@bot.event
async def on_ready():

    print(f"Bot online: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Синхронизировано {len(synced)} команд")
    except Exception as e:
        print(e)

    bot.add_view(VerifyView())

    try:
        channel = await bot.fetch_channel(
            VERIFY_CHANNEL_ID
        )

        print("VERIFY_CHANNEL_ID =", VERIFY_CHANNEL_ID)
        print("Канал найден =", channel)

        embed = discord.Embed(
            title="🔐 Верификация",
            description=(
                "Для получения доступа к серверу "
                "нажмите кнопку ниже.\n\n"
                "После успешной верификации "
                "вам будет выдана роль."
            ),
            color=discord.Color.green()
        )

        await channel.send(
            embed=embed,
            view=VerifyView()
        )

        print("✅ Сообщение верификации отправлено")

    except Exception as e:
        print("❌ Ошибка отправки сообщения:")
        print(e)
# =====================================
# ОБЫЧНЫЕ КОМАНДЫ
# =====================================

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

# =====================================
# SLASH КОМАНДЫ
# =====================================

@bot.tree.command(
    name="kick",
    description="Кикнуть пользователя"
)
@app_commands.checks.has_permissions(
    kick_members=True
)
async def kick(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "Не указана"
):
    await member.kick(reason=reason)

    await interaction.response.send_message(
        f"👢 {member.mention} был кикнут.\n"
        f"Причина: {reason}"
    )

@bot.tree.command(
    name="ban",
    description="Забанить пользователя"
)
@app_commands.checks.has_permissions(
    ban_members=True
)
async def ban(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "Не указана"
):
    await member.ban(reason=reason)

    await interaction.response.send_message(
        f"🔨 {member.mention} был забанен.\n"
        f"Причина: {reason}"
    )

@bot.tree.command(
    name="unban",
    description="Разбанить пользователя"
)
@app_commands.checks.has_permissions(
    ban_members=True
)
async def unban(
    interaction: discord.Interaction,
    user_id: str
):

    user = await bot.fetch_user(
        int(user_id)
    )

    await interaction.guild.unban(user)

    await interaction.response.send_message(
        f"✅ {user} разбанен."
    )

@bot.tree.command(
    name="mute",
    description="Выдать мут"
)
@app_commands.checks.has_permissions(
    moderate_members=True
)
async def mute(
    interaction: discord.Interaction,
    member: discord.Member,
    minutes: int,
    reason: str = "Не указана"
):

    await member.timeout(
        timedelta(minutes=minutes),
        reason=reason
    )

    await interaction.response.send_message(
        f"🔇 {member.mention} получил мут "
        f"на {minutes} минут.\n"
        f"Причина: {reason}"
    )

@bot.tree.command(
    name="unmute",
    description="Снять мут"
)
@app_commands.checks.has_permissions(
    moderate_members=True
)
async def unmute(
    interaction: discord.Interaction,
    member: discord.Member
):

    await member.timeout(None)

    await interaction.response.send_message(
        f"🔊 Мут снят с {member.mention}"
    )

@bot.tree.command(
    name="grole",
    description="Выдать роль"
)
@app_commands.checks.has_permissions(
    manage_roles=True
)
async def grole(
    interaction: discord.Interaction,
    member: discord.Member,
    role: discord.Role
):

    await member.add_roles(role)

    await interaction.response.send_message(
        f"✅ Роль {role.mention} выдана "
        f"{member.mention}"
    )

@bot.tree.command(
    name="gnrole",
    description="Забрать роль"
)
@app_commands.checks.has_permissions(
    manage_roles=True
)
async def gnrole(
    interaction: discord.Interaction,
    member: discord.Member,
    role: discord.Role
):

    await member.remove_roles(role)

    await interaction.response.send_message(
        f"❌ Роль {role.mention} забрана "
        f"у {member.mention}"
    )

@bot.tree.command(
    name="clear",
    description="Удалить сообщения"
)
@app_commands.checks.has_permissions(
    manage_messages=True
)
async def clear(
    interaction: discord.Interaction,
    amount: int
):

    await interaction.response.defer(
        ephemeral=True
    )

    await interaction.channel.purge(
        limit=amount
    )

    await interaction.followup.send(
        f"🗑 Удалено сообщений: {amount}",
        ephemeral=True
    )

# =====================================
# ОБРАБОТКА ОШИБОК
# =====================================

@bot.event
async def on_command_error(
    ctx,
    error
):

    if isinstance(
        error,
        commands.CommandNotFound
    ):
        return

    print(error)

# =====================================

bot.run(TOKEN)