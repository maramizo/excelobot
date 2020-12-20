# Guilds class.
# Loads all guilds data by instantiating Shared.guild for each guild the bot is in.
# TODO add guilds whenever the bot is added to a new guild.
# TODO load all messages sent in a guild.
from Model.database import database
from Model.messages import MessageHandler
from asyncinit import asyncinit
import datetime
from discord import TextChannel

# Guilds Class
# Acts as a wrapper class for database & messages classes.
# Handles all the logic required in commands to prevent class confusion.

@asyncinit
class Guilds:

    async def __init__(self, bot):
        self.bot = bot
        # Empty dict of all guilds.
        self.guilds = {}
        self.message_handler = {}
        for guild in bot.guilds:
            # Each guild has its own empty dict.
            self.guilds[guild.id] = {}
            # Load the prefix for each guild.
            self.load_prefix(guild.id)
            # Load greeting settings for each guild.
            self.load_greetings(guild.id)
            self.message_handler[guild.id] = MessageHandler(self.bot, guild.id)
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

    # Instantiates a MessageHandler() object for each guild.
    # Loops over all channels in guild.
    # Checks if channel is text, if it is, gets the oldest message.
    # If the oldest is younger than a week, requests more data.
    # If there's no existing data, it loads more messages using API.
    # TODO move the loading logic of messages from here to MessageHandler()
    async def load_messages(self, guild_id):
        if self.message_handler[guild_id].messages_exist_for_guild():
            for channel in self.bot.get_guild(guild_id).channels:
                if isinstance(channel, TextChannel):
                    oldest = self.message_handler[guild_id].get_oldest_message(channel.id)

                    # If there's existing data for this channel, check its date.
                    if oldest:
                        date_time_diff = datetime.datetime.now() - oldest.created_at
                        if(date_time_diff.days < 7):
                            await self.message_handler[guild_id].load_channel_messages(channel.id, oldest)

                    # Check if there's existing data for this channel now.
                    else:
                        await self.message_handler[guild_id].load_channel_messages(channel.id)
        else:
            await self.message_handler[guild_id].load_messages()
    
    # TODO get amount of words per user in a channel.
    #  Load all messages from a certain user in DB.
    #  Get total amount of words, divide them by total amount of messages.
    def count_total_user_messages(self, guild_id, user_id):
        count = self.message_handler[guild_id].total_messages(user_id)
        return count

    def count_total_user_words(self, guild_id, user_id):
        count = self.message_handler[guild_id].total_word_count(user_id)
        return count

    # TODO load messages upon joining a guild.
    # TODO load all new messages after latest one upon startup.
