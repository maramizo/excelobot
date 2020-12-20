# TODO role granting.
#  Allow administrators to make a command that grants users a role based on amounts of words typed.
#  This is to be accessed using bot.my_guilds.grant_role('user_id', 'guild_id', 'role_id', 'word_count')
#  or some similar structure.
from discord.ext import commands


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Only admins are allowed to use commands within this cog.
    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    @commands.command()
    async def msgtotal(self, ctx):
        count = self.bot.my_guilds.count_total_user_messages(ctx.guild.id, ctx.author.id)
        return await ctx.send(f'Your total count of messages in this server for the past week is {count}.')

    @commands.command()
    async def wordstotal(self, ctx):
        count = self.bot.my_guilds.count_total_user_words(ctx.guild.id, ctx.author.id)
        return await ctx.send(f'Your total count of words in this server for the past week is {count}.')


def setup(bot):
    bot.add_cog(Roles(bot))
