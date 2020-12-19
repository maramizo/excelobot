# Handles all connections to the MongoDB cluster.
# MongoDB shape: {'guild_id': ID, setting: setting_name}
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()


class Database:
    default_prefix = '.'

    def __init__(self):
        self.client = MongoClient(os.getenv("DB_URL"))
        self.settings = self.client.excelobot.settings

    def get_setting(self, guildid, setting):
        settings = self.settings.find_one({'guild_id': guildid}, {setting: 1})
        if settings is not None:
            return settings['prefix']
        return '.'

    def set_setting(self, guildid, setting, setting_val):
        self.settings.update_one(
            {'guild_id': guildid, setting: {"$exists": True}},
            {"$set": {setting: setting_val}},
            upsert=True
        )


database = Database()
