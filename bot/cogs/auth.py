import logging
from typing import Optional

import discord
import requests
from discord import app_commands
from discord.ext import commands
import os
from .db import DatabaseCog
import yaml


class AuthenticationCog(commands.Cog):
    """
    This cog contains all commands and functionalities to authenticate users
    """

    def __init__(self, client: commands.Bot, db: DatabaseCog):
        self.client = client
        self.db = db
        # with open("../config.yml", "r") as file:
        #     config = yaml.safe_load(file)
        # self.verification_role_id = 
        # print(config)
        # print(self.verification_role_id

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
    @app_commands.describe(username="Your PESU Academy SRN or PRN")
    @app_commands.describe(password="Your PESU Academy password")
    async def authenticate(self, interaction: discord.Interaction, username: str, password: str):
        """
        Authenticates the user with their PESU Academy credentials
        """
        logging.info(f"Authenticating {interaction.user}")
        await interaction.response.defer(ephemeral=True)
        # try:
        #     verification_role_id = self.db.get_verification_role_for_server(guild_id=interaction.guild_id)
        # except AttributeError:
        #     verification_role_id = None
        verification_role_id = 1298119735421960275
        old_role_id = 1188111493976305806
        # print(verification_role_id)
        if verification_role_id is not None:
            verification_role = interaction.guild.get_role(verification_role_id)
            if verification_role in interaction.user.roles:
                embed = discord.Embed(
                    title="Verification Failed",
                    description=f"You are already verified on this server",
                    color=discord.Color.orange(),
                )
                
                await interaction.followup.send(embed=embed)
            else:
                authentication_result = self.check_pesu_academy_credentials(username=username, password=password)
                if authentication_result["status"]:
                    try:
                        old_role = interaction.guild.get_role(old_role_id)
                        await interaction.user.remove_roles(old_role)
                        await interaction.user.add_roles(verification_role)
                    except discord.Forbidden:
                        embed = discord.Embed(
                            title="Verification Failed",
                            description=f"{self.client.user.mention} does not have permission to assign the {verification_role.mention} role. "
                                        f"Please contact an admin to give bot the required permissions",
                            color=discord.Color.red(),
                        )
                        await interaction.followup.send(embed=embed)
                        return
                    embed = discord.Embed(
                        title="Verification Successful",
                        description=f"You have successfully verified your account and have been assigned the "
                                    f"{verification_role.mention} role",
                        color=discord.Color.green(),
                    )
                    for field in authentication_result["profile"]:
                        modified_field = field.replace("_", " ")
                        modify = lambda x: x.capitalize() if len(x) > 3 else x.upper()
                        modified_field = " ".join([modify(word) for word in modified_field.split()])
                        embed.add_field(name=modified_field, value=authentication_result["profile"][field], inline=True)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    embed = discord.Embed(
                        title="Verification Failed",
                        description=f"Your credentials are invalid. Please try again",
                        color=discord.Color.red(),
                    )
                    await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Verification Failed",
                description=f"This server does not have a verification role set. "
                            f"Please contact an admin to set a verification role",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed)


async def setup(client: commands.Bot):
    """
    Adds the cog to the bot
    """
    await client.add_cog(AuthenticationCog(client, client.db))