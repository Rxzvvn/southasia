import discord
import os

# ✅ Command Prefix
PREFIX = ","

# ✅ Discord Bot Token (use Railway Secret environment)
TOKEN = os.getenv("TOKEN")  # Set this in Railway under Project > Variables

# ✅ Logging Channel (logs every command here)
LOG_CHANNEL_ID = 1400809302423375942

# ✅ Role IDs
STAFF_ROLE_ID = 1400967381869658182
PIC_PERM_ROLE_ID = 1401141194397974582
LINK_PERM_ROLE_ID = 1401141250450657340

# ✅ Discord Intents (all enabled)
INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.members = True
INTENTS.guilds = True
INTENTS.messages = True
INTENTS.reactions = True
INTENTS.presences = True

# ✅ List of Cogs to Load
COGS = [
    "moderation",   # warn, mute, ban, kick, jail etc.
    "general",      # ping, help, info etc.
    "fun"           # optional funny/random commands
]
