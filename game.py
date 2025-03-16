import discord
import random
from discord.ui import View, Button
from database import update_score, get_user_data

last_winner = None

# Enhanced difficulty parameters
difficulty_levels = {
    'easy': (0, 3),
    'medium': (4, 5),
    'hard': (6, 8),
    'unbeatable': (9, float('inf'))
}

class TicTacToeButton(Button):
    def __init__(self, label, row, col, parent_view):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, row=row)
        self.parent_view = parent_view
        self.row = row
        self.col = col

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.parent_view.handle_move(interaction, self.row, self.col)

class TicTacToeView(View):
    def __init__(self, player, board, client, difficulty='easy', bot_starts=False):
        super().__init__(timeout=60)
        self.player = player
        self.board = board
        self.client = client
        self.difficulty = difficulty
        self.bot_starts = bot_starts
        self.initialize_board()

        if self.bot_starts:
            self.bot_move()
            self.initialize_board()

    def initialize_board(self):
        self.clear_items()
        for i in range(3):
            for j in range(3):
                label = str(i*3 + j + 1) if self.board[i][j] == ' ' else self.board[i][j]
                btn_style = discord.ButtonStyle.red if self.board[i][j] == 'X' else discord.ButtonStyle.green
                self.add_item(TicTacToeButton(label, i, j, self))

    async def handle_move(self, interaction, row, col):
        global last_winner

        if interaction.user != self.player:
            await interaction.followup.send("This isn't your game!", ephemeral=True)
            return

        if self.board[row][col] != ' ':
            return

        self.board[row][col] = 'O'
        self.initialize_board()

        if self.check_winner('O'):
            await self.end_game(interaction, "player")
            return

        if self.is_board_full():
            await self.end_game(interaction, "draw")
            return

        self.bot_move()
        self.initialize_board()

        if self.check_winner('X'):
            await self.end_game(interaction, "bot")
            return

        if self.is_board_full():
            await self.end_game(interaction, "draw")
            return

        await interaction.message.edit(content=self.game_status(), view=self)

    def bot_move(self):
        if self.difficulty == 'unbeatable':
            row, col = self.minimax_move()
        else:
            row, col = self.smart_move()
        self.board[row][col] = 'X'

    def smart_move(self):
        # Prioritize: 1) Win 2) Block 3) Center 4) Corners
        for player in ['X', 'O']:
            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == ' ':
                        self.board[i][j] = player
                        if self.check_winner(player):
                            self.board[i][j] = ' '
                            return (i, j)
                        self.board[i][j] = ' '

        if self.board[1][1] == ' ':
            return (1, 1)

        corners = [(0,0), (0,2), (2,0), (2,2)]
        empty_corners = [c for c in corners if self.board[c[0]][c[1]] == ' ']
        if empty_corners:
            return random.choice(empty_corners)

        return random.choice([(i,j) for i in range(3) for j in range(3) if self.board[i][j] == ' '])

    def minimax_move(self):
        best_score = -float('inf')
        best_move = None
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == ' ':
                    self.board[i][j] = 'X'
                    score = self.minimax(False)
                    self.board[i][j] = ' '
                    if score > best_score:
                        best_score = score
                        best_move = (i, j)
        return best_move

    def minimax(self, is_maximizing):
        if self.check_winner('X'):
            return 1
        if self.check_winner('O'):
            return -1
        if self.is_board_full():
            return 0

        if is_maximizing:
            best_score = -float('inf')
            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == ' ':
                        self.board[i][j] = 'X'
                        score = self.minimax(False)
                        self.board[i][j] = ' '
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == ' ':
                        self.board[i][j] = 'O'
                        score = self.minimax(True)
                        self.board[i][j] = ' '
                        best_score = min(score, best_score)
            return best_score

    async def end_game(self, interaction, result):
        global last_winner
        content = interaction.message.content
        
        if result == "player":
            content += f"\n🎉 {self.player.mention} wins!"
            update_score(self.player.id, 3, True)
            last_winner = 'bot'  # Winner starts next
        elif result == "bot":
            content += "\n🤖 Bot wins!"
            update_score(self.player.id, 1, False)
            last_winner = 'player'  # Loser starts next
        else:
            content += "\n🤝 It's a draw!"
            last_winner = 'player' if self.bot_starts else 'bot'
        
        await interaction.message.edit(content=content, view=None)
        self.stop()

    def check_winner(self, player):
        # Check rows, columns, and diagonals
        for i in range(3):
            if all(self.board[i][j] == player for j in range(3)) or \
               all(self.board[j][i] == player for j in range(3)):
                return True
        return all(self.board[i][i] == player for i in range(3)) or \
               all(self.board[i][2-i] == player for i in range(3))

    def is_board_full(self):
        return all(cell != ' ' for row in self.board for cell in row)

    def game_status(self):
        return f"Current Board:\n{self.format_board()}\nDifficulty: {self.difficulty.capitalize()}"

    def format_board(self):
        return "```" + "\n".join([" | ".join(row) for row in self.board]) + "```"

async def start_game(message, client):
    user_data = get_user_data(message.author.id)
    points = user_data[0] if user_data else 0
    
    for diff, (min_p, max_p) in difficulty_levels.items():
        if min_p <= points <= max_p:
            difficulty = diff
            break
    
    board = [[' ' for _ in range(3)] for _ in range(3)]
    bot_starts = (last_winner == 'player') if last_winner else False
    
    view = TicTacToeView(message.author, board, client, difficulty, bot_starts)
    content = f"🔴 {message.author.mention} vs 🤖 Bot | Difficulty: {difficulty.capitalize()}"
    if bot_starts:
        content += "\n🤖 Bot starts first!"
    await message.channel.send(content + view.format_board(), view=view)