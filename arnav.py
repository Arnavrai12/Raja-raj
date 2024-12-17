import telebot
import subprocess
import datetime
import os
import random
import string
import json

# Insert your Telegram bot token here
bot = telebot.TeleBot('YOUR_BOT_TOKEN')
# Admin user IDs
admin_id = {'6329099426'}

# Files for data storage
USER_FILE = "users.json"
LOG_FILE = "log.txt"
KEY_FILE = "keys.json"

# Cooldown settings
COOLDOWN_TIME = 0  # in seconds
CONSECUTIVE_ATTACKS_LIMIT = 20
CONSECUTIVE_ATTACKS_COOLDOWN = 5  # in seconds

# In-memory storage
users = {}
keys = {}
bgmi_cooldown = {}
consecutive_attacks = {}

# Read users and keys from files initially
def load_data():
    global users, keys
    users = read_users()
    keys = read_keys()

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users():
    with open(USER_FILE, "w") as file:
        json.dump(users, file)

def read_keys():
    try:
        with open(KEY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_keys():
    with open(KEY_FILE, "w") as file:
        json.dump(keys, file, indent=4)

def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else f"UserID: {user_id}"

    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

def generate_key(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def add_time_to_current_date(hours=0, days=0):
    return (datetime.datetime.now() + datetime.timedelta(hours=hours, days=days)).strftime('%Y-%m-%d %H:%M:%S')

@bot.message_handler(commands=['genkey'])
def generate_key_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 3:
            try:
                time_amount = int(command[1])
                time_unit = command[2].lower()
                if time_unit == 'hours':
                    expiration_date = add_time_to_current_date(hours=time_amount)
                elif time_unit == 'days':
                    expiration_date = add_time_to_current_date(days=time_amount)
                else:
                    raise ValueError("Invalid time unit")
                key = generate_key()
                keys[key] = {"expires_on": expiration_date}
                save_keys()
                response = f"𝐊𝐞𝐲 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐢𝐨𝐧: {key}\n𝐄𝐱𝐩𝐢𝐫𝐞𝐬 𝐎𝐧: {expiration_date}"
            except ValueError:
                response = "𝐏𝐥𝐞𝐚𝐬𝐞 𝐒𝐩𝐞𝐜𝐢𝐟𝐲 𝐀 𝐕𝐚𝐥𝐢𝐝 𝐍𝐮𝐦𝐛𝐞𝐫 𝐚𝐧𝐝 𝐔𝐧𝐢𝐭 𝐨𝐟 𝐓𝐢𝐦𝐞 (hours/days)."
        else:
            response = "𝐔𝐬𝐚𝐠𝐞: /genkey <amount> <hours/days>"
    else:
        response = "𝐎𝐧𝐥𝐲 𝐚𝐝𝐦𝐢𝐧𝐬 𝐜𝐚𝐧 𝐠𝐞𝐧𝐞𝐫𝐚𝐭𝐞 𝐤𝐞𝐲𝐬."

    bot.reply_to(message, response)

@bot.message_handler(commands=['customkey'])
def custom_key_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 3:
            try:
                custom_value = command[1]
                expiration_days = int(command[2])
                expiration_date = add_time_to_current_date(days=expiration_days)
                custom_key = generate_key()
                keys[custom_key] = {"custom_value": custom_value, "expires_on": expiration_date}
                save_keys()
                response = f"𝐂𝐮𝐬𝐭𝐨𝐦 𝐊𝐞𝐲 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝: {custom_key}\n𝐂𝐮𝐬𝐭𝐨𝐦 𝐕𝐚𝐥𝐮𝐞: {custom_value}\n𝐄𝐱𝐩𝐢𝐫𝐞𝐬 𝐎𝐧: {expiration_date}"
            except ValueError:
                response = "𝐄𝐫𝐫𝐨𝐫: 𝐄𝐧𝐬𝐮𝐫𝐞 𝐲𝐨𝐮 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐜𝐮𝐬𝐭𝐨𝐦 𝐯𝐚𝐥𝐮𝐞 𝐚𝐧𝐝 𝐞𝐱𝐩𝐢𝐫𝐚𝐭𝐢𝐨𝐧 𝐝𝐚𝐲𝐬."
        else:
            response = "𝐔𝐬𝐚𝐠𝐞: /customkey <custom_value> <expiration_days>"
    else:
        response = "𝐎𝐧𝐥𝐲 𝐚𝐝𝐦𝐢𝐧𝐬 𝐜𝐚𝐧 𝐠𝐞𝐧𝐞𝐫𝐚𝐭𝐞 𝐜𝐮𝐬𝐭𝐨𝐦 𝐤𝐞𝐲𝐬."

    bot.reply_to(message, response)

@bot.message_handler(commands=['redeem'])
def redeem_key_command(message):
    user_id = str(message.chat.id)
    command = message.text.split()
    if len(command) == 2:
        key = command[1]
        if key in keys:
            key_data = keys[key]
            expiration_date = key_data.get("expires_on")
            custom_value = key_data.get("custom_value", "None")
            if user_id in users:
                user_expiration = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
                new_expiration_date = max(user_expiration, datetime.datetime.now()) + datetime.timedelta(days=1)
                users[user_id] = new_expiration_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                users[user_id] = expiration_date
            save_users()
            del keys[key]
            save_keys()
            response = f"✅ 𝐊𝐞𝐲 𝐫𝐞𝐝𝐞𝐞𝐦𝐞𝐝 𝐬𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲! 𝐀𝐜𝐜𝐞𝐬𝐬 𝐮𝐧𝐭𝐢𝐥: {users[user_id]}\n𝐂𝐮𝐬𝐭𝐨𝐦 𝐕𝐚𝐥𝐮𝐞: {custom_value}"
        else:
            response = "❌ 𝐊𝐞𝐲 𝐧𝐨𝐭 𝐯𝐚𝐥𝐢𝐝 𝐨𝐫 𝐞𝐱𝐩𝐢𝐫𝐞𝐝."
    else:
        response = "𝐔𝐬𝐚𝐠𝐞: /redeem <key>"
    
    bot.reply_to(message, response)

if __name__ == "__main__":
    load_data()
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
