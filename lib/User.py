#!/usr/bin/python2
import re

from lib import config

from lib.events   import events
from lib.linechat import LineClient

class User(LineClient):
    def handle_connect(self):
        self.info = {
            'nick'     : '*',
            'user'     : '',
            'realname' : '',
            'hostname' : self.sock.getsockname()[0]
        }
        events.trigger('initial_connect', self)

    def handle_line(self, line):
        line = line[:512]

        line = line.split(' ')
        if not line:
            return

        if events.trigger('allowed_command', self, line):
            return

        events.trigger('command_' + line[0].lower(), self, line)

    def handle_close(self):
        events.trigger('closed_connection', self)
        pass

    def client_hello(self, hello):
        events.trigger('ssl_client_hello', self, hello)

    def numeric(self, num, message):
        self.send(':%s %03d %s %s' % (config.get(self, 'server_name'), num,
            self.info['nick'], message))

    def srv_notice(self, message):
        self.send(':%s NOTICE %s' % (config.get(self, 'server_name'), message))

    def usercmd(self, cmd, msg):
        self.send(':%s %s :%s' % (self.umask(), cmd, msg))

    def umask(self):
        return '%s!%s@%s' % (self.info['nick'], self.info['user'], self.info['hostname'])

    def connected(self):
        return self.info['nick'] != '*' and self.info['user'] != ''
