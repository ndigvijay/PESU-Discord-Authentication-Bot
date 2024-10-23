from discord.ext import commands

from pymongo import MongoClient


class DatabaseCog(commands.Cog):
    """
    This cog contains all database utilities
    """

    def __init__(self, client: commands.Bot):
        self.client = client
        self.mongo_client = MongoClient(client.config["db"])
        self.db = self.mongo_client["pesu_auth_bot_db"]
        self.collection = self.db["verification"]
        self.mutes_collection = self.db["mutes"]

    def add_server(self, guild_id: str):
        """
        Adds a server to the database
        """
        record = {
            "guild_id": guild_id,
            "verification_role_id": None,
        }
        self.collection.insert_one(record)

    def remove_server(self, guild_id: int):
        """
        Removes a server from the database
        """
        self.collection.delete_one({"guild_id": guild_id})

    def get_verification_role_for_server(self, guild_id: int):
        """
        Gets the verification role for a server
        """
        try:
            return self.collection.find_one({"guild_id": guild_id}).get("verification_role_id", None)
        except AttributeError:
            self.add_server(guild_id)
            return None

    def add_verification_role(self, guild_id: int, role_id: int):
        """
        Adds a verification role to a server
        """
        self.collection.update_one({"guild_id": guild_id}, {"$set": {"verification_role_id": role_id}})

    def remove_verification_role(self, guild_id: int):
        """
        Removes a verification role from a server
        """
        self.collection.update_one({"guild_id": guild_id}, {"$unset": {"verification_role_id": ""}})
        
    def add_mute(self, user_id: int, guild_id: int, end_time: float):
        """
        Adds a mute record to the database.
        """
        record = {
            "user_id": user_id,
            "guild_id": guild_id,
            "end_time": end_time
        }
        self.mutes_collection.update_one(
            {"user_id": user_id},
            {"$set": record},
            upsert=True
        )

    def remove_mute(self, user_id: int):
        """
        Removes a mute record from the database.
        """
        self.mutes_collection.delete_one({"user_id": user_id})

    def get_all_mutes(self):
        """
        Retrieves all mute records from the database.
        """
        return list(self.mutes_collection.find())

    def get_mute(self, user_id: int):
        """
        Retrieves a mute record for a specific user.
        """
        return self.mutes_collection.find_one({"user_id": user_id})


async def setup(client: commands.Bot):
    """
    Adds the cog to the bot
    """
    await client.add_cog(DatabaseCog(client))