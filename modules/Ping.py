from modules.Module import Module
import lib.utilities as utilities
import lib.config as config
import random

class Ping(Module):
    def module_load(self):
        self.on_command('ping', self.ping)
        self.on_command('pong', self.pong)
        self.register('send_ping', self.send_ping)

        self.pinged = {}

        self.trigger_avail('timer', self.ping_all, config.get(None, 'ping_freq'))

    def send_ping(self, user):
        self.pinged[user] = '%08X' % random.randint(268435456, 4294967295)
        user.send('PING :%s' % self.pinged[user])

    def ping(self, user, line):
        if len(line) > 1 and line[1]:
            msg = line[1]
        else:
            msg = ''

        srv = config.get(user, 'server_name')
        user.send(':%s PONG %s :%s' % (srv, srv, msg))

    def pong(self, user, line):
        if user in self.pinged and len(line) == 2 and line[1].lstrip(':') == self.pinged[user]:
            self.pinged[user] = 0
        else:
            self.send_ping(user)

    def ping_all(self, timer):
        to_remove = []

        for user in self.trigger('get_all_users') or []:
            if user in self.pinged and self.pinged[user]:
                to_remove.append(user)
            else:
                self.trigger('send_ping', user)

        for user in to_remove:
            del self.pinged[user]
            user.send('ERROR :Closing Link: [%s] (Ping timeout: DDoSed)' %
                user.info['hostname'])
            self.trigger('user_quit', user, 'Ping Timeout: DDoSed')
