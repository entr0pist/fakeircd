from modules.Module import Module

class NoPOST(Module):
    def module_load(self):
        self.on_command('post', self.nopost)
        self.on_command('get', self.nopost)
        self.on_command('put', self.nopost)
        self.on_command('trace', self.nopost)
        self.on_command('delete', self.nopost)
        self.on_command('patch', self.nopost)

    def nopost(self, user, line):
        user.send('ERROR :Closing Link: [%s] (HTTP method detected)' %
            user.info['hostname'])
        self.trigger('user_quit', user, 'HTTP method detected')
