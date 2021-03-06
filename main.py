import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from Shared.guilds import Guilds
from Tasks.automations import Automations

load_dotenv()

intents = discord.Intents.default()
intents.members = True


async def determine_prefix(_bot, message):
    if message.guild:
        return _bot.my_guilds.prefix(message.guild.id)
    else:
        return '.'


bot = commands.Bot(command_prefix=determine_prefix, description="", intents=intents)

startup_extensions = ["Extensions.greetings", "Extensions.roles", "Extensions.movies"]

for extension in startup_extensions:
    try:
        bot.load_extension(extension)
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        print('Failed to load extension {}\n{}'.format(extension, exc))


@bot.event
async def on_ready():
    print(f"Connected! \nName: {bot.user.name}\tID: {bot.user.id}\n")
    bot.my_guilds = await Guilds(bot)
    tasks = await Automations(bot)


print('Version: ' + discord.__version__)
print(f'Version info: {discord.version_info}')
bot.run(os.getenv("TOKEN"))
