# TODO
#  Command: findmovie|fm <MovieName>
#  Result:
#       -> 720p 1080p All reactions added for user to filter out movie type.
#           -> On react result:
#           -> Embed of all movies with the name.
#           -> Reactions added to embed if more than 1 exist "<-" "->".
#           -> On user clicking embeds, they shift through array.
#           -> Checkmark reaction added for user to select the movie.
import discord
from discord.ext import commands, tasks
import typing
from Model.indexedmessage import IndexedMessage
from Shared.movies import MovieHandler
import requests
from dotenv import load_dotenv
from threading import Timer
import os
import asyncio

load_dotenv()


def formatEmbed(movie):
    icon = 'https://cdn.discordapp.com/icons/718283348681687082/2c5557b3a168a323771a3798303a3b93.webp?size=128'
    embed = discord.Embed(title=movie['title_long'], description=movie['summary'], color=7950900)
    embed.set_author(name='Excelobot', url='https://github.com/maramizo/excelobot', icon_url=icon)
    embed.set_footer(text="Made with ❤️", icon_url=icon)
    embed.set_image(url=movie['medium_cover_image'])
    embed.add_field(name="IMDb Rating", value=movie['rating'])
    embed.add_field(name="YouTube Trailer", value=f"https://youtube.com/{movie['yt_trailer_code']}")
    embed.add_field(name="Duration", value=f"{movie['runtime']} minutes")
    return embed


emojis = {
    'LEFT_ARROW': '\U00002b05\U0000fe0f',
    'RIGHT_ARROW': '\U000027a1\U0000fe0f',
    'CHECK': '<:check:791611554297937920>',
    '720p': '<:720p:791607639690838026>',
    '1080p': '<:1080p:791607640055742494>'
}


