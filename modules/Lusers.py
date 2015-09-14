from modules.Module import Module

class Lusers(Module):
    def module_load(self):
        self.on_command('lusers', self.lusers)

    def lusers(self, user, line):
        self.trigger('lusers_channels', user)
        self.trigger('lusers_users', user)
