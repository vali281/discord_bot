import discord
import random
from discord.ui import View, Button
from database import update_score, get_user_data

last_winner = None  # Track the last winner globally

difficulty_levels = {
    'easy': (0, 3),
    'medium': (4, 5),
    'hard': (6, 8),
    'unbeatable': (9, float('inf'))
}

class TicTacToeButton(Button):
    def __init__(self, label, row, col, parent_view):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, row=row)
        self.row = row
        self.col = col
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Prevent 'interaction failed' message
        await self.parent_view.handle_move(interaction, self.row, self.col)

class TicTacToeView(View):
    def __init__(self, player, board, client, difficulty='easy', bot_starts=False):
        super().__init__()
        self.player = player
        self.board = board
        self.client = client
        self.difficulty = difficulty
        self.bot_starts = bot_starts
        self.initialize_buttons()

        if self.bot_starts:
            self.bot_move()
            self.initialize_buttons()

    def initialize_buttons(self):
        self.clear_items()
        for i in range(3):
            for j in range(3):
                label = str(i * 3 + j + 1) if self.board[i][j] == ' ' else self.board[i][j]
                self.add_item(TicTacToeButton(label, i, j, self))

    async def handle_move(self, interaction, row, col):
        global last_winner

        if self.board[row][col] != ' ':
            await interaction.followup.send("Invalid move! Spot already taken.", ephemeral=True)
            return

        self.board[row][col] = 'O'
        self.initialize_buttons()

        if self.check_winner('O'):
            await interaction.message.edit(content=f"{interaction.user.mention} wins! 🎉", view=None)
            update_score(interaction.user.id, 1, True)
            last_winner = 'player'
            return

        if self.is_board_full():
            await interaction.message.edit(content="It's a draw! 🤝", view=None)
            last_winner = 'bot' if self.bot_starts else 'player'
            return

        self.bot_move()
        self.initialize_buttons()

        if self.check_winner('X'):
            await interaction.message.edit(content="Bot wins! 🤖", view=None)
            update_score(interaction.user.id, 1, False)
            last_winner = 'bot'
            return

        if self.is_board_full():
            await interaction.message.edit(content="It's a draw! 🤝", view=None)
            last_winner = 'bot' if self.bot_starts else 'player'
            return

        await interaction.message.edit(content=self.format_board(), view=self)

    def bot_move(self):
        empty_cells = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ' ']
        if not empty_cells:
            return

        if self.difficulty == 'easy':
            row, col = random.choice(empty_cells)
        elif self.difficulty == 'medium':
            row, col = self.medium_move(empty_cells)
        elif self.difficulty == 'hard':
            row, col = self.hard_move(empty_cells)
        else:
            row, col = self.unbeatable_move()

        self.board[row][col] = 'X'

    def medium_move(self, empty_cells):
        return random.choice(empty_cells)

    def hard_move(self, empty_cells):
        return random.choice(empty_cells)

    def unbeatable_move(self):
        for r, c in [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ' ']:
            self.board[r][c] = 'X'
            if self.check_winner('X'):
                return r, c
            self.board[r][c] = ' '
        for r, c in [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ' ']:
            self.board[r][c] = 'O'
            if self.check_winner('O'):
                return r, c
            self.board[r][c] = ' '
        return random.choice([(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ' '])

    def check_winner(self, player):
        for row in self.board:
            if all(cell == player for cell in row):
                return True
        for col in range(3):
            if all(self.board[row][col] == player for row in range(3)):
                return True
        if all(self.board[i][i] == player for i in range(3)) or all(self.board[i][2 - i] == player for i in range(3)):
            return True
        return False

    def is_board_full(self):
        return all(cell != ' ' for row in self.board for cell in row)

    def format_board(self):
        board_display = "\n".join([" | ".join(row) for row in self.board])
        return f"```{board_display}```"

async def start_game(message, client, points=0):
    global last_winner

    for difficulty, (min_points, max_points) in difficulty_levels.items():
        if min_points <= points <= max_points:
            chosen_difficulty = difficulty
            break
    else:
        chosen_difficulty = 'easy'

    board = [[' ' for _ in range(3)] for _ in range(3)]
    bot_starts = (last_winner == 'player')
    last_winner = None

    view = TicTacToeView(message.author, board, client, chosen_difficulty, bot_starts)
    content = "Let's play Tic-Tac-Toe! 🎯\nYou are 'O', bot is 'X'."
    if bot_starts:
        content += "\nBot is starting first!"
    await message.channel.send(content + "\n" + view.format_board(), view=view)
