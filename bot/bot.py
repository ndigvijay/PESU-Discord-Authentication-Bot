# import asyncio
# import logging
# import traceback
# import os
# import discord
# import yaml
# from discord import app_commands
# from discord.app_commands import AppCommandError
# from discord.ext import commands
# from flask import Flask

# from cogs.db import DatabaseCog

# # Create an absolute path for the log file
# log_file_path = os.path.join(os.path.dirname(__file__), 'bot.log')

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     filename=log_file_path,
#     format="%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(threadName)s:%(lineno)d - %(message)s",
#     filemode="a",  # Append mode
# )

# # Load configuration
# config = yaml.safe_load(open("bot/config.yml"))
# bot_prefix = config["bot"].get("prefix", "pesauth.")
# intents = discord.Intents.default()
# intents.members = True
# intents.message_content = True

# client = commands.Bot(command_prefix=bot_prefix, help_command=None, intents=intents)
# client.config = config

# async def setup():
#     logging.info(f"Adding cogs to bot")
#     database_cog = DatabaseCog(client)
#     client.db = database_cog    
#     await client.add_cog(database_cog)
#     client.extns = ['cogs.auth', 'cogs.base', 'cogs.developer', 'cogs.moderator', 'cogs.misc']
#     for extn in client.extns:
#         await client.load_extension(extn)
#     logging.info(f"Successfully added all cogs. Starting bot now")
#     await client.start(config["bot"]["token"])

# # Error handling
# @client.tree.error
# async def app_command_error(interaction: discord.Interaction, error: AppCommandError):
#     if isinstance(error, app_commands.errors.CheckFailure):
#         embed = discord.Embed(
#             title="Error",
#             description="You do not have the required permissions to run this command",
#             color=discord.Color.red(),
#         )
#     else:
#         logging.error(f"Slash command error: {error}\n{traceback.format_exc()}")
#         embed = discord.Embed(
#             title="Error",
#             description=str(error),
#             color=discord.Color.red(),
#         )
#     try:
#         await interaction.response.send_message(embed=embed, ephemeral=True)
#     except discord.errors.InteractionResponded:
#         await interaction.followup.send(embed=embed, ephemeral=True)

# @client.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.CommandNotFound):
#         return
#     elif isinstance(error, commands.CheckFailure):
#         embed = discord.Embed(
#             title="Error",
#             description="You do not have the required permissions to run this command",
#             color=discord.Color.red(),
#         )
#         await ctx.reply(embed=embed)
#     elif isinstance(error, commands.MissingPermissions):
#         embed = discord.Embed(
#             title="Error",
#             description="You do not have the required permissions to run this command",
#             color=discord.Color.red(),
#         )
#         await ctx.reply(embed=embed)
#     else:
#         logging.error(f"Command error: {error}\n{traceback.format_exc()}")
#         embed = discord.Embed(
#             title="Error",
#             description=str(error),
#             color=discord.Color.red(),
#         )
#         await ctx.reply(embed=embed)

# # Create a Flask web server
# app = Flask(__name__)

# @app.route('/')
# def home():
#     return "Server is running"

# # Start the Flask server in a background thread
# def run_flask_server():
#     logging.info("HTTP server started")
#     port = int(os.getenv("PORT", 8000))
#     app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# # Run the bot and the Flask server concurrently
# async def main():
#     loop = asyncio.get_event_loop()
#     loop.run_in_executor(None, run_flask_server)  # Run Flask server in the background
#     await setup()

# # Start the asyncio event loop and run both the bot and Flask server
# asyncio.run(main())


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

snipe_message = None

async def setup():
    logging.info(f"Adding cogs to bot")
    database_cog = DatabaseCog(client)
    client.db = database_cog    
    await client.add_cog(database_cog)
    client.extns = ['cogs.auth', 'cogs.base', 'cogs.developer', 'cogs.moderator', 'cogs.misc']
    for extn in client.extns:
        await client.load_extension(extn)
    logging.info(f"Successfully added all cogs. Starting bot now")
    await client.start(config["bot"]["token"])

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

# Snipe feature
@client.event
async def on_message_delete(message):
    global snipe_message
    if message.author.bot:
        return
    snipe_message = message

@client.command(name="snipe")
async def snipe(ctx):
    global snipe_message
    if snipe_message is None:
        await ctx.send("There's nothing to snipe!")
    else:
        embed = discord.Embed(
            title="Sniped Message",
            description=snipe_message.content,
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f"Sent by {snipe_message.author} in #{snipe_message.channel}")
        await ctx.send(embed=embed)
        snipe_message = None

# Create a Flask web server
app = Flask(__name__)

@app.route('/')
def home():
    return "Server is running"

# Start the Flask server in a background thread
def run_flask_server():
    logging.info("HTTP server started")
    port = int(os.getenv("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)

# Run the bot and the Flask server concurrently
async def main():
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, run_flask_server)  # Run Flask server in the background
    await setup()

# Start the asyncio event loop and run both the bot and Flask server
asyncio.run(main())
