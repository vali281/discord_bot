import discord
from discord.ui import Button, View

class RoleView(View):
    def __init__(self, roles, single_select=False, timeout=300):
        super().__init__(timeout=timeout)
        self.single_select = single_select  # True for 'si', False for 'mul'
        self.role_mapping = roles  # Dictionary mapping button labels to role objects
        self.user_roles = {}  # Track user selections: {user_id: set of role_ids}

        # Create buttons for each role option
        for label, role in self.role_mapping.items():
            button = Button(label=label, style=discord.ButtonStyle.primary)
            button.callback = self.create_callback(role)
            self.add_item(button)

    def create_callback(self, role):
        async def callback(interaction: discord.Interaction):
            user = interaction.user
            user_id = user.id
            role_id = role.id

            try:
                # Initialize user's role set if not present
                if user_id not in self.user_roles:
                    self.user_roles[user_id] = set()

                if self.single_select:
                    # Single select: Remove all previous roles, add the new one
                    current_roles = self.user_roles[user_id]
                    for old_role_id in current_roles:
                        old_role = interaction.guild.get_role(old_role_id)
                        if old_role and old_role in user.roles:
                            await user.remove_roles(old_role)
                    # Add the new role
                    if role not in user.roles:
                        await user.add_roles(role)
                    # Update the user's role set
                    self.user_roles[user_id] = {role_id}
                else:
                    # Multiple select: Toggle the role
                    if role in user.roles:
                        await user.remove_roles(role)
                        self.user_roles[user_id].discard(role_id)
                    else:
                        await user.add_roles(role)
                        self.user_roles[user_id].add(role_id)

                # Send success message
                await interaction.response.send_message(
                    f"✅ Successfully gave the role **{role.name}** to {user.mention}!",
                    ephemeral=True
                )

            except discord.Forbidden:
                await interaction.response.send_message(
                    "❌ I don't have permission to manage roles! Please ensure I have the 'Manage Roles' permission.",
                    ephemeral=True
                )
            except discord.HTTPException as e:
                await interaction.response.send_message(
                    f"❌ Failed to update roles: {str(e)}",
                    ephemeral=True
                )
            except Exception as e:
                await interaction.response.send_message(
                    f"❌ An unexpected error occurred: {str(e)}",
                    ephemeral=True
                )

        return callback

async def create_role_selection(message, category: str, options: list, single_select: bool):
    """Creates a role selection message with buttons."""
    if len(options) < 1:
        await message.channel.send("❌ You need at least 1 option for role selection!")
        return
    if len(options) > 25:  # Discord limit for components in a view
        await message.channel.send("❌ Role selection can have a maximum of 25 options!")
        return

    guild = message.guild
    if not guild:
        await message.channel.send("❌ This command can only be used in a server!")
        return

    # Create or find roles for each option
    role_mapping = {}
    for option in options:
        # Check if role exists
        role = discord.utils.get(guild.roles, name=option)
        if not role:
            # Create the role if it doesn't exist
            try:
                role = await guild.create_role(name=option, reason=f"Created for role selection: {category}")
            except discord.Forbidden:
                await message.channel.send(f"❌ I don't have permission to create roles in this server!")
                return
            except discord.HTTPException as e:
                await message.channel.send(f"❌ Failed to create role '{option}': {str(e)}")
                return
        role_mapping[option] = role

    # Construct embed
    embed = discord.Embed(
        title=f"🎭 Role Selection: {category}",
        description="Click the buttons below to select your roles!",
        color=discord.Color.purple()
    )
    for i, option in enumerate(options, 1):
        embed.add_field(name=f"Option {i}: {option}", value="\u200b", inline=False)

    # Create the view with buttons
    view = RoleView(role_mapping, single_select=single_select)

    # Send the embed with buttons
    await message.channel.send(embed=embed, view=view)