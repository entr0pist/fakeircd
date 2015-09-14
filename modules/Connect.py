from modules.Module import Module
import lib.config as config

class Connect(Module):
    def module_load(self):
        self.register('initial_connect', self.initial_connect)
        self.register('user_registered', self.user_registered)

    def initial_connect(self, user):
        user.srv_notice('AUTH :*** Looking up your hostname...')
        user.srv_notice("AUTH :*** Couldn't resolve your hostname; using your IP address instead")

    def user_registered(self, user):
        if config.get(user, 'user'):
            self.trigger('send_to_opers', '%s connecting as %s' %
                (config.get(user, 'user'), user.info['nick']))
        else:
            self.trigger('send_to_opers', '%s connecting on port %d' %
                (user.info['nick'], user.saddr[1]))

        self.trigger('welcome', user)
        self.trigger('welcome_version', user)
        self.trigger('isupport', user)

        self.run_command('lusers', user, [])
        self.run_command('motd', user, [])
