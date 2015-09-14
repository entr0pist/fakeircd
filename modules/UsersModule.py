from modules.Module import Module
from lib.globals import users
import lib.config as config

class UsersModule(Module):
    def module_load(self):
        self.register('initial_connect', self.initial_connect)
        self.register('user_quit', self.user_quit)
        self.register('close_server_sock', self.close_server_socket)
        self.register('find_user', self.find_user)
        self.register('send_to_one', self.send_to_one)
        self.register('send_to_opers', self.send_to_opers)
        self.register('get_all_users', self.get_all_users)
        self.register('num_users', self.num_users)

    def initial_connect(self, user):
        users.append(user)
        self.trigger('timer', self.check_reg, 60, repeat=False, args=(user, ))

    def check_reg(self, timer, user):
        if not user.connected() and user in users:
            user.send('ERROR :Closing Link: [%s] (Registration timeout.)' %
                user.info['hostname'])
            self.trigger('user_quit', user, 'Registration timeout.')

    def user_quit(self, user, message):
        try:
            user.close()
        except Exception as e:
            pass

        if user in users:
            users.remove(user)

    def close_server_socket(self, hostname, port):
        to_remove = []

        for user in users:
            if user.saddr == (hostname, port):
                to_remove.append(user)

        for user in to_remove:
            self.trigger('user_quit', user, 'Banished')

    def find_user(self, nick):
        for user in users:
            if user.info['nick'].lower() == nick.lower():
                return user

    def send_to_one(self, user, msg):
        user.send(msg)

    def send_to_opers(self, message):
        for user in users:
            if config.get(user, 'oper'):
                user.srv_notice('%s : - %s' % (user.info['nick'], message))

    def get_all_users(self):
        return users

    def num_users(self):
        return len(users)
