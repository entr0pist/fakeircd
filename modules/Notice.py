from modules.Module import Module
import lib.utilities as utilities

class Notice(Module):
    def module_load(self):
        self.on_command('notice', self.notice)
        self.register('user_notice', self.user_notice)

    def notice(self, user, line):
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
            pass
        else:
            self.trigger('user_notice', user, line[1][:15], message)

    def user_notice(self, user, nick, msg):
        u = self.trigger('find_user', nick)
        if u:
            self.trigger('send_to_one', u, ':%s NOTICE %s :%s' %
                (user.umask(), u.info['nick'], msg))
        else:
            self.trigger('no_such_nick', user, nick)
