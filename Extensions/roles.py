# TODO role granting.
#  Set minimum amount of words through command.
#  Check if bot has permissions immediately and send an error.
import discord
from discord.ext import commands
from discord.utils import get


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Only admins are allowed to use commands within this cog.
    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator and self.bot.guild_permissions.manage_roles

    @commands.command()
    async def msgtotal(self, ctx):
        count = self.bot.my_guilds.count_total_user_messages(ctx.guild.id, ctx.author.id)
        return await ctx.send(f'Your total count of messages in this server for the past week is {count}.')

    @commands.command()
    async def wordstotal(self, ctx):
        count = self.bot.my_guilds.count_total_user_words(ctx.guild.id, ctx.author.id)
        return await ctx.send(f'Your total count of words in this server for the past week is {count}.')

    @commands.bot_has_permissions(manage_roles=True)
    @commands.command()
    async def setrole(self, ctx, role: discord.Role):
        self.bot.my_guilds.set_activity_role(ctx.guild.id, role)
        return await ctx.send(f'You have set the activity role to {role.name}.')

    @commands.command()
    async def getrole(self, ctx):
        role_id = self.bot.my_guilds.get_activity_role(ctx.guild.id)
        if role_id is not None:
            role = get(ctx.guild.roles, id=role_id)
            return await ctx.send(f'Current activity role is {role.name}.')
        return await ctx.send(f'No activity role currently set.')

    async def setwords(self, ctx, words: int):
        self.bot.my_guilds.set_avg_words_for_activity_role(ctx.guild.id, words)
        await ctx.send(f'You have set the average words per day for the activity role to be {words}')
        if self.bot.my_guilds.get_activity_role(ctx.guild.id) is None:
            await ctx.send(f'You have not yet set the activity role, please set it using {ctx.prefix}setrole role')


def setup(bot):
    bot.add_cog(Roles(bot))
