from modules.Module import Module
import lib.utilities as utilities

class PrivMsg(Module):
    def module_load(self):
        self.on_command('privmsg', self.privmsg)
        self.register('channel_privmsg', self.channel_privmsg)
        self.register('user_privmsg', self.user_privmsg)

    def privmsg(self, user, line):
        if utilities.validate(line, 2):
            self.trigger('no_recip', user)
            return

        if utilities.validate(line, 3):
            self.trigger('no_text', user)
            return

        message = utilities.join_msg(line[2:])
        if utilities.ctcp_re.match(message):
            self.trigger('attempted_ctcp', user)
            return

        if line[1].startswith('#'):
            self.trigger('channels_privmsg', user, line[1][:30], message)
        else:
            self.trigger('user_privmsg', user, line[1][:15], message)

    def channel_privmsg(self, user, chan, msg):
        self.trigger('channel_send_to_all_but_one', user, chan,
            'PRIVMSG %s' % chan.name, msg)

    def user_privmsg(self, user, nick, msg):
        u = self.trigger('find_user', nick)
        if u:
            self.trigger('send_to_one', u, ':%s PRIVMSG %s :%s' %
                (user.umask(), u.info['nick'], msg))
        else:
            self.trigger('no_such_nick', user, nick)
