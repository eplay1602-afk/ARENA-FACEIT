import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View
from datetime import timedelta
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os
import json
TOKEN = os.getenv("TOKEN")
DATA_FILE = "users.json"
BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)


def load_users():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

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

        users = load_users()

        uid = str(interaction.user.id)

        users[uid] = {
            "nickname": self.nickname.value,
            "elo": users.get(uid, {}).get("elo", 0)
        }

        print("SAVE USER:", uid)
        print(users)

        save_users(users)

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
@bot.tree.command(
    name="givelo",
    description="Выдать ELO"
)
@app_commands.checks.has_permissions(
    administrator=True
)
async def givelo(
    interaction: discord.Interaction,
    member: discord.Member,
    amount: int
):

    users = load_users()

    uid = str(member.id)

    if uid not in users:
        users[uid] = {
            "nickname": member.name,
            "elo": 0
        }

    users[uid]["elo"] += amount

    save_users(users)

    await interaction.response.send_message(
        f"✅ {amount} ELO выдано {member.mention}"
    )


@bot.tree.command(
    name="ngivelo",
    description="Снять ELO"
)
@app_commands.checks.has_permissions(
    administrator=True
)
async def ngivelo(
    interaction: discord.Interaction,
    member: discord.Member,
    amount: int
):

    users = load_users()

    uid = str(member.id)

    if uid not in users:
        return await interaction.response.send_message(
            "Пользователь не найден",
            ephemeral=True
        )

    users[uid]["elo"] = max(
        0,
        users[uid]["elo"] - amount
    )

    save_users(users)

    await interaction.response.send_message(
        f"❌ {amount} ELO снято с {member.mention}"
    )


@bot.tree.command(
    name="profile",
    description="Ваш профиль"
)
async def profile(
    interaction: discord.Interaction
):

    users = load_users()

    uid = str(interaction.user.id)
    print("PROFILE USER:", uid)
    print("USERS:", users)
    if uid not in users:
        return await interaction.response.send_message(
            "Сначала пройдите верификацию",
            ephemeral=True
        )

    nickname = users[uid]["nickname"]
    elo = users[uid]["elo"]

    sorted_users = sorted(
        users.items(),
        key=lambda x: x[1]["elo"],
        reverse=True
    )

    rating = 0

    for place, (user_id, data) in enumerate(
        sorted_users,
        start=1
    ):
        if user_id == uid:
            rating = place
            break
    print(os.listdir("."))

print("FILES:")
print(os.listdir(BASE_DIR))

background = os.path.join(
    BASE_DIR,
    "Без названия7_20260612001021.png"
)

if not os.path.exists(background):
    return await interaction.response.send_message(
        "Файл фона не найден",
        ephemeral=True
    )

img = Image.open(background)

draw = ImageDraw.Draw(img)

font = ImageFont.truetype(
    os.path.join(
        BASE_DIR,
        "NextExitRounded-Black.74b2cd1cc673040ad8c21110e711f52b.ttf"
    ),
    50
)

draw.text(
    (120, 110),
    f"Nickname: {nickname}",
    fill="white",
    font=font
)

draw.text(
    (120, 190),
    f"ELO: {elo}",
    fill="white",
    font=font
)

draw.text(
    (120, 270),
    f"RATING: #{rating}",
    fill="white",
    font=font
)

image_path = f"profile_{uid}.png"

img.save(image_path)

file = discord.File(
    image_path,
    filename="profile.png"
)

embed = discord.Embed(
    title="Вот ваш профиль 👇",
    color=discord.Color.orange()
)

embed.set_image(
    url="attachment://profile.png"
)

await interaction.response.send_message(
    embed=embed,
    file=file
)

os.remove(image_path)
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

print("COMMANDS:")
for cmd in bot.tree.get_commands():
    print(cmd.name)
    
bot.run(TOKEN)