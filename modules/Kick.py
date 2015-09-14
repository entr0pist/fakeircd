from modules.Module import Module
import lib.utilities as utilities

class Kick(Module):
    def module_load(self):
        self.on_command('kick', self.kick)
        self.register('channel_kick', self.channel_kick)

    def kick(self, user, line):
        if utilities.validate(line, 3):
            self.trigger('not_enough_params', user, 'KICK')
            return

        if not utilities.validate(line, 4):
            message = utilities.join_msg(line[3:])
        else:
            message = 'kicked'

        if not line[1].startswith('#'):
            chan = '#' + line[1]
        else:
            chan = line[1]

        chan = chan[:30]
        if not utilities.chan_re.match(chan):
            return

        self.trigger('channels_kick', user, chan, line[2][:15], message)

    def channel_kick(self, user, chan, nick, message):
        kicked = False
        for u in chan.users:
            if u.info['nick'] == nick:
                kicked = u

        if not kicked:
            return

        self.trigger('channel_send_to_all', user, chan,
            'KICK %s %s' % (chan.name, nick), message)
        chan.users.remove(kicked)
        self.trigger('post_channel_kick', user, chan, kicked)

