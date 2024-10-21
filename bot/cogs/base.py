import logging
import traceback
from itertools import cycle

import discord
from discord.ext import commands, tasks

from .db import DatabaseCog


class BaseCog(commands.Cog):
    """
    This cog contains all base functions
    """

    def __init__(self, client: commands.Bot, db: DatabaseCog):
        self.client = client
        self.db = db
        self.statuses = cycle([
            "with the PRIDE of PESU",
            "with lives",
            "with your future",
            "with PESsants",
            "with PESts"
        ])

        self.change_status_loop.start()

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Called when the bot is ready
        """
        logging.info(f"Logged in as {self.client.user.name}#{self.client.user.discriminator}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """
        Called when the bot joins a new server
        """
        logging.info(f"Joined server {guild.name}")
        self.db.add_server(guild.id)
        embed = discord.Embed(
            title="PESU Auth Bot - Hello!",
            description="I am the PESU Auth Bot. I am here to help you with your server's authentication. "
                        "To get started, please use the `/setup` command to add an existing role as the "
                        "verification role. Once you have done that, members can use the `/auth` command to "
                        "authenticate and assign the verification role to themselves.",
            color=discord.Color.green(),
        )
        for member in guild.members:
            if member.guild_permissions.administrator:
                await member.send(embed=embed)

        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(embed=embed)
                break

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """
        Called when the bot leaves a server
        """
        logging.info(f"Left server {guild.name}")
        self.db.remove_server(guild.id)

    @tasks.loop(hours=5)
    async def change_status_loop(self):
        """
        Changes the bot status every 5 hours
        """
        await self.client.wait_until_ready()
        logging.info("Changing bot status")
        await self.client.change_presence(activity=discord.Game(next(self.statuses)))


async def setup(client: commands.Bot):
    """
    Adds the cog to the bot
    """
    await client.add_cog(BaseCog(client, client.db))