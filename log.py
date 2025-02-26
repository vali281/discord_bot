from datetime import datetime

LOG_FILE = 'log.txt'

def log_command(user_id, username, channel_id, command):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] User: {username} (ID: {user_id}) | Channel: {channel_id} | Command: {command}\n"
    
    with open(LOG_FILE, 'a') as file:
        file.write(log_entry)

