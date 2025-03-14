import discord

async def purge_messages(message, amount):
    try:
        amount = int(amount)
        if amount < 1:
            await message.channel.send("Please provide a number greater than 0.")
            return
        
        deleted = await message.channel.purge(limit=amount + 1)  # +1 to include the command message itself
        
        # Send an ephemeral-like confirmation (deletes after 1 minute)
        confirmation = await message.author.send(f"✅ Purged {len(deleted) - 1} messages in #{message.channel.name}.")
        await confirmation.delete(delay=60)  # Deletes after 1 minute
    
    except ValueError:
        await message.channel.send("Invalid number! Use: `!purge <number>`")
    except discord.Forbidden:
        await message.channel.send("I don't have permission to delete messages.")
    except discord.HTTPException:
        await message.channel.send("Failed to delete messages. Please try again.")
