import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View
from datetime import timedelta
from PIL import Image, ImageDraw, ImageFont
import os
import json

# ---------------- CONFIG ----------------
TOKEN = os.getenv("TOKEN")

DATA_FILE = "users.json"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VERIFY_CHANNEL_ID = 1514680391745667082
VERIFIED_ROLE_ID = 1514679192321658950

# ---------------- JSON ----------------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

def load_users():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ---------------- BOT ----------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- VERIFY MODAL ----------------
class VerifyModal(discord.ui.Modal, title="Верификация"):

    player_id = discord.ui.TextInput(label="Игровой ID", required=True)
    nickname = discord.ui.TextInput(label="Ник", required=True)

    async def on_submit(self, interaction: discord.Interaction):

        role = interaction.guild.get_role(VERIFIED_ROLE_ID)
        if role:
            await interaction.user.add_roles(role)

        users = load_users()
        uid = str(interaction.user.id)

        users[uid] = {
            "nickname": self.nickname.value,
            "elo": users.get(uid, {}).get("elo", 0)
        }

        save_users(users)

        await interaction.response.send_message(
            "✅ Верификация пройдена!",
            ephemeral=True
        )

# ---------------- VERIFY VIEW ----------------
class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Пройти верификацию",
        style=discord.ButtonStyle.green,
        custom_id="verify_btn"
    )
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VerifyModal())

# ---------------- ON READY ----------------
@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

    bot.add_view(VerifyView())

    channel = await bot.fetch_channel(VERIFY_CHANNEL_ID)

    embed = discord.Embed(
        title="Верификация",
        description="Нажмите кнопку для получения доступа",
        color=discord.Color.green()
    )

    await channel.send(embed=embed, view=VerifyView())

# ---------------- PROFILE ----------------
@bot.tree.command(name="profile", description="Ваш профиль")
async def profile(interaction: discord.Interaction):

    users = load_users()
    uid = str(interaction.user.id)

    if uid not in users:
        return await interaction.response.send_message(
            "Сначала пройдите верификацию",
            ephemeral=True
        )

    nickname = users[uid]["nickname"]
    elo = users[uid]["elo"]

    sorted_users = sorted(users.items(), key=lambda x: x[1]["elo"], reverse=True)
    rating = next((i + 1 for i, (u, _) in enumerate(sorted_users) if u == uid), 0)

    # -------- FILES CHECK --------
    print("BASE_DIR =", BASE_DIR)
    print("FILES =", os.listdir(BASE_DIR))
    background = os.path.join(BASE_DIR, "Без названия7_20260612001021.png")

    if not os.path.exists(background):
        return await interaction.response.send_message(
            "❌ Нет файла фона",
            ephemeral=True
        )

    font_path = os.path.join(BASE_DIR, "NextExitRounded-Black.74b2cd1cc673040ad8c21110e711f52b.ttf")

    if not os.path.exists(font_path):
        return await interaction.response.send_message(
            "❌ Нет файла шрифта",
            ephemeral=True
        )

    # -------- IMAGE --------
    img = Image.open(background)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, 50)

    draw.text((120, 110), f"Nickname: {nickname}", font=font, fill="white")
    draw.text((120, 190), f"ELO: {elo}", font=font, fill="white")
    draw.text((120, 270), f"RANK: #{rating}", font=font, fill="white")

    out = f"profile_{uid}.png"
    img.save(out)

    file = discord.File(out, filename="profile.png")

    embed = discord.Embed(title="Профиль", color=discord.Color.orange())
    embed.set_image(url="attachment://profile.png")

    await interaction.response.send_message(embed=embed, file=file)

    os.remove(out)

# ---------------- RUN ----------------
bot.run(TOKEN)

# ----------------COMMAND--------------

@bot.tree.command(
    name="leaderboard",
    description="Топ игроков по ELO"
)
async def leaderboard(interaction: discord.Interaction):

    users = load_users()

    if not users:
        await interaction.response.send_message(
            "Нет игроков."
        )
        return

    top = sorted(
        users.items(),
        key=lambda x: x[1]["elo"],
        reverse=True
    )[:10]

    text = ""

    for i, (uid, data) in enumerate(top, start=1):
        text += f"**#{i}** {data['nickname']} — {data['elo']} ELO\n"

    embed = discord.Embed(
        title="🏆 Топ игроков",
        description=text,
        color=discord.Color.orange()
    )

