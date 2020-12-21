import discord
from discord.ext import commands


class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Only admins are allowed to use commands within this cog.
    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    # TODO move on_command_error to an error handling class.
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(f'{error}')
        if isinstance(error, commands.CheckFailure):
            await ctx.send('You are not authorized to use this command. :(')
        elif isinstance(error, commands.MissingRequiredArgument):
            params = ''
            for param in ctx.command.clean_params:
                params = f'{params} {param}'
            await ctx.send(f'**Usage:**\n{ctx.prefix}{ctx.command.name}{params}')
        else:
            await ctx.send(error)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if self.bot.my_guilds[member.guild.id]['welcome'] is False:
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
        if self.bot.my_guilds[member.guild.id]['goodbye'] is False:
            return
        if channel is not None:
            await channel.send(f'Welcome {member.mention}.')
        else:
            left_guild = member.guild
            send_channel = discord.utils.get(left_guild.channels, name='leavers')
            await send_channel.send(f'Aww, **{member}** has left. :(')

    @commands.command()
    async def goodbye(self, ctx):
        goodbye_enabled = self.bot.my_guilds.goodbye_status(ctx.guild.id)
        goodbye_enabled = not goodbye_enabled
        status_string = '' if goodbye_enabled else 'not '
        await ctx.send(f'I\'m now {status_string}saying goodbye.')
        self.bot.my_guilds.save_greeting(ctx.guild.id, 'goodbye', goodbye_enabled)

    @commands.command()
    async def hello(self, ctx):
        welcome_enabled = self.bot.my_guilds.welcome_status(ctx.guild.id)
        welcome_enabled = not welcome_enabled
        status_string = '' if welcome_enabled else 'not '
        await ctx.send(f'I\'m now {status_string}saying hello.')
        self.bot.my_guilds.save_greeting(ctx.guild.id, 'welcome', welcome_enabled)

    @commands.command()
    async def prefix(self, ctx, arg):
        self.bot.my_guilds.set_prefix(ctx.guild.id, arg)
        await ctx.send(f'Prefix now set to {arg}')


def setup(bot):
    bot.add_cog(Greetings(bot))
