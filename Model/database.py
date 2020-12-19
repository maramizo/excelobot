# Handles all connections to the MongoDB cluster.
# MongoDB shape: {'guild_id': ID, setting: setting_name}
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv
import os

load_dotenv()


class Database:
    default_prefix = '.'

    def __init__(self):
        self.client = MongoClient(os.getenv("DB_URL"))
        self.settings = self.client.excelobot.settings
        self.messages = self.client.excelobot.messages

    def get_setting(self, guild_id, setting, default_value=None):
        settings = self.settings.find_one({'guild_id': guild_id, setting: {"$exists": True}})
        if settings is not None:
            return settings[setting]
        return default_value

    def set_setting(self, guild_id, setting, setting_val):
        self.settings.update_one(
            {'guild_id': guild_id, setting: {"$exists": True}},
            {"$set": {setting: setting_val}},
            upsert=True
        )

    def get_messages(self, guild_id):
        return self.messages.find({'guild_id': guild_id}).sort([('message_date', ASCENDING)]).distinct('message_id')


database = Database()
