import discord
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

GUILD_ID = <guild/server id>  # Replace with the server ID

@bot.event
async def on_ready():
    guild = bot.get_guild(GUILD_ID)
    if guild:
        print(f"Leaving server: {guild.name} ({guild.id})")
        await guild.leave()
        print("✅ Successfully left the server.")
    else:
        print("❌ Bot is not in the specified server.")
    
    await bot.close()  # Close the bot after leaving

bot.run(TOKEN)
