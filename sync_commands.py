#!/usr/bin/env python
import asyncio
import os
import yaml
import argparse
import discord
from discord.ext import commands
from discord import app_commands

# Parse command line arguments
parser = argparse.ArgumentParser(description='Sync Discord commands for the bot')
parser.add_argument('--guild', type=int, help='Specific guild ID to sync commands for')
parser.add_argument('--global', action='store_true', dest='global_sync', help='Sync commands globally')
args = parser.parse_args()

# Load configuration
try:
    config = yaml.safe_load(open("bot/config.yml"))
    TOKEN = config["bot"]["token"]
except Exception as e:
    print(f"Error loading config: {e}")
    exit(1)

# Setup intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize the bot
bot = commands.Bot(command_prefix='!', intents=intents)

async def sync_commands():
    await bot.wait_until_ready()
    print(f"Bot is ready as {bot.user}")
    
    try:
        if args.guild:
            # Sync to a specific guild
            guild = bot.get_guild(args.guild)
            if not guild:
                print(f"Guild with ID {args.guild} not found. Make sure the bot is in this guild.")
                return
            
            await bot.tree.sync(guild=guild)
            print(f"Successfully synced commands to guild: {guild.name} (ID: {guild.id})")
            
        elif args.global_sync:
            # Sync globally
            await bot.tree.sync()
            print("Successfully synced commands globally")
            
        else:
            # Sync to all guilds in the developer_guild_ids list
            for guild_id in config["bot"]["developer_guild_ids"]:
                guild = bot.get_guild(guild_id)
                if guild:
                    await bot.tree.sync(guild=guild)
                    print(f"Successfully synced commands to guild: {guild.name} (ID: {guild.id})")
                else:
                    print(f"Guild with ID {guild_id} not found. Make sure the bot is in this guild.")
            
            # Also sync globally
            await bot.tree.sync()
            print("Successfully synced commands globally")
        
    except Exception as e:
        print(f"Error syncing commands: {e}")
    finally:
        # Stop the bot
        await bot.close()

# Setup the bot
@bot.event
async def on_ready():
    # This is necessary to have a clean event loop
    bot.loop.create_task(sync_commands())

# Run the bot
if __name__ == "__main__":
    print("Starting command sync process...")
    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        print("Error: Invalid token provided. Please check your bot token.")
    except Exception as e:
        print(f"Error: {e}")
    print("Command sync process completed.") 
    
    
    
    
#command to remove the bot from a guild
"""
curl -X DELETE "https://discord.com/api/v10/users/@me/guilds/1340719908383752255" -H "Authorization: Bot MTI5NzU3NTYzNzU3MzE3MzMwMA.GV0f4Z.5RkStRnKZPcmxZ8N4OIOBbgugoqtBurhjX5bys"
"""