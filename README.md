# Discord Bot

A simple Discord bot with utility and fun commands, including a Tic-Tac-Toe game.

## Features

- 🎲 **Fun Commands** — Play games and interact with the bot.
- 🔧 **Utility Commands** — Helpful commands for server management.
- 🕹️ **Tic-Tac-Toe Game** — Play against the bot with scaling difficulty.

## Setup

Follow these steps to set up the bot:

1. **Clone this repository:**
   ```bash
   git clone https://github.com/vali281/discord_bot.git
   ```
   
2.**Navigate to the project directory**
 ```bash
 cd discord_bot
```
 
3.**Create a Token.txt file:**
->In the root directory, create a file named Token.txt.
->Paste your bot’s token into this file (keep this token secret!).

4.**Install dependencies:**
->Ensure you have Python installed, then install any required packages:

```bash
pip install -r requirements.txt
```

5.**Run the bot:**
```bash
python bot.py
```
## Commands
->The bot responds to the following commands:
! is the prefix of the bot, you can change accordingly 

!hello — Replies with "Hello!"
!ping — Replies with "Pong!"
!start — Starts a game of Tic-Tac-Toe.
!say <message> — Repeats your message.
!leaderboard — Displays the top 10 users sorted by points.
!points — Shows your points, wins, and losses.
!repli <n>, <message> — Repeats your message n times.
!bonk <channel_id> <message> — Sends a message to the specified channel.
!help — Lists all available commands.
Use !help in Discord to see this list directly from the bot.

## File Structure
```discord_bot/
├── bot.py           # Main bot file
├── cmd.py           # Handles bot commands
├── game.py          # Game logic (Tic-Tac-Toe)
├── database.py      # Manages user scores and points
├── log.py           # Logging events
├── Token.txt        # Bot token (excluded from Git)
├── game_data.db     # SQLite database for storing user points
├── .gitignore       # Ignored files like Token.txt and __pycache__
└── README.md        # Project documentation
```

## Contributing
->Contributions are welcome! Here’s how you can help:

1.Fork the repository.
2.Create a new branch:
```bash
git checkout -b feature/YourFeature
```
3.Commit your changes:
```bash
git commit -m "Add your feature"
```
4.Push to the branch:
```bash
git push origin feature/YourFeature
```
5.Open a Pull Request on GitHub.

```License```
```This project is licensed under the MIT License — feel free to use and modify it.```

**Note: Keep your Token.txt private — never share it publicly!**



