# import logging
# from typing import Optional

# import discord
# import requests
# from discord import app_commands
# from discord.ext import commands
# import os
# from .db import DatabaseCog
# import yaml


# class AuthenticationCog(commands.Cog):
#     """
#     This cog contains all commands and functionalities to authenticate users
#     """

#     def __init__(self, client: commands.Bot, db: DatabaseCog):
#         self.client = client
#         self.db = db
#         # with open("../config.yml", "r") as file:
#         #     config = yaml.safe_load(file)
#         # self.verification_role_id = 
#         # print(config)
#         # print(self.verification_role_id

#     @staticmethod
#     def check_pesu_academy_credentials(username: str, password: str) -> Optional[dict]:
#         """
#         Checks if the given credentials are valid via the pesu-auth API
#         """
#         data = {
#             'username': username,
#             'password': password,
#             'profile': True
#         }
#         response = requests.post("https://pesu-auth.onrender.com/authenticate", json=data)
#         if response.status_code == 200:
#             return response.json()

#     @app_commands.command(name="auth", description="Verify your discord account with your PESU Academy credentials")
#     @app_commands.describe(username="Your PESU Academy SRN or PRN")
#     @app_commands.describe(password="Your PESU Academy password")
#     async def authenticate(self, interaction: discord.Interaction, username: str, password: str):
#         """
#         Authenticates the user with their PESU Academy credentials
#         """
#         logging.info(f"Authenticating {interaction.user}")
#         await interaction.response.defer(ephemeral=True)
#         # try:
#         #     verification_role_id = self.db.get_verification_role_for_server(guild_id=interaction.guild_id)
#         # except AttributeError:
#         #     verification_role_id = None
#         verification_role_id = 1298119735421960275
#         old_role_id = 1188111493976305806
#         # print(verification_role_id)
#         if verification_role_id is not None:
#             verification_role = interaction.guild.get_role(verification_role_id)
#             if verification_role in interaction.user.roles:
#                 embed = discord.Embed(
#                     title="Verification Failed",
#                     description=f"You are already verified on this server",
#                     color=discord.Color.orange(),
#                 )
                
#                 await interaction.followup.send(embed=embed)
#             else:
#                 authentication_result = self.check_pesu_academy_credentials(username=username, password=password)
#                 if authentication_result["status"]:
#                     try:
#                         old_role = interaction.guild.get_role(old_role_id)
#                         await interaction.user.remove_roles(old_role)
#                         await interaction.user.add_roles(verification_role)
#                     except discord.Forbidden:
#                         embed = discord.Embed(
#                             title="Verification Failed",
#                             description=f"{self.client.user.mention} does not have permission to assign the {verification_role.mention} role. "
#                                         f"Please contact an admin to give bot the required permissions",
#                             color=discord.Color.red(),
#                         )
#                         await interaction.followup.send(embed=embed)
#                         return
#                     embed = discord.Embed(
#                         title="Verification Successful",
#                         description=f"You have successfully verified your account and have been assigned the "
#                                     f"{verification_role.mention} role",
#                         color=discord.Color.green(),
#                     )
#                     for field in authentication_result["profile"]:
#                         modified_field = field.replace("_", " ")
#                         modify = lambda x: x.capitalize() if len(x) > 3 else x.upper()
#                         modified_field = " ".join([modify(word) for word in modified_field.split()])
#                         embed.add_field(name=modified_field, value=authentication_result["profile"][field], inline=True)
#                     await interaction.followup.send(embed=embed, ephemeral=True)
#                 else:
#                     embed = discord.Embed(
#                         title="Verification Failed",
#                         description=f"Your credentials are invalid. Please try again",
#                         color=discord.Color.red(),
#                     )
#                     await interaction.followup.send(embed=embed)
#         else:
#             embed = discord.Embed(
#                 title="Verification Failed",
#                 description=f"This server does not have a verification role set. "
#                             f"Please contact an admin to set a verification role",
#                 color=discord.Color.red(),
#             )
#             await interaction.followup.send(embed=embed)


