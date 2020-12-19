# Guild class.
# Contains all meta-information related to guilds.
# To be shared across all other modules. TODO figure out dependency injection or a way to share this.


class Guild:
    def __init__(self, guild_id, database):
        self.id = guild_id
        self.DB = database
        self.pre = self.DB.get_setting(self.id, 'prefix')

        if self.pre is None:
            self.pre = '.'

    def set_prefix(self, prefix):
        self.pre = prefix
        self.DB.set_setting(self.id, 'prefix', prefix)

    def prefix(self):
        return self.pre

    def load_prefix(self):
        return
