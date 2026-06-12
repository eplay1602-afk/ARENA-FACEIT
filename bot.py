import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import json
import os

TOKEN = os.getenv("TOKEN")

VERIFY_CHANNEL_ID = 1514680391745667082
VERIFIED_ROLE_ID = 1514679192321658950
MOD_ROLE_ID = 1514883779204743280

START_ELO = 100

DATA_FILE = "users.json"

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

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ---------------- VERIFY MODAL ----------------

class VerifyModal(discord.ui.Modal, title="Верификация"):

    player_id = discord.ui.TextInput(
        label="Игровой ID",
        placeholder="Только цифры",
        required=True,
        max_length=20
    )

    nickname = discord.ui.TextInput(
        label="Никнейм",
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):

        users = load_users()
        uid = str(interaction.user.id)

        # Уже зарегистрирован
        if uid in users:
            await interaction.response.send_message(
                "❌ Вы уже прошли верификацию.",
                ephemeral=True
            )
            return

        player_id = self.player_id.value.strip()

        if not player_id.isdigit():
            await interaction.response.send_message(
                "❌ ID должен содержать только цифры.",
                ephemeral=True
            )
            return

        if len(player_id) < 6:
            await interaction.response.send_message(
                "❌ ID должен быть минимум 6 цифр.",
                ephemeral=True
            )
            return

        role = interaction.guild.get_role(VERIFIED_ROLE_ID)

        if role:
            await interaction.user.add_roles(role)

        users[uid] = {
            "nickname": self.nickname.value,
            "player_id": player_id,
            "elo": START_ELO,
            "wins": 0,
            "losses": 0,
            "matches": 0,
            "registered": datetime.now().strftime("%d.%m.%Y")
        }

        save_users(users)

        await interaction.response.send_message(
            "✅ Верификация успешно пройдена.",
            ephemeral=True
        )

# ---------------- VERIFY BUTTON ----------------

class VerifyView(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Пройти верификацию",
        style=discord.ButtonStyle.green,
        custom_id="verify_button"
    )
    async def verify(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            VerifyModal()
        )

# ---------------- READY ----------------

@bot.event
async def on_ready():

    print(f"Bot online: {bot.user}")

    bot.add_view(VerifyView())

    try:
        synced = await bot.tree.sync()
        print(f"Команд синхронизировано: {len(synced)}")
    except Exception as e:
        print(e)
# ---------------- PROFILE ----------------
bot.run(TOKEN)
@bot.tree.command(
    name="profile",
    description="Показать профиль игрока"
)
async def profile(interaction: discord.Interaction):

    users = load_users()
    uid = str(interaction.user.id)

    if uid not in users:
        await interaction.response.send_message(
            "❌ Сначала пройдите верификацию.",
            ephemeral=True
        )
        return

    user = users[uid]

    nickname = user["nickname"]
    player_id = user["player_id"]
    elo = user["elo"]
    wins = user["wins"]
    losses = user["losses"]
    matches = user["matches"]
    reg_date = user["registered"]

    sorted_users = sorted(
        users.items(),
        key=lambda x: x[1]["elo"],
        reverse=True
    )

    rank = next(
        (
            i + 1
            for i, (u, _) in enumerate(sorted_users)
            if u == uid
        ),
        0
    )

    # Ранги

    if elo >= 2500:
        rank_name = "DIAMOND"
    elif elo >= 2000:
        rank_name = "PLATINUM"
    elif elo >= 1500:
        rank_name = "GOLD"
    elif elo >= 1000:
        rank_name = "SILVER"
    else:
        rank_name = "BRONZE"

    background_path = "background.PNG"
    font_path = "font.ttf"

    if not os.path.exists(background_path):
        await interaction.response.send_message(
            "❌ Файл background.PNG не найден.",
            ephemeral=True
        )
        return

    if not os.path.exists(font_path):
        await interaction.response.send_message(
            "❌ Файл font.ttf не найден.",
            ephemeral=True
        )
        return

    try:

        img = Image.open(background_path).convert("RGBA")

        draw = ImageDraw.Draw(img)

        title_font = ImageFont.truetype(font_path, 55)
        text_font = ImageFont.truetype(font_path, 35)

        draw.text(
            (90, 80),
            nickname,
            font=title_font,
            fill="white"
        )

        draw.text(
            (90, 170),
            f"ELO: {elo}",
            font=text_font,
            fill="#ff7b00"
        )

        draw.text(
            (90, 230),
            f"Rank: {rank_name}",
            font=text_font,
            fill="white"
        )

        draw.text(
            (90, 290),
            f"Top #{rank}",
            font=text_font,
            fill="white"
        )

        draw.text(
            (90, 350),
            f"Player ID: {player_id}",
            font=text_font,
            fill="white"
        )

        draw.text(
            (90, 410),
            f"Wins: {wins}",
            font=text_font,
            fill="white"
        )

        draw.text(
            (90, 470),
            f"Losses: {losses}",
            font=text_font,
            fill="white"
        )

        draw.text(
            (90, 530),
            f"Matches: {matches}",
            font=text_font,
            fill="white"
        )

        draw.text(
            (90, 590),
            f"Registered: {reg_date}",
            font=text_font,
            fill="white"
        )

        output = f"profile_{uid}.png"

        img.save(output)

        file = discord.File(
            output,
            filename="profile.png"
        )

        embed = discord.Embed(
            title=f"👤 {nickname}",
            color=discord.Color.orange()
        )

        embed.set_image(
            url="attachment://profile.png"
        )

        await interaction.response.send_message(
            embed=embed,
            file=file
        )

        os.remove(output)

    except Exception as e:

        await interaction.response.send_message(
            f"❌ Ошибка: {e}",
            ephemeral=True
            
        )

# ---------------- RUN ----------------
bot.run(TOKEN)