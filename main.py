import discord
from discord.ext import commands

from dotenv import load_dotenv
load_dotenv()

import os

intents = discord.Intents.default()
intents.members = True
#
# bot = commands.Bot(command_prefix="#", case_insensitive=True)
#
#
# class MyClient(commands.Cog):
#     async def on_ready(self):
#         print('Logged on as {0}!'.format(self.user))
#
#     async def on_message(self, message):
#         print('Message from {0.author}: {0.content}'.format(message))
#
#     # Get member join server ID, get channel with specific name in server, send message.
#     # async def on_member_join(self, member):
#     #     joined_guild = member.guild
#     #     send_channel = discord.utils.get(joined_guild.channels, name='newcomers')
#     #     await client.get_channel(send_channel.id).send(f'**{member}** has joined {member.guild}!')
#     #
#     # async def on_member_remove(self, member):
#     #     left_guild = member.guild
#     #     send_channel = discord.utils.get(left_guild.channels, name='leavers')
#     #     await client.get_channel(send_channel.id).send(f'Aww, **{member}** has left. :(')
#
#
# client = MyClient(intents=intents)


bot = commands.Bot(command_prefix=".", description="", intents=intents)

startup_extensions = ["Misc.greetings"]

for extension in startup_extensions:
    try:
        bot.load_extension(extension)
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        print('Failed to load extension {}\n{}'.format(extension, exc))


@bot.event
async def on_ready():
    print(f"Connected! \nName: {bot.user.name}\tID: {bot.user.id}\n")


print('Version: ' + discord.__version__)
print(f'Version info: {discord.version_info}')
bot.run(os.getenv("TOKEN"))
