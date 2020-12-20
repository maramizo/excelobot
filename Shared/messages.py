import discord
from Model.database import database
import datetime
from Model.structifier import Struct


def valid_message(message):
    if message and len(message.content) > 1:
        return True
    return False

def is_user_message(message, user_id):
    if isinstance(message.author, int):
        author = message.author
    else:
        author = message.author.id
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
    def get_oldest_message(self, channel_id=None):
        oldest_message = {}
        if channel_id is None:
            # If no specific channel is given, find oldest message in entire server.
            for channel in self.messages:
                for message_id in self.messages[channel]:
                    message = self.messages[channel][message_id]
                    if not oldest_message or oldest_message.created_at > message.created_at:
                        oldest_message = message
            self.oldest_message = oldest_message
            return oldest_message
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
    def total_messages(self, user_id):
        count = 0
        for channel_id in self.messages:
            for message_id in self.messages[channel_id]:
                message = self.messages[channel_id][message_id]
                if is_user_message(message, user_id):
                    count += 1
        return count

    def total_word_count(self, user_id):
        count = 0
        for channel_id in self.messages:
            for message_id in self.messages[channel_id]:
                message = self.messages[channel_id][message_id]
                if is_user_message(message, user_id):
                    content = message.content
                    count += len(content.split())
        return count
