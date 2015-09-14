from modules.Module import Module

class Away(Module):
    def module_load(self):
        self.on_command('away', self.away)

    def away(self, user, line):
        if len(line) == 1 or len(line[1]) < 1 or line[1] == ':':
            self.trigger('not_away', user)
        else:
            self.trigger('marked_away', user)
