# in bot.py file initializes the bot , reads the token from token.txt file , listens for the message and replies with the 
# message if it is in the cmd.py
import discord
import os
from discord.ext import commands
from cmd import handle_commands  # Import your command handler
from database import add_user, get_user_data  # Import database functions
from dotenv import load_dotenv  # Load environment variables
from commands_handler import handle_commands  # Updated import to avoid conflict


# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("Error: TOKEN not found in environment variables or .env file.")
    exit(1)

# Initialize bot with command prefix and intents
intents = discord.Intents.default()
intents.typing = False
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    print("📌 Connected to the following servers:")
    for guild in bot.guilds:
        print(f"- {guild.name} (ID: {guild.id})")
    await bot.change_presence(activity=discord.Streaming(name="Youtube Raikun_vali", url="https://www.youtube.com/c/Raikun_vali"))  # Streaming status

@bot.event
async def on_guild_join(guild):
    """Sends a welcome message when the bot joins a new server"""
    system_channel = guild.system_channel
    if system_channel is not None:
        await system_channel.send("Hello! Thanks for inviting me! 🎉")

@bot.event
async def on_message(message):
    """Handles messages and passes them to command handler"""
    if message.author == bot.user or message.author.bot:
        return  # Ignore bot messages

    if message.content.startswith("!"):  # Only process commands
        user_id = message.author.id
        username = str(message.author)
        add_user(user_id, username)  # Add user to database

        await handle_commands(message, bot)  # Handle command
    await bot.process_commands(message)  # Process regular commands

try:
    bot.run(TOKEN)
except Exception as err:
    print(f"❌ Error: {err}")
