import json
import discord
from discord.ui import Button, View

FORWARD_FILE = 'forward.txt'

def load_forward_data():
    try:
        with open(FORWARD_FILE, 'r') as file:
            content = file.read().strip()
            if content.isdigit():  # If file contains only a number, convert it
                return { "default": content }
            return json.loads(content)  # Try to load JSON if possible
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_forward_data(data):
    with open(FORWARD_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def set_forward_channel(guild_id, channel_id):
    data = load_forward_data()
    data[str(guild_id)] = str(channel_id)
    save_forward_data(data)

def get_forward_channel(guild_id):
    data = load_forward_data()
    return data.get(str(guild_id))

class JumpToMessageButton(View):
    def __init__(self, message_link):
        super().__init__()
        self.add_item(Button(label="Jump to Message", url=message_link, style=discord.ButtonStyle.link))

async def star_message(message, client):
    if not message.reference:
        await message.channel.send("Reply to a message to star it!")
        return
    
    starred_message = await message.channel.fetch_message(message.reference.message_id)
    forward_channel_id = get_forward_channel(message.guild.id)
    
    if not forward_channel_id:
        await message.channel.send("Starboard channel not set!")
        return
    
    forward_channel = client.get_channel(int(forward_channel_id))
    
    if not forward_channel:
        await message.channel.send("Invalid starboard channel!")
        return

    embed = discord.Embed(
        description=starred_message.content if starred_message.content else None,
        color=discord.Color.gold(),
        timestamp=starred_message.created_at
    )
    embed.set_author(
        name=starred_message.author.display_name, 
        icon_url=starred_message.author.avatar.url if starred_message.author.avatar else None
    )

    # Add first image from attachments if available
    if starred_message.attachments:
        for attachment in starred_message.attachments:
            if attachment.content_type.startswith("image"):  # Ensuring it's an image
                embed.set_image(url=attachment.url)
                break  # Only add the first image

    # Copy embeds if they exist
    for e in starred_message.embeds:
        new_embed = discord.Embed.from_dict(e.to_dict())  # Copy entire embed
        await forward_channel.send(embed=new_embed)

    message_link = f"https://discord.com/channels/{starred_message.guild.id}/{starred_message.channel.id}/{starred_message.id}"

    await forward_channel.send(
        f"⭐ **Starred message by {starred_message.author.mention}:**",
        embed=embed,
        view=JumpToMessageButton(message_link)
    )
