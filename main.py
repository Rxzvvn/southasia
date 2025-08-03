import discord
from discord.ext import commands
import os
import asyncio
import traceback
import logging

from config import TOKEN, PREFIX, INTENTS, COGS
from utils.logger import log_command
from utils.error_handler import handle_command_error

# Setup logger
logging.basicConfig(level=logging.INFO)

class BleedBot(commands.Bot):
    async def setup_hook(self):
        for cog in COGS:
            try:
                await self.load_extension(f"cogs.{cog}")
                logging.info(f"✅ Loaded cog: {cog}")
            except Exception as e:
                logging.error(f"❌ Failed to load cog {cog}\n{traceback.format_exc()}")

        try:
            synced = await self.tree.sync()
            logging.info(f"🔁 Synced {len(synced)} slash commands.")
        except Exception as e:
            logging.error(f"❌ Slash command sync failed:\n{traceback.format_exc()}")

bot = BleedBot(command_prefix=PREFIX, intents=INTENTS, help_command=None)

@bot.event
async def on_ready():
    logging.info(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    logging.info("✅ Bot is ready and running.")

@bot.event
async def on_command(ctx):
    await log_command(ctx)

@bot.event
async def on_command_error(ctx, error):
    await handle_command_error(ctx, error)

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        logging.critical(f"🔥 Bot crashed unexpectedly:\n{e}")
