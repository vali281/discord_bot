import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('game_data.db')
cursor = conn.cursor()

# Create a users table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    points INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0
)
''')
conn.commit()

# Add a new user to the database if its new
def add_user(user_id, username):
    cursor.execute('''
    INSERT INTO users (user_id, username) 
    VALUES (?, ?)
    ON CONFLICT(user_id) DO NOTHING
    ''', (user_id, username))
    conn.commit()

# Get the user's points, wins, and losses
def get_user_data(user_id):
    cursor.execute('SELECT points, wins, losses FROM users WHERE user_id = ?', (user_id,))
    return cursor.fetchone()

# Update the user's points, wins, and losses
def update_score(user_id, points, won):
    if won:
        cursor.execute('''
        UPDATE users SET points = points + ?, wins = wins + 1 WHERE user_id = ?
        ''', (points, user_id))
    else:
        cursor.execute('''
        UPDATE users SET points = points - ?, losses = losses + 1 WHERE user_id = ?
        ''', (points, user_id))
    conn.commit()

# Get the top 10 users sorted by points
def get_leaderboard():
    cursor.execute('SELECT username, points, wins, losses FROM users ORDER BY points DESC LIMIT 10')
    return cursor.fetchall()