# async def setup(client: commands.Bot):
#     """
#     Adds the cog to the bot
#     """
#     await client.add_cog(AuthenticationCog(client, client.db))



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
        logging.info(f"Authenticating {interaction.user}")
        await interaction.response.defer(ephemeral=True)
        verification_role_id = 1298119735421960275  # Replace with dynamic retrieval if needed
        old_role_id = 1188111493976305806

        if verification_role_id:
            verification_role = interaction.guild.get_role(verification_role_id)
            if verification_role in interaction.user.roles:
                embed = discord.Embed(
                    title="Verification Failed",
                    description="You are already verified on this server",
                    color=discord.Color.orange(),
                )
                await interaction.followup.send(embed=embed)
            else:
                authentication_result = self.check_pesu_academy_credentials(username=username, password=password)
                if authentication_result and authentication_result["status"]:
                    try:
                        old_role = interaction.guild.get_role(old_role_id)
                        await interaction.user.remove_roles(old_role)
                        await interaction.user.add_roles(verification_role)
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

    # Confession Commands
    # @app_commands.command(name="confess", description="Submits an anonymous confession")
    # async def confess(self, interaction: discord.Interaction, confession: str, msg_id: str = ''):
    #     user_id = str(interaction.user.id)
        
    #     # Check if the user is banned before submitting confession
    #     if self.db.is_user_banned_from_confessions(user_id):
    #         await interaction.response.send_message(":x: You are banned from submitting confessions.", ephemeral=True)
    #         return

    #     # Proceed with posting the confession
    #     embed = discord.Embed(
    #         title="Anonymous Confession",
    #         color=discord.Color.random(),
    #         description=confession,
    #         timestamp=datetime.now()
    #     )

    #     confession_channel = self.client.get_channel(1299721480443007038)
    #     try:
    #         msg_id = int(msg_id)
    #         msgObj = await confession_channel.fetch_message(msg_id)
    #         await msgObj.reply(embed=embed)
    #     except ValueError:
    #         await confession_channel.send(embed=embed)
        
    #     await interaction.response.send_message(":white_check_mark: Your confession has been submitted.", ephemeral=True)
    #     self.db.add_confession(user_id=user_id, message_id=embed.id)
    # ------------
    
    @app_commands.command(name="anon", description="Submits an anonymous confession")
    async def confess(self, interaction: discord.Interaction, confession: str, msg_id: str = ''):
        user_id = str(interaction.user.id)
        
        # Check if the user is banned from submitting confessions
        if self.db.is_user_banned_from_confessions(user_id):
            await interaction.response.send_message(":x: You are banned from submitting confessions.", ephemeral=True)
            return

        # Proceed with posting the confession
        embed = discord.Embed(
            title="anonymous message",
            color=discord.Color.random(),
            description=confession,
            timestamp=datetime.now()
        )

        confession_channel = self.client.get_channel(1299721480443007038)
        try:
            # If msg_id is provided, reply to that message
            msg_id = int(msg_id)
            msgObj = await confession_channel.fetch_message(msg_id)
            sent_message = await msgObj.reply(embed=embed)
        except ValueError:
            # If no valid msg_id is provided, send a new message
            sent_message = await confession_channel.send(embed=embed)
        
        # Send confirmation to the user
        await interaction.response.send_message(":white_check_mark: Your confession has been submitted.", ephemeral=True)
        
        # Store confession in the database with the sent message's ID
        self.db.add_confession(user_id=user_id, message_id=str(sent_message.id))
    
    # ----------
    # @app_commands.command(name="confessban", description="Bans a user from submitting confessions")
    # async def confessban(self, interaction: discord.Interaction, member: discord.Member):
    #     if not any(role.id in [self.admin.id, self.mods.id] for role in interaction.user.roles):
    #         await interaction.response.send_message(":x: You are not authorized for this action.", ephemeral=True)
    #         return

    #     self.db.ban_user_from_confessions(str(member.id))
    #     await interaction.response.send_message(f"{member.mention} has been banned from submitting confessions.", ephemeral=True)
        
    #     try:
    #         await member.send("You have been banned from submitting confessions.")
    #     except discord.Forbidden:
    #         pass

    # @app_commands.command(name="confessunban", description="Unbans a user from submitting confessions")
    # async def confessunban(self, interaction: discord.Interaction, member: discord.Member):
    #     if not any(role.id in [self.admin.id, self.mods.id] for role in interaction.user.roles):
    #         await interaction.response.send_message(":x: You are not authorized for this action.", ephemeral=True)
    #         return

    #     self.db.unban_user_from_confessions(str(member.id))
    #     await interaction.response.send_message(f"{member.mention} has been unbanned from submitting confessions.", ephemeral=True)
        
    #     try:
    #         await member.send("You have been unbanned from submitting confessions.")
    #     except discord.Forbidden:
    #         pass

    # @tasks.loop(hours=24)
    # async def flush_confessions(self):
    #     """Clears cached confessions data daily."""
    #     self.confessions.clear()


async def setup(client: commands.Bot):
    """
    Adds the cog to the bot
    """
    await client.add_cog(AuthenticationCog(client, client.db))
    # await client.tree.sync()
