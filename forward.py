import json
import discord

FORWARD_FILE = 'forward.txt'

def load_forward_data():
    try:
        with open(FORWARD_FILE, 'r') as file:
            return json.load(file)
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
        description=starred_message.content,
        color=discord.Color.gold(),
        timestamp=starred_message.created_at
    )
    embed.set_author(
        name=starred_message.author.display_name, 
        icon_url=starred_message.author.avatar.url if starred_message.author.avatar else None
    )

    # Add image from attachments or embeds
    if starred_message.attachments:
        embed.set_image(url=starred_message.attachments[0].url)
    elif starred_message.embeds:
        if starred_message.embeds[0].image:
            embed.set_image(url=starred_message.embeds[0].image.url)
        elif starred_message.embeds[0].thumbnail:
            embed.set_thumbnail(url=starred_message.embeds[0].thumbnail.url)

    # Add Jump to Message button
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Jump to Message", url=starred_message.jump_url, style=discord.ButtonStyle.link))

    await forward_channel.send(f"⭐ **Starred message by {starred_message.author.mention}:**", embed=embed, view=view)
    await message.channel.send("Message has been starred! ✅")
