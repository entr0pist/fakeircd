from modules.Module import Module
import lib.utilities as utilities
import re

class Nick(Module):
    def module_load(self):
        self.on_command('nick', self.nick)
        self.register('user_nicked', self.user_nicked)

    def nick(self, user, line):
        connected = user.connected()

        if utilities.validate(line, 2):
            self.trigger('no_nickname', user)
            return

        nick = line[1][:15].lstrip(':')

        if not utilities.nick_re.match(nick):
            self.trigger('bad_nick', user, nick)
            return

        if self.trigger('find_user', nick):
            self.trigger('nick_in_use', user, nick)
            return

        if not user.connected():
            self.trigger('send_ping', user)

        if connected:
            self.trigger('user_nicked', user, nick)

        user.info['nick'] = nick

        if not connected and user.connected():
            self.trigger('user_registered', user)

    def user_nicked(self, user, nick):
        chans = self.trigger('get_all_chans')
        if not chans:
            return

        users = []
        for chan in chans.values():
            if chan.on(user) and user not in users:
                self.trigger('channel_send_to_all_but_one', user, chan, 'NICK', nick)
                users.append(user)

        user.usercmd('NICK', nick)
