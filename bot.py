import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

# Проверка работы бота
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

# Приветствие
@bot.command()
async def hello(ctx):
    await ctx.send(f"Привет, {ctx.author.mention}!")

# Информация о сервере
@bot.command()
async def server(ctx):
    await ctx.send(f"Сервер: {ctx.guild.name}")

# Аватар пользователя
@bot.command()
async def avatar(ctx):
    await ctx.send(ctx.author.display_avatar.url)

# Очистка сообщений
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"Удалено {amount} сообщений.")
    await msg.delete(delay=3)

# Кик участника
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Без причины"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.mention} был кикнут. Причина: {reason}")

# Бан участника
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Без причины"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.mention} был забанен. Причина: {reason}")

# Обработка ошибок
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ У тебя нет прав для этой команды.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Не хватает аргументов.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Участник не найден.")
    else:
        print(error)

print("TOKEN =", TOKEN)

bot.run(TOKEN)