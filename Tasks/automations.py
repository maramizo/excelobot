# To contain all interval-related tasks, such as role checking, message gathering, etc.
import asyncio
from asyncinit import asyncinit


@asyncinit
class Automations:
    minimum_average_words = 100
    async def __init__(self, bot):
        self.bot = bot
        await self.guild_automations()
        self._loop = asyncio.get_event_loop()
        self._loop.call_later(30, self._loop.create_task, self.guild_automations())

    # Function: guild_automations()
    # Loops over all guilds.
    # Contains the calls to the tasks that are allowed to run.
    async def guild_automations(self):
        for guild_id in self.bot.my_guilds.guilds:
            guild = self.bot.get_guild(guild_id)
            await self.member_automations(guild)
        return

    # Function: member_automations()
    # Loops over all guild members.
    # Calls member-specific tasks.
    async def member_automations(self, guild):
        for member in guild.members:
            # If the guild has an activity role, start the activity role checks.
            if self.bot.my_guilds.get_activity_role(guild.id) is not None:
                role = guild.get_role(self.bot.my_guilds.get_activity_role(guild.id))
                await self.give_activity_role(member, role)
        return

    # Middleman function to ease logic. Member automations calls this per member.
    # This then calls the check average word activity.
    async def give_activity_role(self, member, role):
        await self.check_avg_word_activity(member.guild, member, role)
        return

    # Function: check_avg_word_activity(guild)
    # Checks if user has specific average word count.
    # If they do, it grants the role.
    # If they don't, it removes it.

    async def check_avg_word_activity(self, guild, member, role, after_date=None):
        avg_word_count = self.bot.my_guilds.count_avg_user_words(guild.id, member.id, after_date)
        if avg_word_count > self.minimum_average_words:
            await member.add_roles(role)
            print(
                f"{member} had {avg_word_count} word average per day. Granting them the "
                f"{role} role")
        # else:
        #     print(f"{member} had {avg_word_count} word average per day. They're not getting jack.")
        return
