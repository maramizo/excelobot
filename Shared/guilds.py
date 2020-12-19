# Guilds class.
# Loads all guilds data by instantiating Shared.guild for each guild the bot is in.
# TODO add guilds whenever the bot is added to a new guild.
# TODO load all messages sent in a guild.
from Model.database import database


class Guilds:
    def __init__(self, bot):
        # Empty dict of all guilds.
        self.gu = {}
        for guild in bot.guilds:
            # Each guild has its own empty dict.
            self.gu[guild.id] = {}
            # Load the prefix for each guild.
            self.load_prefix(guild.id)

    def set_prefix(self, _id, prefix):
        # Set local prefix.
        self.gu[_id]['pre'] = prefix
        # Update database to reflect the prefix change.
        database.set_setting(_id, 'prefix', prefix)

    def prefix(self, _id):
        return self.gu[_id]['pre']

    def load_prefix(self, _id):
        # Load prefix from database.
        self.gu[_id]['pre'] = database.get_setting(_id, 'prefix')
        if self.gu[_id]['pre'] is None:
            # Default prefix is '.' if no prefix was found.
            self.gu[_id]['pre'] = '.'

