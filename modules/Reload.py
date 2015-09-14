from modules.Module import Module
from lib.module_driver import modules
from lib.Sockets import sockets
from lib.events import events

import lib.config as config
import signal

class Reload(Module):
    def module_load(self):
        self.on_command('reload', self.reload_command)
        self.register('reload', self.reload)
        signal.signal(signal.SIGHUP, self.reload)

    def reload_command(self, user, line):
        if not config.get(user, 'oper'):
            return

        user.srv_notice('%s : [*] Reloading config.' % user.info['nick'])
        self.reload()

    def reload(self, signum=None, frame=None):
        config.load_config()
        sockets.spawn_all()
        events.unregister_all()
        modules.load_all()
