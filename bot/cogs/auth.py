import logging
from typing import Optional
import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime
from .db import DatabaseCog
import requests

class AuthenticationCog(commands.Cog):
    """
    This cog contains all commands and functionalities to authenticate users and manage confessions
    """

    def __init__(self, client: commands.Bot, db: DatabaseCog):
        self.client = client
        self.db = db
        self.confessions = {}
        
        
    def check_valid_prn(prn: str) -> bool:
        """
        Checks if the given PRN is valid
        """
        # after PES we need to have '1' or '2' for campus , then the year of student then the roll number
        if prn[:3] != 'PES':
            return False
        if prn[3] not in ['1', '2']:
            return False
        year = prn[4:6]
        try:
            int(year)  
            if(int(year) < 18):
                return False
        except ValueError:
            return False
        return True
        

    @staticmethod
    def check_pesu_academy_credentials(username: str, password: str) -> Optional[dict]:
        """
        Checks if the given credentials are valid via the pesu-auth API
        """
        data = {
            'username': username,
            'password': password,
            'profile': True
        }
        response = requests.post("https://pesu-auth.onrender.com/authenticate", json=data)
        if response.status_code == 200:
            return response.json()

    @app_commands.command(name="auth", description="Verify your discord account with your PESU Academy credentials")
    async def authenticate(self, interaction: discord.Interaction, username: str, password: str):
        # use only PRN as username , if email return error
        if '@' in username:
            embed = discord.Embed(
                title="Verification Failed",
                description="Please use your PRN as username",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)
            return        
        if not self.check_valid_prn(username):
            embed = discord.Embed(
                title="Verification Failed",
                description="Please use a valid PRN",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)
            return
        logging.info(f"Authenticating {interaction.user}")
        await interaction.response.defer(ephemeral=True)
        verification_role_id = 1373648829051568259  # Replace with dynamic retrieval if needed
        old_role_id = 1373650258013454376
        guild_id = 1340719908383752255  # The guild ID where verification is happening

        # Get the guild object directly using the guild ID
        guild = self.client.get_guild(guild_id)
        if not guild:
            embed = discord.Embed(
                title="Verification Failed",
                description="Could not find the server. Please try again later or contact an admin.",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)
            return

        if verification_role_id:
            verification_role = guild.get_role(verification_role_id)
            if not verification_role:
                embed = discord.Embed(
                    title="Verification Failed",
                    description=f"Could not find the verification role (ID: {verification_role_id}). Please contact an admin.",
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed)
                return
                
            member = guild.get_member(interaction.user.id)
            if not member:
                embed = discord.Embed(
                    title="Verification Failed",
                    description="Could not find your user in the server. Please make sure you're in the server and try again.",
                    color=discord.Color.red(),
                )
                await interaction.followup.send(embed=embed)
                return
                
            if verification_role in member.roles:
                embed = discord.Embed(
                    title="Verification Failed",
                    description="You are already verified on this server",
                    color=discord.Color.orange(),
                )
                await interaction.followup.send(embed=embed)
            else:
                authentication_result = self.check_pesu_academy_credentials(username=username, password=password)
                if authentication_result and authentication_result["status"] and authentication_result["profile"] and authentication_result["profile"]["prn"] and authentication_result["profile"]["program"]:
                    try:
                        old_role = guild.get_role(old_role_id)
                        if old_role:
                            await member.remove_roles(old_role)
                        await member.add_roles(verification_role)
                    except discord.Forbidden:
                        embed = discord.Embed(
                            title="Verification Failed",
                            description=f"{self.client.user.mention} does not have permission to assign the {verification_role.mention} role.",
                            color=discord.Color.red(),
                        )
                        await interaction.followup.send(embed=embed)
                        return
                    embed = discord.Embed(
                        title="Verification Successful",
                        description=f"You have successfully verified your account and have been assigned the {verification_role.mention} role",
                        color=discord.Color.green(),
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    embed = discord.Embed(
                        title="Verification Failed",
                        description="Your credentials are invalid. Please try again",
                        color=discord.Color.red(),
                    )
                    await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Verification Failed",
                description="This server does not have a verification role set. Please contact an admin",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="anon", description="Submits an anonymous message")
    async def send_anon_message(self, interaction: discord.Interaction, message: str, msg_id: str = ''):
        user_id = str(interaction.user.id)

        # Check if the user is banned from submitting anonymous messages
        if self.db.is_user_banned_from_confessions(user_id):
            await interaction.response.send_message(":x: You are banned from submitting anonymous messages.", ephemeral=True)
            return

        # Proceed with posting the anonymous message
        embed = discord.Embed(
            title="anonymous message",
            color=discord.Color.random(),
            description=message,
            timestamp=datetime.now()
        )

        anon_channel = self.client.get_channel(1340719909121822729)  # Channel for anonymous messages
        try:
            # If msg_id is provided, reply to that message
            msg_id = int(msg_id)
            msgObj = await anon_channel.fetch_message(msg_id)
            sent_message = await msgObj.reply(embed=embed)
        except ValueError:
            # If no valid msg_id is provided, send a new message
            sent_message = await anon_channel.send(embed=embed)

        # Send confirmation to the user
        await interaction.response.send_message(":white_check_mark: Your anonymous message has been submitted.", ephemeral=True)

        # Store message in the database with the sent message's ID
        self.db.add_confession(user_id=user_id, message_id=str(sent_message.id))


async def setup(client: commands.Bot):
    """
    Adds the cog to the bot
    """
    await client.add_cog(AuthenticationCog(client, client.db))