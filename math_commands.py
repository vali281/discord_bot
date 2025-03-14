import discord
import re

async def handle_math_command(message):
    try:
        # Extract the math expression (everything after '!math')
        expression = message.content[len('!math '):].strip()

        # Validate the expression (only numbers and basic operators allowed)
        if not re.match(r'^[\d+\-*/().\s]+$', expression):
            await message.reply("Invalid expression! Please use numbers and basic operators (+, -, *, /).")
            return

        # Calculate the result safely using eval
        result = eval(expression)

        # Ensure the result is rounded to 2 decimal places if needed
        if isinstance(result, float):
            result = round(result, 2)

        # Reply to the user with the result
        await message.reply(f"{result}")

    except ZeroDivisionError:
        await message.reply("Error: Division by zero is not allowed.")
    except Exception as e:
        await message.reply(f"Invalid calculation! Error: {str(e)}")
 # type: ignore