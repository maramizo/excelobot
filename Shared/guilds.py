# Guilds class.
# Loads all guilds data by instantiating Shared.guild for each guild the bot is in.
# TODO add guilds whenever the bot is added to a new guild.
# TODO load all messages sent in a guild.
from Model.database import database
from Shared.messages import MessageHandler
from asyncinit import asyncinit


@asyncinit
class Guilds:

    async def __init__(self, bot):
        self.bot = bot
        # Empty dict of all guilds.
        self.guilds = {}
        for guild in bot.guilds:
            # Each guild has its own empty dict.
            self.guilds[guild.id] = {}
            # Load the prefix for each guild.
            self.load_prefix(guild.id)
            # Load greeting settings for each guild.
            self.load_greetings(guild.id)
            # Load messages for each guild.
            await self.load_messages(guild.id)

    def set_prefix(self, guild_id, prefix):
        # Set local prefix.
        self.guilds[guild_id]['pre'] = prefix
        # Update database to reflect the prefix change.
        database.set_setting(guild_id, 'prefix', prefix)

    def prefix(self, guild_id):
        return self.guilds[guild_id]['pre']

    def load_prefix(self, guild_id):
        # Load prefix from database.
        self.guilds[guild_id]['pre'] = database.get_setting(guild_id, 'prefix', '.')

    def load_greetings(self, guild_id):
        self.guilds[guild_id]['welcome'] = database.get_setting(guild_id, 'welcome', True)
        self.guilds[guild_id]['goodbye'] = database.get_setting(guild_id, 'goodbye', True)

    def save_greeting(self, guild_id, greeting, greeting_val):
        database.set_setting(guild_id, greeting, greeting_val)
        self.guilds[guild_id][greeting] = greeting_val

    def welcome_status(self, guild_id):
        return self.guilds[guild_id]['welcome']

    def goodbye_status(self, guild_id):
        return self.guilds[guild_id]['goodbye']

    # Load all messages for guild.
    # Get existing messages for each guild channel.
    # If any are found, get oldest.
    # If the oldest is less than a week ago, get more messages.
    # Get messages until the date is more than a week ago or none are found.
    
    async def load_messages(self, guild_id):
        message_handler = MessageHandler(self.bot, guild_id)
        if message_handler.messages_exist_for_guild():
            oldest = message_handler.get_oldest_message()
            # if oldest.date > 1 week ago
            # get more messages
        else:
            print(f'Loading messages for guild {guild_id}')
            await message_handler.load_messages()
    
    # TODO get amount of words per user in a channel.
    #  Load all messages from a certain user in DB.
    #  Get total amount of words, divide them by total amount of messages.
