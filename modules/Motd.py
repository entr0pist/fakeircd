from modules.Module import Module
import lib.config as config

class Motd(Module):
    def module_load(self):
        self.on_command('motd', self.motd)

    def motd(self, user, line):
        self.trigger('motd_start', user)
        self.trigger('motd_text', user, open(config.get(user, 'motd')).readlines())
        self.trigger('motd_end', user)
