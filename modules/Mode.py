from modules.Module import Module
import lib.config as config
import lib.utilities as utilities

channel_modes = {
    's': 0, 'o': 1, 'a': 0, 'k': 2
}

class Mode(Module):
    def module_load(self):
        self.on_command('mode', self.mode)
        self.register('channel_mode', self.channel_mode)
        self.register('channel_op?', self.opped)
        self.register('channel_join', self.join_mode)
        self.register('channel_created', self.create_channel)
        self.register_first('channel_privmsg', self.handle_privmsg)
        self.register('channel_post_join', self.post_join)
        self.register('user_nicked', self.track_nick)
        self.register('op_user', self.op_user)
        self.register_first('channel_kick', self.handle_ops)
        self.register_first('setting_topic', self.handle_ops)
        self.register_first('channel_list', self.handle_list)
        self.register('prepend_names', self.prepend_names)
        self.register('mode_string', self.get_modes)

    def mode(self, user, line):
        if utilities.validate(line, 2):
            self.trigger('not_enough_params', user, 'MODE')
            return

        if not utilities.validate(line, 3):
            modes = ' '.join(line[2:])
        else:
            modes = ''

        if line[1].startswith('#'):
            self.trigger('channels_mode', user, line[1][:30], modes)
        else:
            self.trigger('user_modes', user, line[1], '')

    def channel_mode(self, user, channel, modes=None):
        if not modes:
            self.trigger('channel_mode_msg', user, channel.name,
                self.mode_string(chan=channel))
            self.trigger('channel_time_created', user, channel.name, channel.created)
        elif modes in [ 'b', '+b' ]:
            self.trigger('end_channel_ban_list', user, channel.name)
        elif self.opped(channel, user.info['nick']):
            modes = self.parse_modes(channel, modes)
            if modes:
                self.trigger('channel_send_to_all', user, channel,
                    'MODE %s' % channel.name, modes)
        else:
            self.trigger('not_chan_op', user, channel.name)

    def channel_samode(self, channel, mode):
        self.trigger('channel_send_to_all', config.get(None, 'server_name'), channel,
            'MODE %s' % channel.name, mode)

    def do_mode(self, chan, mode, param=None, add=False):
        changed = False

        if mode not in chan.modes:
            if mode in channel_modes and channel_modes[mode]:
                if channel_modes[mode] == 2:
                    chan.modes[mode] = ""
                else:
                    chan.modes[mode] = []
            else:
                chan.modes[mode] = add
                changed = add

        if not add and channel_modes[mode] == 1 and param and param in chan.modes[mode]:
            chan.modes[mode].remove(param)
            changed = True
        elif add and channel_modes[mode] == 1 and param and param not in chan.modes[mode]:
            chan.modes[mode].append(param)
            changed = True
        elif add and channel_modes[mode] == 2 and param and param != chan.modes[mode]:
            chan.modes[mode] = param
            changed = True
        elif add and not chan.modes[mode] and not param and not channel_modes[mode]:
            chan.modes[mode] = True
            changed = True
        elif not add and chan.modes[mode] and not param and channel_modes[mode] != 1:
            chan.modes[mode] = False
            changed = True

        return changed

    def parse_modes(self, chan, mode_string):
        _modes  = []
        params = []

        args = mode_string.split()
        if len(args) < 1:
            return

        add = '+'
        for char in args[0]:
            if char == '+' or char == '-':
                add = char
            else:
                _modes.append(add + char)

        if len(args) > 1:
            params = [ arg.lower() for arg in args[1:] ]

        added, removed, _params = "", "", []
        for mode in _modes:
            do = False
            add  = mode[0] == '+'
            mode = mode[1]

            if mode not in channel_modes:
                continue

            if ((channel_modes[mode] == 1) or
                    (channel_modes[mode] == 2 and add)) and params:
                param = params.pop(0)
                do = True
            elif channel_modes[mode] == 2 and not add:
                param = ''
                do = True
            elif mode in channel_modes and not channel_modes[mode]:
                param = ''
                do = True

            if do and self.do_mode(chan, mode, param=param, add=add):
                if add:
                    added += mode
                else:
                    removed += mode
                if param:
                    _params.append(param)

        return self.mode_string(added, removed, _params, True)

    def get_modes(self, chan):
        return self.mode_string(chan=chan)

    def mode_string(self, added=None, removed=None, params=None, changed=False, chan=False):
        mode_string = ""
        if changed:
            if added:
                mode_string += "+" + added + " "
            if removed:
                mode_string  = mode_string.rstrip(' ')
                mode_string += "-" + removed + " "
            if params:
                mode_string += ' '.join(params)
        else:
            modes, params = "", []
            for mode, param in chan.modes.iteritems():
                if not param:
                    continue

                if isinstance(param, list):
                    continue
                    modes  += mode * len(param)
                    params += param
                elif isinstance(param, unicode) or isinstance(param, str):
                    modes += mode
                    params.append(param)
                else:
                    modes += mode
            mode_string = "%s %s" % (modes, ' '.join(params))
        return mode_string.rstrip()

    def get_mode(self, chan, mode):
        if mode in chan.modes:
            return chan.modes[mode]
        else:
            return None

    def opped(self, chan, nick):
        if hasattr(nick, 'info'):
            nick = nick.info['nick']
        return 'o' in chan.modes and nick.lower() in chan.modes['o']

    def join_mode(self, user, chan):
        if self.get_mode(chan, 'a'):
            return

        if len(chan.users) > 1:
            self.parse_modes(chan, '-o ' + user.info['nick'])
        elif len(chan.users) == 1:
            self.channel_samode(chan, '+o ' + user.info['nick'])

    def post_join(self, user, chan):
        if self.get_mode(chan, 'a'):
            self.trigger('op_user', user, chan)
            self.channel_samode(chan, '+o ' + user.info['nick'])

    def create_channel(self, user, chan):
        if not self.get_mode(chan, 'a'):
            self.op_user(user, chan)

    def op_user(self, user, chan):
        self.parse_modes(chan, '+o ' + user.info['nick'])

    def handle_ops(self, user, chan, arg, arg2=None):
        if not self.opped(chan, user):
            self.trigger('not_chan_op', user, chan.name)
            return True

    def handle_privmsg(self, user, chan, msg):
        prefix        = self.get_mode(chan, 'k')
        action_prefix = '\x01action %s' % prefix
        check         = msg.lower().startswith
        if prefix and not check(prefix) and not check(action_prefix):
            self.trigger('msg_blocked', user, chan.name, 'not matching prefix')
            return True

    def handle_list(self, user, chan):
        if self.get_mode(chan, 's'):
            return True

    def prepend_names(self, user, chan):
        if self.opped(chan, user):
            return '@'

    def track_nick(self, user, nick):
        chans = self.trigger('get_all_chans')
        if not chans:
            return

        for name, chan in chans.iteritems():
            if self.opped(chan, user):
                self.parse_modes(chan, '-o ' + user.info['nick'])
                self.parse_modes(chan, '+o ' + nick)
            elif self.opped(chan, nick):
                self.parse_modes(chan, '-o ' + nick)
