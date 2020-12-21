# Guilds class.
# Loads all guilds data by instantiating Shared.guild for each guild the bot is in.
# TODO add guilds whenever the bot is added to a new guild.
# TODO load all new messages sent in a guild.
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
            # Load activity role for each guild.
            self.load_activity_role(guild.id)
            # Load average words for the activity role
            self.load_avg_words_for_activity_role(guild.id)
            # Load messages for each guild.
            self.message_handler[guild.id] = MessageHandler(self.bot, guild.id)
            await self.load_messages(guild.id)

    # Set prefix for the guild.
    def set_prefix(self, guild_id, prefix):
        # Set local prefix.
        self.guilds[guild_id]['pre'] = prefix
        # Update database to reflect the prefix change.
        database.set_setting(guild_id, 'prefix', prefix)

    # Return prefix for the guild.
    def prefix(self, guild_id):
        return self.guilds[guild_id]['pre']

    # Load prefix from DB.
    def load_prefix(self, guild_id):
        # Load prefix from database.
        self.guilds[guild_id]['pre'] = database.get_setting(guild_id, 'prefix', '.')

    # Load greetings status from DB.
    def load_greetings(self, guild_id):
        self.guilds[guild_id]['welcome'] = database.get_setting(guild_id, 'welcome', True)
        self.guilds[guild_id]['goodbye'] = database.get_setting(guild_id, 'goodbye', True)

    # Save greetings status into DB.
    def save_greeting(self, guild_id, greeting, greeting_val):
        database.set_setting(guild_id, greeting, greeting_val)
        self.guilds[guild_id][greeting] = greeting_val

    # Return welcome status.
    def welcome_status(self, guild_id):
        return self.guilds[guild_id]['welcome']

    # Return goodbye status.
    def goodbye_status(self, guild_id):
        return self.guilds[guild_id]['goodbye']

    def set_avg_words_for_activity_role(self, guild_id, words):
        database.set_setting(guild_id, 'minimum_words', words)
        self.guilds[guild_id]['minimum_words'] = words

    def get_avg_words_for_activity_role(self, guild_id):
        return self.guilds[guild_id]['minimum_words']

    def load_avg_words_for_activity_role(self, guild_id):
        self.guilds[guild_id]['activity_role'] = database.get_setting(guild_id, 'activity_role')

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
    
    # Get amount of messages sent by a user after a specific date.
    def count_total_user_messages(self, guild_id, user_id, after_date=None):
        count = self.message_handler[guild_id].total_messages(user_id, after_date)
        return count

    # Get amount of words sent by a user after a specific date.
    def count_total_user_words(self, guild_id, user_id, after_date=None):
        count = self.message_handler[guild_id].total_word_count(user_id, after_date)
        return count

    def count_avg_user_messages(self, guild_id, user_id, after_date=None):
        count = self.message_handler[guild_id].average_message_count(user_id, after_date)
        return count

    def count_avg_user_words(self, guild_id, user_id, after_date=None):
        count = self.message_handler[guild_id].average_word_count(user_id, after_date)
        return count

    def set_activity_role(self, guild_id, role):
        self.guilds[guild_id]['activity_role'] = role.id
        database.set_setting(guild_id, 'activity_role', role.id)
        return

    def get_activity_role(self, guild_id):
        return self.guilds[guild_id]['activity_role']

    def load_activity_role(self, guild_id):
        self.guilds[guild_id]['activity_role'] = database.get_setting(guild_id, 'activity_role')
        return
    # TODO load messages upon joining a guild.
    # TODO load all new messages after latest one upon startup.
