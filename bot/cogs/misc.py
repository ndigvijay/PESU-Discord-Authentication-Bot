# import discord
# from discord.ext import commands, tasks
# import time
# import re
# import logging

# class MiscCog(commands.Cog):
#     """
#     Cog for moderation commands, including mute and unmute.
#     """

#     def __init__(self, client: commands.Bot):
#         self.client = client
#         self.db = client.db  
#         self.muted_role_name = 'Muted' 
#         self.check_mutes.start()

#     @tasks.loop(seconds=60)
#     async def check_mutes(self):
#         """
#         Background task that checks for expired mutes every minute.
#         """
#         current_time = time.time()
#         mutes = self.db.get_all_mutes()
#         for mute in mutes:
#             if current_time >= mute['end_time']:
#                 guild = self.client.get_guild(mute['guild_id'])
#                 if guild is None:
#                     continue
#                 member = guild.get_member(mute['user_id'])
#                 if member:
#                     muted_role = discord.utils.get(guild.roles, name=self.muted_role_name)
#                     if muted_role:
#                         try:
#                             await member.remove_roles(muted_role, reason="Mute duration expired.")
#                             logging.info(f"Unmuted {member} in guild {guild.name}")
#                         except Exception as e:
#                             logging.error(f"Error unmuting {member}: {e}")
#                 self.db.remove_mute(mute['user_id'])

#     @commands.command(name='mute')
#     @commands.has_permissions(manage_roles=True)
#     async def mute(self, ctx, member: discord.Member = None, time_str='', *, reason: str = 'No reason provided'):
#         """
#         Mutes a member for a specified duration.

#         Usage: !mute @member 1h30m reason
#         """
#         if member is None:
#             await ctx.send("Please mention a member to mute.")
#             return
#         if not time_str:
#             await ctx.send("Please specify a duration for the mute (e.g., 1h30m).")
#             return

#         # Allow self-muting
#         if member == ctx.author:
#             pass  # Allow self-muting
#         else:
#             # Prevent muting higher roles
#             if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
#                 await ctx.send("You cannot mute a member with an equal or higher role.")
#                 return

#         # Parse duration
#         seconds = self.parse_time(time_str)
#         if seconds <= 0 or seconds > 1209600:  # 14 days in seconds
#             await ctx.send("Please enter a valid duration (up to 14 days).")
#             return

#         # Get or create muted role
#         muted_role = discord.utils.get(ctx.guild.roles, name=self.muted_role_name)
#         if muted_role is None:
#             try:
#                 muted_role = await ctx.guild.create_role(name=self.muted_role_name)
#                 for channel in ctx.guild.channels:
#                     await channel.set_permissions(muted_role, send_messages=False, speak=False)
#             except discord.Forbidden:
#                 await ctx.send("I do not have permission to create the Muted role.")
#                 return
#             except Exception as e:
#                 await ctx.send(f"An error occurred while creating the Muted role: {e}")
#                 return

#         # Apply mute
#         try:
#             if ctx.guild.me.top_role <= member.top_role:
#                 await ctx.send("I do not have permission to mute this user due to role hierarchy.")
#                 return
#             await member.add_roles(muted_role, reason=reason)
#             end_time = time.time() + seconds
#             for channel in ctx.guild.channels:
#                 if channel.name =='bot-test':
#                     await channel.set_permissions(muted_role, view_channel=True, send_messages=False, speak=False)
#                 else:
#                     await channel.set_permissions(muted_role, view_channel=False)
#             self.db.add_mute(member.id, ctx.guild.id, end_time)
#             await ctx.send(f"{member.mention} has been muted for {time_str}. Reason: {reason}")
#         except discord.Forbidden:
#             await ctx.send("I do not have permission to mute this user.")
#         except Exception as e:
#             await ctx.send(f"An error occurred: {e}")

