import discord
from discord.ext import commands


class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send('Welcome {0.mention}.'.format(member))
        else:
            joined_guild = member.guild
            send_channel = discord.utils.get(joined_guild.channels, name='newcomers')
            await send_channel.send(f'**{member}** has joined {member.guild}!')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send('Welcome {0.mention}.'.format(member))
        else:
            left_guild = member.guild
            send_channel = discord.utils.get(left_guild.channels, name='leavers')
            await send_channel.send(f'Aww, **{member}** has left. :(')

    @commands.command()
    async def hello(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send(f'Hello {member.name}~')
        else:
            await ctx.send(f'Hello {member.name}... This feels familiar.')
        self._last_member = member


def setup(bot):
    bot.add_cog(Greetings(bot))