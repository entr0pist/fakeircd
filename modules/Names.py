from modules.Module import Module
import lib.utilities as utilities

class Names(Module):
    def module_load(self):
        self.on_command('names', self.names)
        self.register('channel_names', self.channel_names)

    def names(self, user, line):
        if utilities.validate(line, 2):
            self.trigger('not_enough_params', user, 'NAMES')
            return

        if not line[1].startswith('#'):
            line[1] = '#' + line[1]

        chan = line[1][:30]
        self.trigger('channels_names', user, chan)

    def channel_names(self, user, chan):
        users = []
        for u in chan.users:
            nick = (self.trigger('prepend_names', u, chan) or '') + u.info['nick']
            users.append(nick)

        self.trigger('names_list', user, chan.name, users)
        self.trigger('end_names', user, chan.name)
