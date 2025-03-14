import json

FORWARD_FILE = 'forward.txt'

# Load forward data from the file
def load_forward_data():
    try:
        with open(FORWARD_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save forward data to the file
def save_forward_data(data):
    with open(FORWARD_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Set the forward channel for a specific server (by guild ID)
def set_forward_channel(guild_id, channel_id):
    data = load_forward_data()
    data[str(guild_id)] = str(channel_id)
    save_forward_data(data)

# Get the forward channel for a specific server (by guild ID)
def get_forward_channel(guild_id):
    data = load_forward_data()
    return data.get(str(guild_id))
