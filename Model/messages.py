import discord
from Model.database import database
import datetime
from Model.structifier import Struct


def valid_message(message):
    if message and len(message.content) > 1:
        return True
    return False


def is_valid_user_message(message, user_id, after_date=None):
    if isinstance(message.author, int):
        author = message.author
    else:
        author = message.author.id
    if after_date is not None:
        return author == user_id and (after_date is None or message.created_at > after_date)
    return author == user_id


# MessageHandler class:
# Instantiated for each guild.
# Loads user's messages from DB.
# Loads extra messages using Discord API.
# Stores data.
# Contains all the logic for how to load and save messages.


class MessageHandler:
    def __init__(self, bot, guild_id):
        self.bot = bot
        self.guild = bot.get_guild(guild_id)
        self.messages = {}
        self.oldest_message = {}
        self.load_db_messages()
        self.new_messages_loaded = False

    # Loads messages for current guild from the database.
    def load_db_messages(self):
        self.messages = {}
        messages = database.get_messages(self.guild.id)
        for channel in self.guild.channels:
            self.messages[channel.id] = {}
        if messages:
            for message in messages:
                message = Struct(**message)
                message.id = int(message.id)
                self.messages[message.channel_id][message.id] = message

    # Checks if there are any messages in this instance.
    def messages_exist_for_guild(self):
        if self.messages:
            return True
        return False

    # Loops over existing (stored) messages and returns the oldest one.
    # If no channel_id is passed, it loops over all guilds.
    # If no user_id is passed, it gets oldest message of any user.
    # If no after_date is passed, it gets the oldest message regardless of date.
    def get_oldest_message(self, channel_id=None, user_id=None, after_date=None):
        oldest_message = {}
        if channel_id is None:
            # If no specific channel is given, find oldest message in entire server.
            for channel in self.messages:
                for message_id in self.messages[channel]:
                    message = self.messages[channel][message_id]
                    if (not oldest_message or (
                            after_date is not None and oldest_message.created_at > message.created_at
                            and oldest_message.created_at > after_date)) \
                            and (user_id is None or is_valid_user_message(message, user_id, after_date)):
                        oldest_message = message
            self.oldest_message = oldest_message
        else:
            for message_id in self.messages[channel_id]:
                message = self.messages[channel_id][message_id]
                if not oldest_message or oldest_message.created_at > message.created_at:
                    oldest_message = message
        return oldest_message

    # Loops over all of the channels and calls load_channel_messages().
    async def load_messages(self):
        self.messages = {}
        # Load all messages in all channels in the guild
        for channel in self.guild.channels:
            if channel.type is discord.ChannelType.text:
                self.messages[channel.id] = {}
                # Initial messages loading.
                await self.load_channel_messages(channel.id)

    # Initial load only loads 50 messages, then increments of 50 every time it's called afterwards.
    async def load_channel_messages(self, channel_id, _oldest_message=None, times_called=1, _limit=50):
        channel = {}
        try:
            channel = self.bot.get_channel(channel_id)
            if _oldest_message:
                messages = await channel.history(limit=_limit * times_called, before=_oldest_message).flatten()
            else:
                messages = await channel.history(limit=_limit * times_called).flatten()
        except discord.errors.Forbidden:
            print(f"Don't have access to channel {channel}. SKIPPING")
        except discord.errors.HTTPException:
            print('Request to get messages failed')
        else:
            # Check if messages are valid, and add them to array belonging to their channel.
            messages_exist = False
            for message in messages:
                if valid_message(message):
                    self.new_messages_loaded = True
                    self.messages[channel.id][message.id] = message
                    messages_exist = True
            # If there are any new messages grabbed, continue.
            if messages_exist:
                # Grab oldest message through get_oldest_message
                oldest_message = self.get_oldest_message(channel.id)
                # If there is a valid message in the channel.
                if oldest_message:
                    date_time_diff = datetime.datetime.now() - oldest_message.created_at
                    # print(
                    #     f'Now: {datetime.datetime.now()} - Oldest Message {oldest_message.created_at} - '
                    #     f'Channel {oldest_message.channel} - Content {oldest_message.content} - '
                    #     f'Time diff: {date_time_diff} : {date_time_diff.days > 6}')
                    # If the message is younger than a week old.
                    if date_time_diff.days < 7:
                        # Load more messages with this message as the oldest.
                        await self.load_channel_messages(channel.id, oldest_message, times_called + 1, 50)
                    else:
                        # Store existing messages if there is a message older than a week.
                        self.store_messages(channel.id)
            # If there are no grabbed messages, simply store the existing ones.
            elif self.new_messages_loaded:
                self.store_messages(channel.id)

    def store_messages(self, channel_id):
        formatted_messages = self.format_messages(channel_id)
        if formatted_messages:
            database.store_messages(formatted_messages)

    # Format messages for storage.
    def format_messages(self, channel_id):
        formatted_messages = []
        for message_id in self.messages[channel_id]:
            message = self.messages[channel_id][message_id]
            if isinstance(message.author, int):
                author = message.author
            else:
                author = message.author.id
            formatted_messages.append({'guild_id': self.guild.id, 'channel_id': channel_id, 'author': author,
                                       'content': message.content, 'created_at': message.created_at, 'id': message.id})
        return formatted_messages

    # Counts user messages sent across a guild.
    def total_messages(self, user_id, after_date=None):
        count = 0
        for channel_id in self.messages:
            for message_id in self.messages[channel_id]:
                message = self.messages[channel_id][message_id]
                if is_valid_user_message(message, user_id, after_date):
                    count += 1
        return count

    def total_word_count(self, user_id, after_date=None):
        count = 0
        for channel_id in self.messages:
            for message_id in self.messages[channel_id]:
                message = self.messages[channel_id][message_id]
                if is_valid_user_message(message, user_id, after_date):
                    content = message.content
                    count += len(content.split())
        return count

    def average_word_count(self, user_id, after_date=None):
        count = self.total_word_count(user_id, after_date)
        if count:
            if after_date is not None:
                date_diff = datetime.datetime.now() - after_date
            else:
                oldest_message = self.get_oldest_message(user_id=user_id)
                if oldest_message:
                    date_diff = datetime.datetime.now() - oldest_message.created_at
                else:
                    date_diff = 1
            days = date_diff.days
            return count / days
        return 0

    def average_message_count(self, user_id, after_date=None):
        count = self.total_messages(user_id, after_date)
        if after_date is not None:
            date_diff = datetime.datetime.now() - after_date
        else:
            oldest_message = self.get_oldest_message(user_id=user_id)
            date_diff = datetime.datetime.now() - oldest_message.created_at
        days = date_diff.days
        return count / days
