import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View
from datetime import timedelta
from PIL import Image, ImageDraw, ImageFont
import os
import json

TOKEN = os.getenv("TOKEN")

DATA_FILE = "users.json"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VERIFY_CHANNEL_ID = 1514680391745667082
VERIFIED_ROLE_ID = 1514679192321658950

# -------------------------
# JSON HELPERS
# -------------------------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

def load_users():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# -------------------------
# BOT SETUP
# -------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------------
# VERIFY MODAL
# -------------------------
class VerifyModal(discord.ui.Modal, title="Верификация"):

    player_id = discord.ui.TextInput(
        label="Игровой ID",
        required=True
    )

    nickname = discord.ui.TextInput(
        label="Ник",
        required=True
    )

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

# -------------------------
# VERIFY VIEW
# -------------------------
class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Верификация",
        style=discord.ButtonStyle.green,
        custom_id="verify_btn"
    )
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VerifyModal())

# -------------------------
# READY EVENT
# -------------------------
@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

    bot.add_view(VerifyView())

    channel = await bot.fetch_channel(VERIFY_CHANNEL_ID)

    embed = discord.Embed(
        title="Верификация",
        description="Нажмите кнопку ниже",
        color=discord.Color.green()
    )

    await channel.send(embed=embed, view=VerifyView())

# -------------------------
# PROFILE COMMAND
# -------------------------
@bot.tree.command(name="profile")
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

    # ---------------- IMAGE ----------------
background = os.path.join(
    BASE_DIR,
    "Без названия7_20260612001021.png"
)

    if not os.path.exists(background):
        return await interaction.response.send_message(
            "Нет фона",
            ephemeral=True
        )

    img = Image.open(background)
    draw = ImageDraw.Draw(img)

    font_path = os.path.join(BASE_DIR, "NextExitRounded-Black.ttf")

    if not os.path.exists(font_path):
        return await interaction.response.send_message(
            "Нет шрифта",
            ephemeral=True
        )

    font = ImageFont.truetype(font_path, 50)

    draw.text((120, 110), f"Nickname: {nickname}", font=font, fill="white")
    draw.text((120, 190), f"ELO: {elo}", font=font, fill="white")
    draw.text((120, 270), f"RANK: #{rating}", font=font, fill="white")

    path = f"profile_{uid}.png"
    img.save(path)

    file = discord.File(path, filename="profile.png")

    embed = discord.Embed(title="Профиль", color=discord.Color.orange())
    embed.set_image(url="attachment://profile.png")

    await interaction.response.send_message(embed=embed, file=file)

    os.remove(path)

# -------------------------
# RUN
# -------------------------
bot.run(TOKEN)