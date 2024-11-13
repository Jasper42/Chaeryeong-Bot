# gui.py
import json
import asyncio
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QWidget
from PyQt6.QtCore import QThread, pyqtSignal

class DiscordGUI(QMainWindow):
    """Main GUI window and logic for handling interactions."""
    status_updated = pyqtSignal(str)
    channel_name_updated = pyqtSignal(int, str)

    def __init__(self, bot, moderation_actions):
        super().__init__()
        self.bot = bot
        self.moderation_actions = moderation_actions
        self.current_channel = 0
        self.channel_entries = []  # Initialize the list for channel entries
        self.init_ui()
        self.load_channel_ids()

    def init_ui(self):
        self.setWindowTitle('Discord Bot GUI')
        main_widget = QWidget()
        layout = QVBoxLayout()

        # Create input fields for each channel slot
        for i in range(5):
            channel_layout = QHBoxLayout()
            channel_label = QLabel(f"Channel Slot {i + 1}:")
            channel_entry = QLineEdit()
            self.channel_entries.append(channel_entry)  # Add each entry to the list
            save_button = QPushButton("Save")
            save_button.clicked.connect(lambda _, slot=i: self.save_channel(slot))

            channel_layout.addWidget(channel_label)
            channel_layout.addWidget(channel_entry)
            channel_layout.addWidget(save_button)
            layout.addLayout(channel_layout)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def load_channel_ids(self):
        try:
            with open("config.json", "r") as file:
                config = json.load(file)
                self.bot.channel_ids[:] = config.get("channel_ids", [None] * 5)
                for i, channel_id in enumerate(self.bot.channel_ids):
                    if channel_id and i < len(self.channel_entries):  # Ensure index is within range
                        self.channel_entries[i].setText(channel_id)
        except FileNotFoundError:
            self.bot.channel_ids[:] = [None] * 5

    def save_channel(self, slot):
        new_channel_id = self.channel_entries[slot].text().strip()
        if new_channel_id.isdigit():
            self.bot.channel_ids[slot] = new_channel_id
            with open("config.json", "w") as file:
                json.dump({"channel_ids": self.bot.channel_ids}, file)
            self.status_updated.emit(f"Channel ID saved in slot {slot + 1}.")
            if self.bot.client:
                asyncio.run_coroutine_threadsafe(
                    self.bot.update_channel_names(),
                    self.bot.client.loop
                )
        else:
            self.status_updated.emit("Invalid channel ID entered.")

    def login(self):
        self.bot.client = self.bot.setup_client()
        self.discord_thread = QThread()
        self.discord_thread.run = lambda: self.bot.client.run(self.bot.token)
        self.discord_thread.start()