#     def parse_time(self, time_str):
#         """
#         Parses a time string (e.g., '1h30m') into seconds.
#         """
#         time_units = {'d': 86400, 'h': 3600, 'm': 60, 's': 1}
#         matches = re.findall(r'(\d+)([dhms])', time_str.lower())
#         if not matches:
#             return 0
#         seconds = sum(int(amount) * time_units[unit] for amount, unit in matches)
#         return seconds

#     @commands.command(name='unmute')
#     @commands.has_permissions(manage_roles=True)
#     async def unmute(self, ctx, member: discord.Member = None):
#         """
#         Unmutes a member.

#         Usage: !unmute @member
#         """
#         if member is None:
#             await ctx.send("Please mention a member to unmute.")
#             return

#         muted_role = discord.utils.get(ctx.guild.roles, name=self.muted_role_name)
#         if muted_role in member.roles:
#             try:
#                 await member.remove_roles(muted_role, reason=f"Unmuted by {ctx.author}")
#                 self.db.remove_mute(member.id)
#                 await ctx.send(f"{member.mention} has been unmuted.")
#             except discord.Forbidden:
#                 await ctx.send("I do not have permission to unmute this user.")
#             except Exception as e:
#                 await ctx.send(f"An error occurred: {e}")
#         else:
#             await ctx.send("This user is not muted.")
#             self.db.remove_mute(member.id)
            
            
    

#     @check_mutes.before_loop
#     async def before_check_mutes(self):
#         """
#         Ensures the bot is ready before starting the background task.
#         """
#         await self.client.wait_until_ready()

# async def setup(client: commands.Bot):
#     """
#     Adds the cog to the bot.
#     """
#     await client.add_cog(MiscCog(client))


import discord
from discord.ext import commands, tasks
import time
import re
import logging
import asyncio

