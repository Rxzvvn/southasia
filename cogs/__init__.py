from utils.data_handler_warnings import load_warnings, save_warnings
from utils.data_handler_notes import load_notes, save_notes

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings_data = load_warnings()
        self.notes_data = load_notes()