await interaction.response.send_message(
        embed=embed
    )
    
@bot.tree.command(
    name="rank",
    description="Показать место в рейтинге"
)
async def rank(interaction: discord.Interaction):

    users = load_users()
    uid = str(interaction.user.id)

    if uid not in users:
        await interaction.response.send_message(
            "Сначала пройдите верификацию.",
            ephemeral=True
        )
        return

    sorted_users = sorted(
        users.items(),
        key=lambda x: x[1]["elo"],
        reverse=True
    )

    position = next(
        (
            i + 1
            for i, (u, _) in enumerate(sorted_users)
            if u == uid
        ),
        0
    )

    await interaction.response.send_message(
        f"🏆 Ваше место: **#{position}**"
    )


@bot.tree.command(
    name="addelo",
    description="Выдать ELO"
)
async def addelo(
    interaction: discord.Interaction,
    member: discord.Member,
    amount: int
):

    if MOD_ROLE_ID not in [r.id for r in interaction.user.roles]:
        await interaction.response.send_message(
            "❌ Нет доступа.",
            ephemeral=True
        )
        return

    users = load_users()
    uid = str(member.id)

    if uid not in users:
        await interaction.response.send_message(
            "Игрок не зарегистрирован."
        )
        return

    users[uid]["elo"] += amount

    save_users(users)

    await interaction.response.send_message(
        f"✅ {member.mention} получил {amount} ELO"
    )
    
    
    @bot.tree.command(
    name="removeelo",
    description="Снять ELO"
)
async def removeelo(
    interaction: discord.Interaction,
    member: discord.Member,
    amount: int
):

    if MOD_ROLE_ID not in [r.id for r in interaction.user.roles]:
        await interaction.response.send_message(
            "❌ Нет доступа.",
            ephemeral=True
        )
        return

    users = load_users()
    uid = str(member.id)

    if uid not in users:
        await interaction.response.send_message(
            "Игрок не зарегистрирован."
        )
        return

    users[uid]["elo"] = max(
        0,
        users[uid]["elo"] - amount
    )

    save_users(users)

    await interaction.response.send_message(
        f"✅ У {member.mention} снято {amount} ELO"
    )
    
    @bot.tree.command(name="profile", description="Ваш профиль")
async def profile(interaction: discord.Interaction):

    users = load_users()
    uid = str(interaction.user.id)

    if uid not in users:
        return await interaction.response.send_message(
            "❌ Сначала пройдите верификацию",
            ephemeral=True
        )

    nickname = users[uid]["nickname"]
    game_id = users[uid]["game_id"]
    elo = users[uid]["elo"]

    sorted_users = sorted(
        users.items(),
        key=lambda x: x[1]["elo"],
        reverse=True
    )

    place = next(
        (i + 1 for i, (u, _) in enumerate(sorted_users) if u == uid),
        0
    )

    background_path = "background.PNG"
    font_path = "font.ttf"

    if not os.path.exists(background_path):
        return await interaction.response.send_message(
            "❌ background.PNG не найден",
            ephemeral=True
        )

    if not os.path.exists(font_path):
        return await interaction.response.send_message(
            "❌ font.ttf не найден",
            ephemeral=True
        )

    img = Image.open(background_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    font_big = ImageFont.truetype(font_path, 55)
    font_medium = ImageFont.truetype(font_path, 40)
    font_small = ImageFont.truetype(font_path, 32)

    draw.text(
        (120, 120),
        nickname,
        font=font_big,
        fill="white"
    )

    draw.text(
        (120, 220),
        f"ELO: {elo}",
        font=font_medium,
        fill="#ff6b00"
    )

    draw.text(
        (120, 300),
        f"ID: {game_id}",
        font=font_small,
        fill="white"
    )

    draw.text(
        (120, 370),
        f"TOP #{place}",
        font=font_small,
        fill="white"
    )

    filename = f"profile_{uid}.png"

    img.save(filename)

    file = discord.File(
        filename,
        filename="profile.png"
    )

    embed = discord.Embed(
        title=f"Профиль {nickname}",
        color=discord.Color.orange()
    )

    embed.set_image(
        url="attachment://profile.png"
    )

    await interaction.response.send_message(
        embed=embed,
        file=file
    )

    os.remove(filename)
    
    
    