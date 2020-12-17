import discord
from discord.ext import commands


class Greetings(commands.Cog):
    welcome_enabled = True
    goodbye_enabled = True

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    async def cog_check(self, ctx):
        # Check if  user has admin role
        return ctx.author.guild_permissions.administrator

    @commands.Cog.listener()
    async def on_command_error(self, ctx):
        await ctx.send('You are not authorized to use this command. :(')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if self.welcome_enabled is False:
            return
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Welcome {member.mention}.')
        else:
            joined_guild = member.guild
            send_channel = discord.utils.get(joined_guild.channels, name='newcomers')
            await send_channel.send(f'**{member}** has joined {member.guild}!')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = member.guild.system_channel
        if self.goodbye_enabled is False:
            return
        if channel is not None:
            await channel.send(f'Welcome {member.mention}.')
        else:
            left_guild = member.guild
            send_channel = discord.utils.get(left_guild.channels, name='leavers')
            await send_channel.send(f'Aww, **{member}** has left. :(')

    @commands.command()
    async def goodbye(self, ctx, *, member: discord.Member = None):
        self.goodbye_enabled = not self.goodbye_enabled
        status_string = '' if self.goodbye_enabled else 'not '
        await ctx.send(f'I\'m now {status_string}saying goodbye.')

    @commands.command()
    async def hello(self, ctx, *, member: discord.Member = None):
        self.welcome_enabled = not self.welcome_enabled
        status_string = '' if self.welcome_enabled else 'not '
        await ctx.send(f'I\'m now {status_string}saying hello.')


def setup(bot):
    bot.add_cog(Greetings(bot))
