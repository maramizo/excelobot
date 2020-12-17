import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
intents.members = True

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
