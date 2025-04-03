# bot.py - Initializes the bot, reads the token from .env, listens for messages, and processes commands.
import sys
import discord
import os
from discord.ext import commands
from database import add_user, get_user_data  # Import database functions
from dotenv import load_dotenv  # Load environment variables
from commands_handler import handle_commands  # Import your command handler

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TOKEN")

sys.stdout.reconfigure(encoding='utf-8')

if not TOKEN:
    print("Error: TOKEN not found in environment variables or .env file.")
    exit(1)

# Initialize bot with command prefix and intents
intents = discord.Intents.default()
intents.typing = False
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    print("📌 Connected to the following servers:")
    for guild in bot.guilds:
        print(f"- {guild.name} (ID: {guild.id})")
    await bot.change_presence(activity=discord.Streaming(
        name="Youtube Raikun_vali",
        url="https://www.youtube.com/c/Raikun_vali"
    ))  # Streaming status

@bot.event
async def on_guild_join(guild):
    """Sends a welcome message when the bot joins a new server"""
    system_channel = guild.system_channel
    if system_channel is not None:
        await system_channel.send("Hello! Thanks for inviting me! 🎉")

@bot.event
async def on_message(message):
    """Handles messages and commands"""
    if message.author == bot.user or message.author.bot:
        return  # Ignore bot messages

    # Process registered commands first
    await bot.process_commands(message)

    # If the message starts with "!", check custom commands
    if message.content.startswith("!"):
        user_id = message.author.id
        username = str(message.author)
        add_user(user_id, username)  # Add user to database

        handled = await handle_commands(message, bot)  # Custom command handling
        if not handled:
            pass  # Ignore unknown commands

@bot.event
async def on_command_error(ctx, error):
    """Ignore unknown command errors to prevent spam in logs"""
    if isinstance(error, commands.CommandNotFound):
        return  # Suppress 'command not found' errors
    raise error  # Raise other errors normally

try:
    bot.run(TOKEN)
except Exception as err:
    print(f"❌ Error: {err}")
