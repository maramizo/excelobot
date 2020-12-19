# Guild class.
# Contains all meta-information related to guilds.
# To be shared across all other modules.


class Guild:
    def __init__(self, guild_id, database):
        self.id = guild_id
        self.DB = database
        self.load_prefix()

        if self.pre is None:
            self.pre = '.'

    def set_prefix(self, prefix):
        self.pre = prefix
        self.DB.set_setting(self.id, 'prefix', prefix)

    def prefix(self):
        return self.pre

    def load_prefix(self):
        self.pre = self.DB.get_setting(self.id, 'prefix')
        return
