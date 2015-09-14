from modules.Module import Module
import lib.utilities as utilities

class Join(Module):
    def module_load(self):
        self.on_command('join', self.join)
        self.register('channel_join', self.channel_join)

    def join(self, user, line):
        if utilities.validate(line, 2):
            self.trigger('not_enough_params', user, 'JOIN')
            return

        chans = line[1].split(',')
        for chan in chans:
            if not chan.startswith('#'):
                chan = '#' + chan
            chan = chan[:30]
            if utilities.chan_re.match(chan):
                self.trigger('channels_join', user, chan)

    def channel_join(self, user, chan):
        chan.users.append(user)
        self.trigger('channel_send_to_all', user, chan, 'JOIN', chan.name)
        self.trigger('send_topic', user, chan, True)
        self.trigger('channel_names', user, chan)
        self.trigger('channel_post_join', user, chan)
