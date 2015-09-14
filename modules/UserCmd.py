from modules.Module import Module
import lib.utilities as utilities
import lib.config as config

class UserCmd(Module):
    def module_load(self):
        self.on_command('user', self.user)

    def user(self, user, line):
        connected = user.connected()
        if connected:
            return

        if utilities.validate(line, 5):
            self.trigger('not_enough_params', user, 'USER')
            return

        if not utilities.nick_re.match(line[1]):
            self.trigger('not_enough_params', user, 'USER')
            return

        user.info['user']     = line[1][:15]
        user.info['realname'] = utilities.join_msg(line[4:])[:30]

        if config.get(user, 'spoof_user'):
            user.info['user'] = config.get(user, 'spoof_user')
        if config.get(user, 'spoof_real'):
            user.info['realname'] = config.get(user, 'spoof_real')
        if config.get(user, 'spoof_address'):
            user.info['hostname'] = config.get(user, 'spoof_address')

        if user.connected():
            self.events.trigger('user_registered', user)

