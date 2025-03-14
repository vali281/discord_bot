# in bot.py file initializes the bot , reads the token from token.txt file , listens for the message and replies with the 
# message if it is in the cmd.py
import discord, os # Import the discord.py module
from cmd import handle_commands # type: ignore # Import commands handler
from database import add_user, get_user_data # For database interaction


intents = discord.Intents.default()
intents.typing = False
intents.members = True
intents.message_content = True
intents.guilds = True

# Try to get the token from environment variables
token = os.getenv('DISCORD_TOKEN')

# If the environment variable is not set, use the Token.txt file
if not token:
    try:
        with open('Token.txt', 'r') as file:
            token = file.read().strip()
    except FileNotFoundError:
        print("Error: No token found. Please set DISCORD_TOKEN or provide Token.txt.")
        exit(1)


#initialize the bot using intents 
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_guild_join(guild):
    """Sends a welcome message when the bot joins a new server"""
    system_channel = guild.system_channel  # Gets the default system channel (if available)
    if system_channel is not None:
        await system_channel.send("Hello! Thanks for inviting me! 🎉")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    user_id = message.author.id
    username = str(message.author)
    add_user(user_id, username)

    await handle_commands(message, client) # type: ignore

try:
    client.run(token)
except Exception as err:
    raise err