class MiscCog(commands.Cog):
    """
    Cog for moderation commands, including mute and unmute.
    """

    def __init__(self, client: commands.Bot):
        self.client = client
        self.db = client.db  # Ensure your bot has a 'db' attribute for database operations
        self.muted_role_name = 'Didnt-Listen-to-Mother'
        self.mutedict = {}  # In-memory tracking for active mutes
        self.check_mutes.start()
        self.client.add_listener(self.on_ready, 'on_ready')

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.wait_until_ready()
        self.load_active_mutes()

    def load_active_mutes(self):
        """
        Load active mutes from the database into the in-memory dictionary.
        This is essential for handling bot restarts.
        """
        mutes = self.db.get_all_mutes()
        current_time = time.time()
        for mute in mutes:
            user_id = mute['user_id']
            guild_id = mute['guild_id']
            end_time = mute['end_time']
            if end_time > current_time:
                self.mutedict[user_id] = end_time
            else:
                # If the mute has already expired, schedule immediate unmute
                asyncio.create_task(self.unmute_user(guild_id, user_id))

    @tasks.loop(seconds=60)
    async def check_mutes(self):
        """
        Background task that checks for expired mutes every minute.
        """
        current_time = time.time()
        expired = [user_id for user_id, end_time in self.mutedict.items() if current_time >= end_time]
        for user_id in expired:
            mute = self.db.get_mute(user_id)
            if not mute:
                self.mutedict.pop(user_id, None)
                continue
            guild = self.client.get_guild(mute['guild_id'])
            if guild is None:
                self.db.remove_mute(user_id)
                self.mutedict.pop(user_id, None)
                continue
            member = guild.get_member(user_id)
            if member:
                muted_role = discord.utils.get(guild.roles, name=self.muted_role_name)
                if muted_role:
                    try:
                        await member.remove_roles(muted_role, reason="Mute duration expired.")
                        logging.info(f"Unmuted {member} in guild {guild.name}")
                    except Exception as e:
                        logging.error(f"Error unmuting {member}: {e}")
            self.db.remove_mute(user_id)
            self.mutedict.pop(user_id, None)

    async def unmute_user(self, guild_id: int, user_id: int):
        """
        Unmute a user by removing the Muted role.
        """
        guild = self.client.get_guild(guild_id)
        if guild is None:
            return
        member = guild.get_member(user_id)
        if member:
            muted_role = discord.utils.get(guild.roles, name=self.muted_role_name)
            if muted_role:
                try:
                    await member.remove_roles(muted_role, reason="Mute duration expired.")
                    logging.info(f"Unmuted {member} in guild {guild.name}")
                except Exception as e:
                    logging.error(f"Error unmuting {member}: {e}")
        self.db.remove_mute(user_id)
        self.mutedict.pop(user_id, None)

    @commands.command(name='mute')
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member = None, time_str='', *, reason: str = 'No reason provided'):
        """
        Mutes a member for a specified duration.

        Usage: !mute @member 1h30m reason
        """
        if member is None:
            await ctx.send("Please mention a member to mute.")
            return
        if not time_str:
            await ctx.send("Please specify a duration for the mute (e.g., 1h30m).")
            return

        # Prevent muting users with higher or equal roles
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("You cannot mute a member with an equal or higher role.")
            return

        # Prevent the bot from muting itself
        if member == ctx.guild.me:
            await ctx.send("I cannot mute myself.")
            return

        # Parse duration
        seconds = self.parse_time(time_str)
        if seconds <= 0 or seconds > 1209600:  # 14 days in seconds
            await ctx.send("Please enter a valid duration (up to 14 days).")
            return

        # Get or create muted role
        muted_role = discord.utils.get(ctx.guild.roles, name=self.muted_role_name)
        if muted_role is None:
            try:
                muted_role = await ctx.guild.create_role(name=self.muted_role_name)
                # Set permissions for the muted role in each channel
                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted_role, 
                        send_messages=False, 
                        speak=False, 
                        add_reactions=False,
                        send_messages_in_threads=False,
                        create_public_threads=False,
                        create_private_threads=False)
            except discord.Forbidden:
                await ctx.send("I do not have permission to create the Muted role.")
                return
            except Exception as e:
                await ctx.send(f"An error occurred while creating the Muted role: {e}")
                return

        # Ensure the bot's highest role is above the Muted role
        if ctx.guild.me.top_role <= muted_role:
            await ctx.send("Please ensure my highest role is above the Muted role.")
            return

        # Apply mute
        try:
            await member.add_roles(muted_role, reason=reason)
            end_time = time.time() + seconds

            # Save mute to the database and in-memory dict
            self.db.add_mute(member.id, ctx.guild.id, end_time)
            self.mutedict[member.id] = end_time

            await ctx.send(f"{member.mention} has been muted for {time_str}. Reason: {reason}")
            logging.info(f"{member} has been muted in {ctx.guild.name} for {time_str} by {ctx.author}")
        except discord.Forbidden:
            await ctx.send("I do not have permission to mute this user.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command(name='unmute')
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member = None):
        """
        Unmutes a member.

        Usage: !unmute @member
        """
        if member is None:
            await ctx.send("Please mention a member to unmute.")
            return

        muted_role = discord.utils.get(ctx.guild.roles, name=self.muted_role_name)
        if muted_role in member.roles:
            try:
                await member.remove_roles(muted_role, reason=f"Unmuted by {ctx.author}")
                self.db.remove_mute(member.id)
                self.mutedict.pop(member.id, None)
                await ctx.send(f"{member.mention} has been unmuted.")
                logging.info(f"{member} has been unmuted in {ctx.guild.name} by {ctx.author}")
            except discord.Forbidden:
                await ctx.send("I do not have permission to unmute this user.")
            except Exception as e:
                await ctx.send(f"An error occurred: {e}")
        else:
            await ctx.send("This user is not muted.")

    @commands.command(name='selfmute')
    @commands.cooldown(rate=1, per=3600, type=commands.BucketType.user)  # 1 use per hour per user
    @commands.has_permissions(manage_roles=False)  # Regular users without manage_roles
    async def selfmute(self, ctx, time_str='', *, reason: str = 'No reason provided'):
        """
        Allows users to mute themselves for a specified duration.

        Usage: !selfmute 1h30m reason
        """
        member = ctx.author

        if not time_str:
            await ctx.send("Please specify a duration for the mute (e.g., 1h30m).")
            return

        # Parse duration
        seconds = self.parse_time(time_str)
        if seconds <= 0 or seconds > 3600:  # 1 hour in seconds
            await ctx.send("Please enter a valid duration (up to 1 hour).")
            return

        # Get or create muted role
        muted_role = discord.utils.get(ctx.guild.roles, name=self.muted_role_name)
        if muted_role is None:
            try:
                muted_role = await ctx.guild.create_role(name=self.muted_role_name)
                # Set permissions for the muted role in each channel
                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted_role, 
                        send_messages=False, 
                        speak=False, 
                        add_reactions=False,
                        send_messages_in_threads=False,
                        create_public_threads=False,
                        create_private_threads=False)
            except discord.Forbidden:
                await ctx.send("I do not have permission to create the Muted role.")
                return
            except Exception as e:
                await ctx.send(f"An error occurred while creating the Muted role: {e}")
                return

        # Ensure the bot's highest role is above the Muted role
        if ctx.guild.me.top_role <= muted_role:
            await ctx.send("Please ensure my highest role is above the Muted role.")
            return

        # Prevent users from muting themselves multiple times
        if muted_role in member.roles:
            await ctx.send("You are already muted. Please unmute yourself before muting again.")
            return

        # Apply mute
        try:
            await member.add_roles(muted_role, reason=reason)
            end_time = time.time() + seconds

            # Save mute to the database and in-memory dict
            self.db.add_mute(member.id, ctx.guild.id, end_time)
            self.mutedict[member.id] = end_time

            await ctx.send(f"You have been muted for {time_str}. Reason: {reason}")
            logging.info(f"{member} has self-muted in {ctx.guild.name} for {time_str}")
        except discord.Forbidden:
            await ctx.send("I do not have permission to mute you.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @selfmute.error
    async def selfmute_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Please wait {int(error.retry_after)} seconds before using this command again.")
        else:
            raise error

    @commands.command(name='selfunmute')
    @commands.has_permissions(manage_roles=False)  # Regular users without manage_roles
    async def selfunmute(self, ctx):
        """
        Allows users to unmute themselves before the mute duration expires.

        Usage: !selfunmute
        """
        member = ctx.author
        muted_role = discord.utils.get(ctx.guild.roles, name=self.muted_role_name)

        if muted_role not in member.roles:
            await ctx.send("You are not muted.")
            return

        try:
            await member.remove_roles(muted_role, reason="User self-unmuted.")
            self.db.remove_mute(member.id)
            self.mutedict.pop(member.id, None)
            await ctx.send("You have been unmuted.")
            logging.info(f"{member} has self-unmuted in {ctx.guild.name}")
        except discord.Forbidden:
            await ctx.send("I do not have permission to unmute you.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    def parse_time(self, time_str):
        """
        Parses a time string (e.g., '1h30m') into seconds.
        """
        time_units = {'d': 86400, 'h': 3600, 'm': 60, 's': 1}
        pattern = re.compile(r'(\d+)([dhms])')
        matches = pattern.findall(time_str.lower())
        if not matches:
            return 0
        seconds = sum(int(amount) * time_units[unit] for amount, unit in matches)
        return seconds

    @check_mutes.before_loop
    async def before_check_mutes(self):
        """
        Ensures the bot is ready before starting the background task.
        """
        await self.client.wait_until_ready()

async def setup(client: commands.Bot):
    """
    Adds the cog to the bot.
    """
    await client.add_cog(MiscCog(client))
