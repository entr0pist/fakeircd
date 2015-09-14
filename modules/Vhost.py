from modules.Module import Module
import lib.utilities as utilities

class Vhost(Module):
    def module_load(self):
        self.on_command('vhost', self.vhost)
        self.on_command('setuser', self.setuser)

    def vhost(self, user, line):
        if utilities.validate(line, 2):
            self.trigger('not_enough_params', user, 'VHOST')
            return

        if not utilities.host_re.match(line[1]):
            self.trigger('bad_host', user, line[1])
            return

        user.info['hostname'] = line[1][:30]

    def setuser(self, user, line):
        if utilities.validate(line, 2):
            self.trigger('not_enough_params', user, 'SETUSER')
            return

        if not utilities.nick_re.match(line[1]):
            self.trigger('bad_nick', user, line[1])
            return

        user.info['user'] = line[1][:15]
