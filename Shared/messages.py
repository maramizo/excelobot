import discord
from Model.database import database
import datetime


def valid_message(message):
    if message and len(message.content) > 1:
        return True
    return False


class MessageHandler:
    def __init__(self, bot, guild_id):
        self.bot = bot
        self.guild = bot.get_guild(guild_id)
        self.messages = {}
        self.oldest_message = {}

    def messages_exist_for_guild(self):
        self.messages = database.get_messages(self.guild.id)
        if self.messages:
            return True
        return False

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
            # print(f'{oldest_message.author} wrote {oldest_message.content} at {oldest_message.created_at}')
            return oldest_message
        else:
            for message_id in self.messages[channel_id]:
                message = self.messages[channel_id][message_id]
                if not oldest_message or oldest_message.created_at > message.created_at:
                    oldest_message = message
        # print(f'{oldest_message.author} wrote {oldest_message.content} at {oldest_message.created_at}')
        return oldest_message

    # Load all messages in all channels in the guild
    # Keep loading messages until date > 1 week OR none found
    # Store all loaded messages in self.messages[channel.id]
    async def load_messages(self):
        print(f'load messages called')
        self.messages = {}
        for channel in self.guild.channels:
            if channel.type is discord.ChannelType.text:
                self.messages[channel.id] = {}
                await self.load_channel_messages(channel.id)

    async def load_channel_messages(self, channel_id, _oldest_message=None, times_called=1, _limit=50):
        try:
            channel = self.bot.get_channel(channel_id)
            if _oldest_message:
                messages = await channel.history(limit=_limit * times_called, before=_oldest_message).flatten()
            else:
                messages = await channel.history(limit=_limit * times_called).flatten()
        except discord.errors.Forbidden:
            print("Don't have access to this channel. SKIPPING")
        except discord.errors.HTTPException:
            print('Request to get messages failed')
        else:
            # Check if messages are valid, and add them to array belonging to their channel.
            messages_exist = False
            for message in messages:
                if valid_message(message):
                    self.messages[channel.id][message.id] = message
                    messages_exist = True
            # If there are any new messages grabbed, continue.
            if messages_exist:
                # Grab oldest message through get_oldest_message
                oldest_message = self.get_oldest_message(channel.id)
                # If there is a valid message in the channel.
                if oldest_message:
                    date_time_diff = datetime.datetime.now() - oldest_message.created_at
                    print(
                        f'Now: {datetime.datetime.now()} - Oldest Message {oldest_message.created_at} - '
                        f'Channel {oldest_message.channel} - Content {oldest_message.content} - '
                        f'Time diff: {date_time_diff} : {date_time_diff.days > 6}')
                    # If the message is younger than a week old.
                    if date_time_diff.days < 7:
                        # Load more messages with this message as the oldest.
                        await self.load_channel_messages(channel.id, oldest_message, times_called + 1, 50)
                    else:
                        self.store_messages(channel.id)
            else:
                self.store_messages(channel.id)

    # TODO Store messages in DB.
    def store_messages(self, channel_id):
        print(f'storing messages for {channel_id}')

    # TODO load oldest message from DB.
    #  Add a quick check to see if any messages exist before it.
    #  If they exist use load_channel_messages to load older ones.
