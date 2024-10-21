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


async def setup(client: commands.Bot):
    """
    Adds the cog to the bot
    """
    await client.add_cog(DatabaseCog(client))