# main.py
import sys
from PyQt6.QtWidgets import QApplication
from bot import DiscordBot
from moderation import ModerationActions
from gui import DiscordGUI

if __name__ == '__main__':
    with open('token.txt', 'r') as f:
        TOKEN = f.read().strip()

    app = QApplication(sys.argv)

    # Initialize bot, moderation actions, and GUI
    bot = DiscordBot(token=TOKEN, gui=None)  # GUI will be linked later
    moderation_actions = ModerationActions(bot=bot)
    gui = DiscordGUI(bot=bot, moderation_actions=moderation_actions)
    bot.gui = gui  # Link GUI back to bot for signal communication

    # Show GUI
    gui.resize(600, 400)
    gui.show()

    # Start the application
    sys.exit(app.exec())