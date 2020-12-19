# Guilds class.
# Loads all guilds data by instantiating Shared.guild for each guild the bot is in.
# TODO add guilds whenever the bot is added to a new guild.
# TODO load all messages sent in a guild.
from Model.guild import Guild
from Model.database import database


class Guilds:
    def __init__(self, bot):
        self.gu = {}
        for guild in bot.guilds:
            self.gu[guild.id] = Guild(guild.id, database)

    def __setitem__(self, key, value):
        self.gu[key] = value

    def __getitem__(self, item):
        return self.gu[item]

    def set_prefix(self, _id, prefix):
        self.gu[_id].set_prefix(prefix)

    def get_prefix(self, _id):
        return self.gu[_id].prefix()
