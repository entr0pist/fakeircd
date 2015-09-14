from modules.Module import Module
import lib.utilities as utilities

class Quit(Module):
    def module_load(self):
        self.on_command('quit', self.quit)
        self.register('user_quit', self.channel_quit)

    def quit(self, user, line):
        if len(line) > 1 and line[1]:
            msg = utilities.join_msg(line[1:])
        else:
            msg = 'quit'

        self.trigger('user_quit', user, 'Quit: ' + msg)
        return True

    def channel_quit(self, user, message):
        self.trigger('send_to_all_shared', user, 'QUIT', message)

        chans = self.trigger('get_all_chans')
        if not chans:
            return

        for chan in chans.values():
            if chan.on(user):
                chan.users.remove(user)

