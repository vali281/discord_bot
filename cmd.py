import discord
from database import add_user, get_user_data, update_score, get_leaderboard
from game import start_game
from log import log_command

prefix = '!'

async def handle_commands(message,client):
    if not message.content.startswith(prefix):
        return

    command = message.content[len(prefix):].strip().lower()

    # Log the command
    log_command(message.author.id, message.author.name, message.channel.id, message.content)

    command = message.content[len(prefix):].strip().lower()

    if command == 'hello':
        await message.channel.send('Hello!')


    if command == 'ping':
        await message.channel.send('pong!')

    
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


    if 'help' in command:
        await message.channel.send(
            "```Commands:\n"
            "!hello - Replies with Hello!\n"
            "!ping - Replies with pong!\n"
            "!start - Starts the game of Tick tack toe\n"
            "!say <message> - Repeats the message\n"
            "!leaderboard - Displays the top 10 users sorted by points\n"
            "!points - Displays your points, wins, and losses\n"
            "!msg c<channelid> u<userid> <message> - Sends a message to the specified channel mentioning the user\n"
            "!repli <n>, <message> - Repeats the message n times\n"
            "!bonk <channel_id> <message> - Sends a message to the specified channel\n"
            "!help - Displays this message```"
        ) # type: ignore