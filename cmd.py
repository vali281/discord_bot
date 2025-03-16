import discord
import random
from database import add_user, get_user_data, update_score, get_leaderboard
from game import start_game
from log import log_command
from wiki import fetch_wiki_summary
from fandom_api import fetch_fandom_summary
from math_commands import handle_math_command
from forward import get_forward_channel , save_forward_data , load_forward_data
from purge import purge_messages
from discord.ui import Button, View
import aiohttp
import io
from PIL import Image


prefix = '!'

async def handle_commands(message, client):
    # Ignore messages without prefix
    if not message.content.startswith(prefix) or message.author.bot:
        return

    # If bot is mentioned directly
    if client.user in message.mentions and message.content.strip() == f'<@{client.user.id}>':
        await message.reply(f'Hello! {message.author.mention}')
        return

    # Log the command
    log_command(message.author.id, message.author.name, message.channel.id, message.content)

    # Extract command
    command = message.content[len(prefix):].strip().lower()

    if command == "ping":
        latency = round(client.latency * 1000)  # Convert to milliseconds
        await message.channel.send(f"Pong! 🏓 `{latency}ms`")



    elif command == "hello":
        await message.channel.send("Hello!")

    elif command == "start":
        user_id = message.author.id
        username = str(message.author)
        add_user(user_id, username)
        await message.channel.send(f'Hello!! <@{user_id}>, Let\'s start the game!')
        await start_game(message, client)

    elif command.startswith("math "):
        await handle_math_command(message)

    elif command.startswith("purge "):
        args = command[len("purge"):].strip()
        await purge_messages(message, args)

    elif command == "leaderboard":
        leaderboard = get_leaderboard()
        if not leaderboard:
            await message.channel.send("No data available for the leaderboard.")
            return
        embed = discord.Embed(title="🏆 Leaderboard", color=discord.Color.gold())
        for idx, (username, points, wins, losses) in enumerate(leaderboard, start=1):
            embed.add_field(
                name=f'#{idx} {username}',
                value=f'Points: {points} | Wins: {wins} | Losses: {losses}',
                inline=False
            )
        await message.channel.send(embed=embed)

    elif command.startswith("say "):
        message_content = command[4:].strip()
        if message_content:
            await message.channel.send(message_content)
        else:
            await message.reply("Usage: `!say <message>`")

    elif command.startswith("setmessage"):
        try:
            _, channel_id = command.split(" ", 1)
            data = load_forward_data()
            data[str(message.guild.id)] = str(channel_id.strip())  # Store in JSON format
            save_forward_data(data)
            await message.channel.send(f"✅ Forward channel set to <#{channel_id.strip()}>!")
        except ValueError:
            await message.channel.send("❌ Invalid format! Use: `!setmessage <channel_id>`")

    elif command == "star":
        if not message.reference:
            await message.channel.send("Reply to a message to star it!")
        else:
            channel_id = get_forward_channel(message.guild.id)
            if not channel_id:
                await message.channel.send("Please set a channel first using `!setmessage <channel_id>`.")
                return
            channel = message.guild.get_channel(int(channel_id))
            if not channel:
                await message.channel.send("The set channel no longer exists. Please set a new one.")
                return
            replied_message = await message.channel.fetch_message(message.reference.message_id)
            jump_url = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{replied_message.id}"

            # Default color
            embed_color = discord.Color.gold()
            image_url = None

            # Check for image attachments
            if replied_message.attachments:
                for attachment in replied_message.attachments:
                    if attachment.content_type and attachment.content_type.startswith("image"):
                        image_url = attachment.url
                        # Use the average color of the image
                        try:
                            async with aiohttp.ClientSession() as session:
                                async with session.get(image_url) as resp:
                                    img_data = await resp.read()
                            img = Image.open(io.BytesIO(img_data))
                            img = img.convert("RGB")
                            img = img.resize((1, 1))  # Resize to 1px to get average color
                            dominant_color = img.getpixel((0, 0))
                            embed_color = discord.Color.from_rgb(*dominant_color)
                        except:
                            pass  # Fall back to default color if error occurs
                        break

            # Create embed
            embed = discord.Embed(
                description=replied_message.content or None,
                color=embed_color,
                timestamp=replied_message.created_at
            )
            embed.set_author(
                name=replied_message.author.display_name,
                icon_url=replied_message.author.avatar.url if replied_message.author.avatar else None
            )

            # Add image if present
            if image_url:
                embed.set_image(url=image_url)

            # Create simple button
            view = View()
            view.add_item(Button(label="Jump to Message", url=jump_url, style=discord.ButtonStyle.link))

            # Send to starboard
            await channel.send(
                f"⭐ **Starred message by {replied_message.author.mention}:**",
                embed=embed,
                view=view
            )
            await message.channel.send("Message has been starred! ✅")
            
    elif command.startswith("repli "):
        try:
            incmd = command[6:].strip()
            left, right = incmd.split(",", 1)
            lf = int(left.strip())
            rt = right.strip()

            if lf <= 0:
                await message.channel.send("❌ The repeat count must be greater than 0.")
                return
            if not rt:
                await message.channel.send("⚠️ Please provide a message to repeat.")
                return

            # Spam prevention: Limit to 10 repetitions
            for _ in range(min(lf, 10)):
                await message.channel.send(rt)

        except (ValueError, IndexError):
            await message.channel.send("❌ Invalid format! Use: `!repli <n>, <message>`")

    elif command.startswith("msg "):
        try:
            msg_command = command[4:].strip()
            channel_id = None
            user_id = None
            msg_content = ""

            parts = msg_command.split()
            for part in parts:
                if part.startswith('c'):
                    channel_id = int(part[1:])
                elif part.startswith('u'):
                    user_id = int(part[1:])
                else:
                    msg_content = " ".join(parts[parts.index(part):])
                    break

            channel = client.get_channel(channel_id)
            if channel is None:
                await message.channel.send("❌ Invalid channel ID!")
                return

            if user_id:
                msg_content = f"<@{user_id}> {msg_content}"

            if not msg_content.strip():
                await message.channel.send("⚠️ Please provide a message to send.")
                return

            await channel.send(msg_content)
            await message.channel.send(f"✅ Message sent to <#{channel_id}>!")
        
        except (ValueError, IndexError):
            await message.channel.send("❌ Invalid format! Use one of the following:\n"
                                       "• `!msg c<channelid> u<userid> <message>`\n"
                                       "• `!msg c<channelid> <message>`\n"
                                       "• `!msg c<channelid> u<userid>")


    elif command.startswith("bonk"):
        try:
            bonk_command = command[5:].strip()
            channel_id, bonk_message = bonk_command.split(" ", 1)
            channel = client.get_channel(int(channel_id.strip()))
            if not channel:
                await message.channel.send("❌ Invalid channel ID!")
                return
            await channel.send(bonk_message)
            await message.channel.send(f'✅ Message sent to <#{channel_id}>!')
        except (ValueError, IndexError):
            await message.channel.send("❌ Invalid format! Use: `!bonk <channel_id> <message>`")

    elif command == "points":
        user_data = get_user_data(message.author.id)
        if user_data:
            points, wins, losses = user_data
            await message.channel.send(f'<@{message.author.id}>\'s Points: {points}, Wins: {wins}, Losses: {losses}')
        else:
            await message.channel.send("You have no game history yet.")

    elif command == "pin":
        if message.reference:
            replied_message = await message.channel.fetch_message(message.reference.message_id)
            try:
                await replied_message.pin()
                await message.reply("📌 Message pinned successfully!", delete_after=60)
            except discord.Forbidden:
                await message.reply("I don't have permission to pin messages in this channel.")
            except discord.HTTPException:
                await message.reply("Failed to pin the message.")
        else:
            await message.reply("Please reply to a message you want to pin.")

    elif command.startswith("roll "):
        try:
            _, faces = command.split(" ", 1)
            faces = int(faces.strip())
            if faces < 1:
                raise ValueError
            result = random.randint(1, faces)
            await message.reply(f"🎲 You rolled a {faces}-sided dice and got: **{result}**!")
        except (ValueError, IndexError):
            await message.reply("Please use the proper command: `!roll <number>`")

    elif command.startswith("wiki "):
        parts = command.split(" ", 1)
        if len(parts) == 2:
            topic = parts[1].strip()
            embed = await fetch_wiki_summary(topic)
            if embed:
                await message.reply(embed=embed)
            else:
                await message.reply(f"{message.author.mention} No results found for '{topic}'.")
        else:
            await message.reply(f"{message.author.mention} Please use the proper command: `!wiki <topic>`")

    elif command == "help":
        embed = discord.Embed(title="📜 Bot Commands", description="Here is a list of available commands:", color=discord.Color.blue())
        embed.add_field(name="🔹 General Commands", value="`!hello` - Replies with Hello!\n`!ping` - Shows bot latency.\n`!help` - Displays this help message.", inline=False)
        embed.add_field(name="🎮 Game Commands", value="`!start` - Starts a game of Tic-Tac-Toe.\n`!leaderboard` - Displays top users sorted by points.\n`!points` - Shows your points, wins, and losses.", inline=False)
        embed.add_field(name="🛠️ Utility Commands", value="`!say <message>` - Repeats your message.\n`!repli <n>, <message>` - Repeats a message n times (max 10).\n`!math <operation>` - Performs basic arithmetic.\n`!msg c<channelid> u<userid> <message>` - Sends a message to the specified channel mentioning the user.\n`!bonk <channel_id> <message>` - Sends a message to the specified channel", inline=False)
        embed.add_field(name="⭐ Starboard & Moderation", value="`!setmessage <channel_id>` - Sets forward channel for starred messages.\n`!star` - Stars a replied-to message.\n`!pin` - Pins a message.\n`!purge <number>` - Deletes messages.", inline=False)
        embed.set_footer(text="Use these commands wisely!")
        await message.channel.send(embed=embed)
 # type: ignore