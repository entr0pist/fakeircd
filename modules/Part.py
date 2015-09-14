from modules.Module import Module
import lib.utilities as utilities

class Part(Module):
    def module_load(self):
        self.on_command('part', self.part)
        self.register('channel_part', self.channel_part)

    def part(self, user, line):
        if utilities.validate(line, 2):
            self.trigger('not_enough_params', user, 'PART')
            return

        if len(line) > 2 and line[2]:
            message = utilities.join_msg(line[2:])
        else:
            message = ''

        chans = line[1].split(',')
        for chan in chans:
            if not chan.startswith('#'):
                chan = '#' + chan
            chan = chan[:30]
            if utilities.chan_re.match(chan):
                self.trigger('channels_part', user, chan, message)

    def channel_part(self, user, chan, msg):
        self.trigger('channel_send_to_all', user, chan, 'PART %s' % chan.name, msg)
        chan.users.remove(user)
        self.trigger('post_channel_part', user, chan)
