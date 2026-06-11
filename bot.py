import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Modal, TextInput
from datetime import timedelta
from PIL import Image, ImageDraw, ImageFont
import os
import json

TOKEN = os.getenv("TOKEN")

DATA_FILE = "users.json"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VERIFY_CHANNEL_ID = 1514680391745667082
VERIFIED_ROLE_ID = 1514679192321658950

# ====================
# JSON DATA
# ====================

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)


def load_users():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# =====================
# BOT SETUP
# =====================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# =====================
# VERIFICATION MODAL
# =====================

class VerifyModal(Modal, title="Верификация"):

    player_id = TextInput(label="Игровой ID", required=True)
    nickname = TextInput(label="Ник", required=True)

    async def on_submit(self, interaction: discord.Interaction):

        role = interaction.guild.get_role(VERIFIED_ROLE_ID)

        if role:
            await interaction.user.add_roles(role)

        users = load_users()
        uid = str(interaction.user.id)

        if uid not in users:
            users[uid] = {"nickname": "", "elo": 0}

        users[uid]["nickname"] = self.nickname.value

        save_users(users)

        await interaction.response.send_message(
            f"✅ Верификация пройдена!\nID: {self.player_id.value}\nНик: {self.nickname.value}",
            ephemeral=True
        )


class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Пройти верификацию",
        style=discord.ButtonStyle.green,
        custom_id="verify_button"
    )
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VerifyModal())


# =====================
# READY EVENT
# =====================

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

    bot.add_view(VerifyView())

    try:
        channel = await bot.fetch_channel(VERIFY_CHANNEL_ID)

        embed = discord.Embed(
            title="Верификация",
            description="Нажмите кнопку ниже для доступа к серверу",
            color=discord.Color.green()
        )

        await channel.send(embed=embed, view=VerifyView())

        print("Verification message sent")

    except Exception as e:
        print("Error:", e)


# =====================
# PROFILE COMMAND
# =====================

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

    rating = 0
    for i, (user_id, data) in enumerate(sorted_users, start=1):
        if user_id == uid:
            rating = i
            break

    background = os.path.join(BASE_DIR, "Без названия7_20260612001021.png")

    if not os.path.exists(background):
        return await interaction.response.send_message(
            "Фон не найден",
            ephemeral=True
        )

    img = Image.open(background)
    draw = ImageDraw.Draw(img)

    font = ImageFont.load_default()

    draw.text((120, 110), f"Nickname: {nickname}", fill="white", font=font)
    draw.text((120, 190), f"ELO: {elo}", fill="white", font=font)
    draw.text((120, 270), f"RATING: #{rating}", fill="white", font=font)

    image_path = f"profile_{uid}.png"
    img.save(image_path)

    file = discord.File(image_path, filename="profile.png")

    embed = discord.Embed(title="Ваш профиль", color=discord.Color.orange())
    embed.set_image(url="attachment://profile.png")

    await interaction.response.send_message(embed=embed, file=file)

    os.remove(image_path)


# =====================
# SIMPLE COMMAND
# =====================

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


# =====================
# RUN
# =====================

bot.run(TOKEN)