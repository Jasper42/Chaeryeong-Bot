import sys
import json
import discord
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLineEdit, QLabel)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from threading import Thread
import asyncio
import datetime

with open('token.txt', 'r') as f:
    TOKEN = f.read().strip()
client = None
channel_ids = [None] * 5
channel_names = ["Unknown"] * 5

class DiscordThread(QThread):
    status_updated = pyqtSignal(str)
    channel_name_updated = pyqtSignal(int, str)

    def __init__(self, gui):
        super().__init__()
        self.gui = gui

    def run(self):
        global client
        intents = discord.Intents.default()
        intents.members = True
        intents.moderation = True
        intents.message_content = True
        client = discord.Client(intents=intents)
        
        @client.event
        async def on_ready():
            self.status_updated.emit(f"Logged in as {client.user}")
            for i, channel_id in enumerate(channel_ids):
                if channel_id:
                    try:
                        channel = await client.fetch_channel(int(channel_id))
                        channel_names[i] = channel.name
                        self.channel_name_updated.emit(i, channel.name)
                    except:
                        pass

        client.run(TOKEN)

class DiscordBotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_channel = 0
        self.init_ui()
        self.load_channel_ids()

    def init_ui(self):
        self.setWindowTitle('Discord Bot GUI')
        self.setStyleSheet("""
            QMainWindow { background-color: #7289DA; }
            QPushButton { 
                background-color: #5B6EAE; 
                color: white; 
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:pressed { 
                background-color: #4E5D94;
                padding: 7px 5px 3px 5px;
            }
            QLineEdit { 
                background-color: #4E5D94; 
                color: white;
                padding: 5px;
            }
            QLabel { color: white; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Login button
        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        # Message input
        self.message_entry = QLineEdit()
        self.message_entry.setPlaceholderText("Enter your message...")
        self.message_entry.returnPressed.connect(self.send_message)
        layout.addWidget(self.message_entry)

        # Send button
        send_button = QPushButton('Send')
        send_button.clicked.connect(self.send_message)
        layout.addWidget(send_button)

        # Channel inputs
        self.channel_entries = []
        self.go_to_buttons = []
        
        mod_frame = QWidget()
        mod_layout = QHBoxLayout(mod_frame)

        user_id_frame = QWidget()
        user_id_layout = QHBoxLayout(user_id_frame)

        user_id_label = QLabel("User ID:")
        user_id_layout.addWidget(user_id_label)

        self.user_id_entry = QLineEdit()
        self.user_id_entry.setPlaceholderText("Enter user ID for moderation...")
        user_id_layout.addWidget(self.user_id_entry)

        layout.addWidget(user_id_frame)
        kick_button = QPushButton('Kick User')
        kick_button.clicked.connect(self.kick_user)
        mod_layout.addWidget(kick_button)

        ban_button = QPushButton('Ban User')
        ban_button.clicked.connect(self.ban_user)
        mod_layout.addWidget(ban_button)

        timeout_button = QPushButton('Timeout User')
        timeout_button.clicked.connect(self.timeout_user)
        mod_layout.addWidget(timeout_button)

        layout.addWidget(mod_frame)

        for i in range(5):
            channel_frame = QWidget()
            channel_layout = QHBoxLayout(channel_frame)
            
            channel_label = QLabel(f"Channel {i + 1}:")
            channel_layout.addWidget(channel_label)
            
            entry = QLineEdit()
            self.channel_entries.append(entry)
            channel_layout.addWidget(entry)
            
            save_button = QPushButton('Save')
            save_button.clicked.connect(lambda checked, idx=i: self.save_channel(idx))
            channel_layout.addWidget(save_button)
            
            go_to_button = QPushButton(f'Go to {channel_names[i]}')
            go_to_button.clicked.connect(lambda checked, idx=i: self.go_to_channel(idx))
            self.go_to_buttons.append(go_to_button)
            channel_layout.addWidget(go_to_button)
            
            layout.addWidget(channel_frame)

        # Status label
        self.status_label = QLabel('Bot not connected.')
        self.status_label.setStyleSheet("background-color: #4E5D94; padding: 5px;")
        layout.addWidget(self.status_label)

    def login(self):
        self.discord_thread = DiscordThread(self)
        self.discord_thread.status_updated.connect(self.update_status)
        self.discord_thread.channel_name_updated.connect(self.update_channel_name)
        self.login_button.setStyleSheet("background-color: #43B581;")  # Discord's green color
        self.login_button.setEnabled(False)  # Optional: disable button after logging in
        self.discord_thread.start()

    def update_status(self, message):
        self.status_label.setText(message)

    def update_channel_name(self, slot, name):
        self.go_to_buttons[slot].setText(f"Go to {name}")

    def send_message(self):
        message = self.message_entry.text().strip()
        if message and client and channel_ids[self.current_channel]:
            asyncio.run_coroutine_threadsafe(
                self.send_message_async(message, channel_ids[self.current_channel]),
                client.loop
            )
            self.message_entry.clear()
        else:
            self.status_label.setText("No message entered or bot not connected.")

    async def send_message_async(self, message, channel_id):
        channel = client.get_channel(int(channel_id))
        if channel:
            await channel.send(message)
            self.status_label.setText("Message sent!")
        else:
            self.status_label.setText(f"Channel with ID {channel_id} not found.")

    def save_channel(self, slot):
        new_channel_id = self.channel_entries[slot].text().strip()
        if new_channel_id.isdigit():
            channel_ids[slot] = new_channel_id
            with open("config.json", "w") as file:
                json.dump({"channel_ids": channel_ids}, file)
            self.status_label.setText(f"Channel ID saved in slot {slot + 1}.")
            if client:
                asyncio.run_coroutine_threadsafe(
                    self.fetch_channel_name(slot, new_channel_id),
                    client.loop
                )
        else:
            self.status_label.setText("Invalid channel ID entered.")

    async def fetch_channel_name(self, slot, channel_id):
        try:
            channel = await client.fetch_channel(int(channel_id))
            channel_names[slot] = channel.name
            self.go_to_buttons[slot].setText(f"Go to {channel.name}")
        except:
            self.go_to_buttons[slot].setText("Channel not found")

    def go_to_channel(self, slot):
        if channel_ids[slot]:
            self.current_channel = slot
            self.status_label.setText(f"Switched to channel ID in slot {slot + 1}.")
        else:
            self.status_label.setText(f"No channel ID saved in slot {slot + 1}.")

    def load_channel_ids(self):
        try:
            with open("config.json", "r") as file:
                config = json.load(file)
                channel_ids[:] = config.get("channel_ids", [None] * 5)
                for i, channel_id in enumerate(channel_ids):
                    if channel_id:  # Fixed the truncated line
                        self.channel_entries[i].setText(channel_id)
        except FileNotFoundError:
            channel_ids[:] = [None] * 5

    def kick_user(self):
        user_id = self.user_id_entry.text().strip()
        if user_id.isdigit() and client:
            asyncio.run_coroutine_threadsafe(
                self.kick_user_async(user_id),
                client.loop
            )

    async def kick_user_async(self, user_id):
        try:
            channel = client.get_channel(int(channel_ids[self.current_channel]))
            guild = channel.guild
            member = await guild.fetch_member(int(user_id))
            await member.kick()
            self.status_label.setText(f"User {user_id} kicked successfully")
        except:
            self.status_label.setText("Failed to kick user")

    def ban_user(self):
        user_id = self.user_id_entry.text().strip()
        if user_id.isdigit() and client:
            asyncio.run_coroutine_threadsafe(
                self.ban_user_async(user_id),
                client.loop
            )

    async def ban_user_async(self, user_id):
        try:
            channel = client.get_channel(int(channel_ids[self.current_channel]))
            guild = channel.guild
            member = await guild.fetch_member(int(user_id))
            await member.ban()
            self.status_label.setText(f"User {user_id} banned successfully")
        except:
            self.status_label.setText("Failed to ban user")

    def timeout_user(self):
        user_id = self.user_id_entry.text().strip()
        if user_id.isdigit() and client:
            asyncio.run_coroutine_threadsafe(
                self.timeout_user_async(user_id),
                client.loop
            )

    async def timeout_user_async(self, user_id):
        try:
            channel = client.get_channel(int(channel_ids[self.current_channel]))
            guild = channel.guild
            member = await guild.fetch_member(int(user_id))
            # 5 minute timeout by default
            await member.timeout(datetime.timedelta(minutes=5))
            self.status_label.setText(f"User {user_id} timed out successfully")
        except:
            self.status_label.setText("Failed to timeout user")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DiscordBotGUI()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())
