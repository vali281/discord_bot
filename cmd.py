import discord
import random
from database import add_user, get_user_data, update_score, get_leaderboard
from game import start_game
from log import log_command
from wiki import fetch_wiki_summary
from fandom_api import fetch_fandom_summary
from math_commands import handle_math_command
from forward import star_message
from purge import purge_messages

prefix = '!'

async def handle_commands(message,client):
    async def ping_command(message, client):
        latency = round(client.latency * 1000)  # Convert seconds to milliseconds
        await message.channel.send(f"Pong! 🏓 `{latency}ms`")
        # If the bot is mentioned without a command
    if client.user in message.mentions and message.content.strip() == f'<@{client.user.id}>':
        await message.reply(f'Hello! {message.author.mention}')
        return

    # Ignore messages that don't start with the prefix
    if not message.content.startswith(prefix):
        return
    
    # Ignore bot messages to prevent duplicate replies
    if message.author.bot:
        return 


    # Log the command
    log_command(message.author.id, message.author.name, message.channel.id, message.content)

    # Get the command without the prefix
    command = message.content[len(prefix):].strip().lower()

    if command.startswith('math'):
        await handle_math_command(message)

    #purge command
    if command.startswith('purge'):
        args = command[len('purge'):].strip()
        await purge_messages(message, args)

    if command == "ping":
        await ping_command(message, client)


    if command == 'star':
        print(f"Processing !star command from {message.author}")  # Debugging

        if not message.reference:
            await message.channel.send("Reply to a message to star it!")
            return

        # Call star_message from forward.py
        await star_message(message, client)



    if command == 'hello':
        await message.channel.send('Hello!')


    if command == 'start':
        user_id = message.author.id
        username = str(message.author)
        
        # Add user to the database if they're new
        add_user(user_id, username)
        
        await message.channel.send(f'Hello!! <@{user_id}>, Let\'s start the game!')
        await start_game(message, client) # type: ignore

    
    if 'say' in command:
        await message.channel.send(command[4:])

    
    if 'repli' in command:
        try:
            incmd=command[6:]
            full = incmd.strip()
            left , right = full.split(',',1)
            lf=int(left.strip())
            rt=right.strip()
            for _ in range(lf):
                await message.channel.send(rt)
        except (ValueError, IndexError):
            await message.channel.send("Invalid format! Use: `!repli <n>, <message>`")

    if 'bonk' in command:
        try:
            bonk_command = command[5:].strip()
            channel_id, bonk_message = bonk_command.split(' ', 1)
            channel_id = int(channel_id.strip())

            channel = client.get_channel(channel_id)
            if channel is None:
                await message.channel.send("Invalid channel ID!")
                return
            
            await channel.send(bonk_message)
            await message.channel.send(f'Message sent to <#{channel_id}>!')
        
        except (ValueError, IndexError):
            await message.channel.send("Invalid format! Use: `!bonk <channel_id> <message>`")
    
    if command == 'points':
        user_data = get_user_data(message.author.id) # type: ignore
        if user_data:
            points, wins, losses = user_data
            await message.channel.send(f'<@{message.author.id}>\'s Points: {points}, Wins: {wins}, Losses: {losses}')
        else:
            await message.channel.send('You have no game history yet.')

    if command == 'leaderboard':
        leaderboard = get_leaderboard()
        if not leaderboard:
            await message.channel.send('No data available for the leaderboard.')
            return
        
        embed = discord.Embed(title='🏆 Leaderboard', color=discord.Color.gold())
        
        for idx, (username, points, wins, losses) in enumerate(leaderboard, start=1):
            embed.add_field(
                name=f'#{idx} {username}',
                value=f'Points: {points} | Wins: {wins} | Losses: {losses}',
                inline=False
            )
        
        await message.channel.send(embed=embed)

    if 'msg' in command:
        try:
            # Remove 'msg' and strip extra whitespace
            msg_command = command[3:].strip()

            # Initialize placeholders
            channel_id = None
            user_id = None
            msg_content = ""

            # Extract channel, user, and message
            parts = msg_command.split()
            for part in parts:
                if part.startswith('c'):
                    channel_id = int(part[1:])
                elif part.startswith('u'):
                    user_id = int(part[1:])
                else:
                    msg_content = " ".join(parts[parts.index(part):])
                    break

            # Get the channel object
            channel = client.get_channel(channel_id)
            if channel is None:
                await message.channel.send("Invalid channel ID!")
                return

            # Format the message with user mention if user_id is provided
            if user_id:
                msg_content = f"<@{user_id}> {msg_content}"

            # Ensure message content is not empty
            if not msg_content.strip():
                await message.channel.send("Please provide a message to send.")
                return

            # Send the message in the specified channel
            await channel.send(msg_content)
            await message.channel.send(f"Message sent to <#{channel_id}>!")
    
        except (ValueError, IndexError):
            await message.channel.send("Invalid format! Use one of the following:\n"
                                   "• `!msg c<channelid> u<userid> <message>`\n"
                                   "• `!msg c<channelid> <message>`\n"
                                   "• `!msg c<channelid> u<userid>`")

    if command.startswith('pin'):
        if message.reference:  # Check if the user replied to a message
            replied_message = await message.channel.fetch_message(message.reference.message_id)
            try:
                await replied_message.pin()  # Pin the replied-to message
                await message.reply("📌 Message pinned successfully!", delete_after=60)
            except discord.Forbidden:
                await message.reply("I don't have permission to pin messages in this channel.")
            except discord.HTTPException:
                await message.reply("Failed to pin the message.")
        else:
            await message.reply("Please reply to a message you want to pin.")

    if command.startswith('roll'):
        try:
            _, faces = command.split(' ', 1)
            faces = int(faces.strip())

            if faces < 1:
                raise ValueError  # Dice can't have less than 1 face

            result = random.randint(1, faces)
            await message.reply(f"🎲 You rolled a {faces}-sided dice and got: **{result}**!")
        
        except (ValueError, IndexError):
            await message.reply(f"Please use the proper command: `!roll <number>`")

    command = message.content[len(prefix):].strip()

    if command.startswith('wiki'):
        parts = command.split(' ', 1)
        if len(parts) == 2:
            topic = parts[1].strip()
            embed = await fetch_wiki_summary(topic)
            if embed:
                await message.reply(embed=embed)
            else:
                await message.reply(f"{message.author.mention} No results found for '{topic}'.")
        else:
            await message.reply(f"{message.author.mention} Please use the proper command: `!wiki <topic>`")

    async def help_command(message):
        embed = discord.Embed(
            title="📜 Bot Commands",
            description="Here is a list of available commands:",
            color=discord.Color.blue()
        )

        embed.add_field(name="🔹 General Commands", value="""
        `!hello` - Replies with Hello!
        `!ping` - Shows bot latency.
        `!help` - Displays this help message.
        """, inline=False)

        embed.add_field(name="🎮 Game Commands", value="""
        `!start` - Starts a game of Tic-Tac-Toe.
        `!leaderboard` - Displays the top 10 users sorted by points.
        `!points` - Shows your points, wins, and losses.
        """, inline=False)

        embed.add_field(name="🛠️ Utility Commands", value="""
        `!say <message>` - Repeats your message.
        `!msg c<channelid> u<userid> <message>` - Sends a message to a specific channel mentioning a user.
        `!repli <number>, <message>` - Repeats a message a specified number of times.
        `!math <operation>` - Performs basic arithmetic (e.g., `!math 600/160`).
        """, inline=False)

        embed.add_field(name="⭐ Starboard & Moderation", value="""
        `!setmessage <channel_id>` - Sets the forward channel for starred messages.
        `!star` - Stars a replied-to message and forwards it to the set channel.
        `!pin` - Pins a message in the channel.
        `!purge <number>` - Deletes a specified number of messages.
        """, inline=False)

        embed.set_footer(text="Use these commands wisely!")
        
        await message.channel.send(embed=embed)

    # Modify your command handler in cmd.py:
    if command == "help":
        await help_command(message)