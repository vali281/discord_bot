import discord
import random
from discord.ui import View, Button
from database import update_score

class TicTacToeButton(discord.ui.Button):
    def __init__(self, label, row, col):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, row=row)
        self.row = row
        self.col = col

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if view.board[self.row][self.col] == "":
            view.board[self.row][self.col] = "O" if view.current_turn == "user" else "X"
            self.label = "⭕" if view.current_turn == "user" else "❌"
            self.disabled = True

            if view.check_winner():
                await view.end_game(interaction)
                return

            view.current_turn = "bot" if view.current_turn == "user" else "user"
            if view.current_turn == "bot":
                await view.bot_move(interaction)
            else:
                await interaction.response.edit_message(view=view)

class TicTacToeView(View):
    def __init__(self, user, client):
        super().__init__()
        self.user = user
        self.client = client
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_turn = "user"
        self.create_buttons()

    def create_buttons(self):
        for row in range(3):
            for col in range(3):
                self.add_item(TicTacToeButton(str(row * 3 + col + 1), row, col))

    def check_winner(self):
        for row in self.board:
            if row.count(row[0]) == 3 and row[0] != "":
                return True
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != "":
                return True
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != "":
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != "":
            return True
        return False

    async def bot_move(self, interaction):
        empty_cells = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
        if empty_cells:
            row, col = random.choice(empty_cells)
            self.board[row][col] = "X"
            for button in self.children:
                if isinstance(button, TicTacToeButton) and button.row == row and button.col == col:
                    button.label = "❌"
                    button.disabled = True
                    break

            if self.check_winner():
                await self.end_game(interaction, bot_wins=True)
                return

            self.current_turn = "user"
        await interaction.response.edit_message(view=self)

    async def end_game(self, interaction, bot_wins=False):
        if bot_wins:
            update_score(self.user.id, points=1, won=False)
            await interaction.response.edit_message(content=f"Bot wins! 😢", view=None)
        else:
            update_score(self.user.id, points=1, won=True)
            await interaction.response.edit_message(content=f"Congratulations {self.user.mention}, you win! 🎉", view=None)

async def start_game(message, client):
    view = TicTacToeView(message.author, client)
    await message.channel.send(f"Starting Tic-Tac-Toe! {message.author.mention} vs Bot!", view=view)