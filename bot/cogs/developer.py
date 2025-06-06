import logging
import subprocess
import sys
import yaml
from typing import Optional, Union

import discord
from discord import app_commands
from discord.ext import commands
import os


class DeveloperCog(commands.Cog):
    """
    This cog contains all commands and functionalities available to the bot developers
    """

    config = yaml.safe_load(open("bot/config.yml"))

    def __init__(self, client: commands.Bot):
        self.client = client
        self.developer_user_ids = client.config["bot"]["developer_user_ids"]
        self.developer_channel_ids = client.config["bot"]["developer_channel_ids"]
        self.developer_log_channels = []

    @commands.Cog.listener()
    async def on_ready(self):
        # Fetch the channels after the bot is fully ready
        if not self.developer_log_channels:  # Ensure we do not fetch channels multiple times
            try:
                self.developer_log_channels = [
                    await self.client.fetch_channel(channel_id)
                    for channel_id in self.developer_channel_ids
                ]
                logging.info("Developer channels successfully fetched.")
            except Exception as e:
                logging.error(f"Failed to fetch developer channels: {e}")

    # @staticmethod
    def check_developer_permissions(type: str = "app"):
        """
        Checks if the user is a developer
        """

        async def predicate(interaction: Union[commands.Context, discord.Interaction]):
            if isinstance(interaction, commands.Context):
                return interaction.author.id in interaction.bot.cogs["DeveloperCog"].developer_user_ids
            return interaction.user.id in interaction.client.cogs["DeveloperCog"].developer_user_ids

        if type == "app":
            return app_commands.check(predicate)
        return commands.check(predicate)
    
    dev_commands = app_commands.Group(name="dev", description="Developer commands", guild_ids=config["bot"]["developer_guild_ids"], guild_only=True)

    @dev_commands.command(name="gitpull", description="Pull the latest changes from GitHub")
    @check_developer_permissions()
    async def git_pull(self, interaction: discord.Interaction):
        """
        Pulls the latest changes from the git repository
        """
        await interaction.response.defer()
        logging.info(f"Pulling latest changes from git repository")
        sys.stdout.flush()

        embed = discord.Embed(
            title="Git pull",
            description="Pulling changes from GitHub...",
            color=discord.Color.blue(),
        )
        await interaction.followup.send(embed=embed)

        output = list()
        p = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
        for line in iter(p.stdout.readline, b""):
            if not line:
                break
            line = str(line.rstrip(), "utf-8", "ignore").strip()
            logging.info(line)
            output.append(line)

        output = '\n'.join(output)
        output = f"```bash\n{output}```"
        embed = discord.Embed(
            title="Git pull complete",
            description=output,
            color=discord.Color.green(),
        )
        await interaction.followup.send(embed=embed)
        sys.stdout.flush()

    @commands.command(name="sync", help="Sync commands with Discord")
    @check_developer_permissions("text")
    async def sync_command(self, ctx: commands.Context):
        """
        Syncs commands with Discord
        """
        logging.info(f"Synchronizing commands with Discord")
        await self.client.tree.sync()
        embed = discord.Embed(
            title="Commands synced with Discord",
            description="The bot has finished syncing commands with Discord",
            color=discord.Color.green(),
        )
        await ctx.reply(embed=embed)

    @commands.command(name="sync_guild", help="Sync commands with Discord for a specific guild")
    @check_developer_permissions("text")
    async def sync_guild_command(self, ctx: commands.Context, guild_id: int = None):
        """
        Syncs commands with Discord for a specific guild
        """
        if guild_id is None:
            guild = ctx.guild
        else:
            guild = await self.client.fetch_guild(guild_id)
        logging.info(f"Synchronizing commands with Discord for guild {guild.id}")
        await self.client.tree.sync(guild=guild)
        embed = discord.Embed(
            title="Commands synced with Discord",
            description=f"The bot has finished syncing commands with Discord for guild {guild.id}",
            color=discord.Color.green(),
        )
        await ctx.reply(embed=embed)

    @commands.command(name="reload", help="Reloads specified cog or all cogs")
    @check_developer_permissions("text")
    async def reload_cog(self, ctx: commands.Context, cog: str = None):
        """
        Reloads specified cog or all cogs
        """
        logging.info(f"Reloading cog {cog}")
        if cog is None:
            for extn in self.client.extns:
                await self.client.reload_extension(extn)
            logging.info(f"Reloaded all cogs")
        else:
            if not cog.startswith("cogs."):
                cog = f"cogs.{cog}"
            if cog in self.client.extns:
                await self.client.reload_extension(cog)
                logging.info(f"Reloaded cog {cog}")
            else:
                embed = discord.Embed(
                    title="Cog reload failed",
                    description=f"The cog `{cog}` does not exist",
                    color=discord.Color.red(),
                )
                await ctx.reply(embed=embed)
                return
        embed = discord.Embed(
            title="Cog reloaded",
            description=f"The cog `{cog}` has been reloaded" if cog else "All cogs have been reloaded",
            color=discord.Color.green(),
        )
        await ctx.reply(embed=embed)

    @dev_commands.command(name="log", description="Get the logs of the bot")
    @app_commands.describe(lines="The number of lines to fetch from EOF")
    @check_developer_permissions()
    async def logs(self, interaction: discord.Interaction, lines: Optional[int] = None):
        await interaction.response.defer(ephemeral=True)
        try:
            lines = int(lines)
        except (TypeError, ValueError):
            lines = None

        if lines is None:
            await interaction.followup.send(file=discord.File(open("bot.log", "rb")))
        else:
            logs = open("bot.log", "r").readlines()
            logs = logs[-lines:]
            logs = f"```log\n{''.join(logs)}```"
            await interaction.followup.send(logs)

    @dev_commands.command(name="shutdown", description="Shutdown the bot")
    @check_developer_permissions()
    async def shutdown(self, interaction: discord.Interaction):
        """
        Shuts down the bot
        """
        await interaction.response.defer()
        logging.info(f"Shutting down")
        embed = discord.Embed(
            title="Shutting down",
            description="The bot has been shut down",
            color=discord.Color.red(),
        )
        await interaction.followup.send(embed=embed)
        await self.client.close()

    @dev_commands.command(name="restart", description="Restart the bot")
    @check_developer_permissions()
    async def restart(self, interaction: discord.Interaction):
        """
        Restarts the bot
        """
        await interaction.response.defer()
        logging.info(f"Restarting")
        embed = discord.Embed(
            title="Restarting",
            description="The bot has been restarted",
            color=discord.Color.red(),
        )
        await interaction.followup.send(embed=embed)
        subprocess.Popen(["python", "bot/bot.py"])
        await self.client.close()


async def setup(client: commands.Bot):
    """
    Adds the cog to the bot
    """
    await client.add_cog(DeveloperCog(client))
