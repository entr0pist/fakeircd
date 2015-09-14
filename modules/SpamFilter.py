from modules.Module import Module

banned = [ 'ayy', 'dafuq' ]
kill_msg = 'Wash your mouth out with soap.'

class SpamFilter(Module):
    def module_load(self):
        self.register_first('channel_privmsg', self.kill)
        self.register_first('user_privmsg', self.kill)

    def kill(self, user, target, msg):
        for ban in banned:
            if ban in msg.lower():
                user.send('ERROR :Closing Link: [%s] (Killed: %s)' %
                    (user.info['hostname'], kill_msg))
                self.trigger('user_quit', user, 'Killed: %s' % kill_msg)

                return True
