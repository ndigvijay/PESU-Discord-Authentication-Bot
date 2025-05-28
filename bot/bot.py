import asyncio
import logging
import traceback
import os
import discord
import yaml
from discord import app_commands
from discord.app_commands import AppCommandError
from discord.ext import commands
from flask import Flask
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from cogs.db import DatabaseCog

# Create an absolute path for the log file
log_file_path = os.path.join(os.path.dirname(__file__), 'bot.log')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename=log_file_path,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(threadName)s:%(lineno)d - %(message)s",
    filemode="a",  # Append mode
)

# Load configuration
config = yaml.safe_load(open("bot/config.yml"))
bot_prefix = config["bot"].get("prefix", "pesauth.")
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = commands.Bot(command_prefix=bot_prefix, help_command=None, intents=intents)
client.config = config

# Add environment variables to config
client.config["bot"]["token"] = os.getenv("BOT_TOKEN")
client.config["db"] = os.getenv("MONGODB_URI")

async def setup():
    logging.info(f"Adding cogs to bot")
    database_cog = DatabaseCog(client)
    client.db = database_cog    
    await client.add_cog(database_cog)
    client.extns = ['cogs.auth', 'cogs.base', 'cogs.developer', 'cogs.moderator', 'cogs.misc']
    for extn in client.extns:
        await client.load_extension(extn)
    logging.info(f"Successfully added all cogs. Starting bot now")
    
    # Sync application commands with Discord
    try:
        logging.info("Syncing commands with Discord")
        await client.tree.sync()
        logging.info("Successfully synced commands with Discord")
    except Exception as e:
        logging.error(f"Failed to sync commands with Discord: {e}")
    
    await client.start(os.getenv("BOT_TOKEN"))

# Error handling
@client.tree.error
async def app_command_error(interaction: discord.Interaction, error: AppCommandError):
    if isinstance(error, app_commands.errors.CheckFailure):
        embed = discord.Embed(
            title="Error",
            description="You do not have the required permissions to run this command",
            color=discord.Color.red(),
        )
    else:
        logging.error(f"Slash command error: {error}\n{traceback.format_exc()}")
        embed = discord.Embed(
            title="Error",
            description=str(error),
            color=discord.Color.red(),
        )
    try:
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except discord.errors.InteractionResponded:
        await interaction.followup.send(embed=embed, ephemeral=True)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            title="Error",
            description="You do not have the required permissions to run this command",
            color=discord.Color.red(),
        )
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error",
            description="You do not have the required permissions to run this command",
            color=discord.Color.red(),
        )
        await ctx.reply(embed=embed)
    else:
        logging.error(f"Command error: {error}\n{traceback.format_exc()}")
        embed = discord.Embed(
            title="Error",
            description=str(error),
            color=discord.Color.red(),
        )
        await ctx.reply(embed=embed)

# New Snipe command
@client.tree.command(name="snipe", description="Attempt to recover a deleted message")
async def snipe(interaction: discord.Interaction):
    await interaction.response.send_message("Snipe has been removed due to privacy reasons")

# Create a Flask web server
app = Flask(__name__)

@app.route('/')
def home():
    return "Server is running"

# Start the Flask server in a background thread
def run_flask_server():
    logging.info("HTTP server started")
    port = int(os.getenv("PORT", 8084))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)

# Run the bot and the Flask server concurrently
async def main():
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, run_flask_server)  
    await setup()

# Start the asyncio event loop and run both the bot and Flask server
asyncio.run(main())