class Movies(commands.Cog):
    movieTypes = ['720', '1080', '720p', '1080p', 'all']

    def __init__(self, bot):
        self.bot = bot
        self.indices = {}
        self.movies = {}
        self.tasks = {}

    def movie_type(self, value):
        value = value.lower()
        if value == self.movieTypes[0] or value == self.movieTypes[2]:
            return self.movieTypes[2]
        elif value == self.movieTypes[1] or value == self.movieTypes[3]:
            return self.movieTypes[3]
        return self.movieTypes[4]

    def is_a_movie_type(self, value):
        if value in self.movieTypes:
            return True
        return False

    def waiting_for_user_input(self, user_id):
        for index in self.indices:
            if self.indices[index].author == user_id:
                return index
        return False

    def clean_arrays(self, key):
        del self.indices[key]
        del self.movies[key]
        return

    async def create_movie(self, uri, password, m_id):
        res = requests.get(os.getenv("WEBSITE_URL") + os.getenv("WEBSITE_ROOM_ENDPOINT"),
                           params={'uri': uri, 'password': password}).json()
        room_id = res['id']
        url = res['url']
        validation = res['validation']
        self.tasks[m_id] = self.check_progress.start(m_id, room_id, url, validation)
        return

    @tasks.loop(seconds=5)
    async def check_progress(self, m_id, room_id, url, validation):
        res = requests.get(os.getenv("WEBSITE_URL") + '/room/' + str(room_id) + '/progress')
        print(res)
        print('got response')
        res = res.json()
        if 'progress' in res and res['progress'] < 100:
            message = await self.indices[m_id].channel.fetch_message(m_id)
            await message.edit(content=f"Preparing your room. Current"
                                       f" progress: {0 if res['progress'] is None else res['progress']}%")
        else:
            url = os.getenv("WEBSITE_URL") + url
            print(f"Room created! Please type in '{validation}' to validate your ownership.\n"
                  f"Room URL: {url}")
            author = await self.bot.fetch_user(self.indices[m_id].author)
            await author.send(f"Room created! Please type in '{validation}' to validate your ownership.\n"
                              f"Room URL: {url}")
            self.tasks[m_id].cancel()
            self.clean_arrays(m_id)
        return

    @commands.Cog.listener()
    async def on_message(self, message):
        message_id = self.waiting_for_user_input(message.author.id)
        if isinstance(message.channel, discord.channel.DMChannel) and message_id:
            password = message.content
            if len(message.content) > 10:
                password = message.content[:10]
            await message.channel.send(f"Your password is:\n{password}\nEveryone needs to enter the password to join"
                                       f"the room.")
            index = self.indices[message_id].index
            await self.create_movie(self.movies[message_id].get_uri(index), password, message_id)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        await self.on_reaction_add(reaction, user)
        return

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # If the bot has reactions to check, and the reaction message is one of them, and the bot is
        # listening for checks specifically from this user, and the react is either <- or ->
        if self.indices is not False and reaction.message.id in self.indices and \
                self.indices[reaction.message.id].author == user.id:
            m_id = reaction.message.id
            index = self.indices[m_id].index
            if reaction.emoji == emojis['LEFT_ARROW'] or reaction.emoji == emojis['RIGHT_ARROW']:
                if reaction.emoji == emojis['LEFT_ARROW']:
                    index = self.indices[m_id].prev()
                else:
                    index = self.indices[m_id].next()
                movie = self.movies[m_id].get(index)
                embed = formatEmbed(movie)
                await reaction.message.edit(embed=embed)
            elif str(reaction.emoji) == emojis['CHECK'] and self.movies[m_id].get_quality() == 'All':
                movie = self.movies[m_id].get(index)
                await reaction.message.edit(content=f"You have selected {movie['title']}, please choose the quality:")
                await reaction.message.clear_reactions()
                if self.movies[m_id].has_quality(index, '720p'):
                    await reaction.message.add_reaction(emojis['720p'])
                if self.movies[m_id].has_quality(index, '1080p'):
                    await reaction.message.add_reaction(emojis['1080p'])
            elif str(reaction.emoji) == emojis['720p'] \
                    or str(reaction.emoji) == emojis['1080p']:
                if str(reaction.emoji) == emojis['720p']:
                    self.movies[m_id].set_quality('720p')
                else:
                    self.movies[m_id].set_quality('1080p')
                await reaction.message.clear_reactions()
                await reaction.message.edit(content=f"If you would like to have a password, "
                                                    f"please DM me, otherwise, click {emojis['CHECK']}")
                await reaction.message.add_reaction(emojis["CHECK"])
            elif str(reaction.emoji) == emojis['CHECK']:
                movie = self.movies[m_id].get(index)
                uri = self.movies[m_id].get_uri(index)
                quality = self.movies[m_id].get_quality()
                await reaction.message.edit(
                    content=f"{movie['title']} picked with {quality} quality."
                            f" Creating an online page for you to stream now.")
                await self.create_movie(uri, '', reaction.message.id)

    @commands.command(require_var_positional=True, aliases=['fm', 'findmovie'])
    async def find_movie(self, ctx, *name, quality: typing.Optional[str] = 'All'):
        last_name = name[-1]
        if self.is_a_movie_type(last_name):
            name = ' '.join(name[:-1])
            quality = self.movie_type(last_name)
        else:
            name = ' '.join(name)
        if name is False:
            await ctx.send(f'Usage: {ctx.prefix}{ctx.command} <Movie Name> <Optional: **720p**, 1080p, '
                           f'All>')
        else:
            movies = MovieHandler(name, quality)
            if movies.get():
                await ctx.send(f'Found {movies.count()} movies')
                movie = movies.get()[0]
                embed = formatEmbed(movie)
                message = await ctx.send(embed=embed)
                self.indices[message.id] = IndexedMessage(0, movies.count(), ctx.author.id, ctx.channel)
                self.movies[message.id] = movies
                await message.add_reaction("\U00002b05\U0000fe0f")
                await message.add_reaction("<:check:791611554297937920>")
                await message.add_reaction("\U000027a1\U0000fe0f")
            else:
                await ctx.send(f'Could not find "{name}".')


def setup(bot):
    bot.add_cog(Movies(bot))
