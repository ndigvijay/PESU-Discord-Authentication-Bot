# import asyncio
# import logging
# import traceback
# import os
# import discord
# import yaml
# from discord import app_commands
# from discord.app_commands import AppCommandError
# from discord.ext import commands

# from cogs.db import DatabaseCog

# logging.basicConfig(
#     level=logging.INFO,
#     filename="bot.log",
#     format="%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(threadName)s:%(lineno)d - %(message)s",
#     filemode="w",
# )


# async def setup():
#     """
#     Adds all cogs to the bot and starts the bot
#     """
#     logging.info(f"Adding cogs to bot")
#     database_cog = DatabaseCog(client)
#     client.db = database_cog    
#     await client.add_cog(database_cog)
#     client.extns = ['cogs.auth', 'cogs.base', 'cogs.developer', 'cogs.moderator']
#     for extn in client.extns:
#         await client.load_extension(extn)
#     logging.info(f"Successfully added all cogs. Starting bot now")
#     await client.start(config["bot"]["token"])
#     # print(os.getenv("BOT_TOKEN"))
#     # await client.start(os.getenv("BOT_TOKEN"))


# config = yaml.safe_load(open("bot/config.yml"))
# bot_prefix = config["bot"].get("prefix", "pesauth.")
# intents = discord.Intents.default()
# intents.members = True
# intents.message_content = True

# client = commands.Bot(command_prefix=bot_prefix, help_command=None, intents=intents)
# client.config = config


# @client.tree.error
# async def app_command_error(interaction: discord.Interaction, error: AppCommandError):
#     """
#     Handles errors raised by app commands
#     """
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


# asyncio.run(setup())
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
import os

from cogs.db import DatabaseCog

logging.basicConfig(
    level=logging.INFO,
    filename="bot.log",
    format="%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(threadName)s:%(lineno)d - %(message)s",
    filemode="w",
)

async def setup():
    logging.info(f"Adding cogs to bot")
    database_cog = DatabaseCog(client)
    client.db = database_cog    
    await client.add_cog(database_cog)
    client.extns = ['cogs.auth', 'cogs.base', 'cogs.developer', 'cogs.moderator']
    for extn in client.extns:
        await client.load_extension(extn)
    logging.info(f"Successfully added all cogs. Starting bot now")
    await client.start(config["bot"]["token"])

# Load configuration
config = yaml.safe_load(open("bot/config.yml"))
bot_prefix = config["bot"].get("prefix", "pesauth.")
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = commands.Bot(command_prefix=bot_prefix, help_command=None, intents=intents)
client.config = config

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

# Create a Flask web server
app = Flask(__name__)

@app.route('/')
def home():
    return "Server is running"

# Start the Flask server in a background thread
def run_flask_server():
    logging.info("HTTP server started")
    port = int(os.getenv("PORT", 8000))
    app.run(port=port)

# Run the bot and the Flask server concurrently
async def main():
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, run_flask_server)  # Run Flask server in the background
    await setup()

# Start the asyncio event loop and run both the bot and Flask server
asyncio.run(main())
