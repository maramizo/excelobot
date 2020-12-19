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
    async def activityrole(self, ctx):
        self.bot.my_guilds.load_messages(ctx.guild.id)


def setup(bot):
    bot.add_cog(Roles(bot))
