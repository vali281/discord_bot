import discord

async def create_poll(message, question: str, *options: str):
    """Creates a poll with up to 9 options using reactions."""
    if len(options) < 2:
        await message.channel.send("❌ You need at least 2 options for a poll!")
        return
    if len(options) > 9:
        await message.channel.send("❌ Polls can have a maximum of 9 options!")
        return

    # Number emojis for options
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

    # Construct embed
    embed = discord.Embed(title="📊 Poll", description=f"**{question}**", color=discord.Color.blue())
    for i, option in enumerate(options):
        embed.add_field(name=f"{emojis[i]} {option}", value="\u200b", inline=False)

    # Send the embed and get the message object
    poll_message = await message.channel.send(embed=embed)

    # React with number emojis
    for i in range(len(options)):
        await poll_message.add_reaction(emojis[i])