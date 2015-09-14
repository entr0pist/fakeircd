#!/usr/bin/python
from modules.Module import Module

import lib.utilities as utilities
import lib.config as config
import socket
import urllib
import threading

TORRC_PREFIX = config.get(None, 'torrc_prefix')

def make_request(*args):
    args = '/'.join([ str(arg) for arg in args ])
    auth = 'user:password'
    onion = '127.0.0.1:5000'
    url  = 'http://%s@%s/onion/%s' % (auth, onion, args)

    while 1:
        try:
            output = urllib.urlopen(url).read()
            break
        except Exception as e:
            print("[!] Request failed: %s, retrying." % e)

    if len(output) > 1:
        return output
    if output == '1':
        return True
    else:
        return False

def get_block(where):
    for listen in config.get(None, 'listen'):
        match = True
        for key in where:
            if key not in listen or listen[key] != where[key]:
                match = False
                break
        if match:
            return listen

def find_sock(in_use=[]):
    port = 0
    s = socket.socket()
    while not port or port in in_use:
        s.bind(("127.0.0.1", 0))
        _, port = s.getsockname()
        s.close()
    return port

class GetUser:
    def __init__(self, user):
        self.user   = user
        self.exists = get_block({ 'user' : user })

    def ports(self):
        maps = eval(make_request(TORRC_PREFIX + self.user, 'maps'))
        return maps[0][-1], maps[1][-1]

    def onion(self):
        if hasattr(self, '_onion') and self._onion:
            return self._onion
        else:
            return make_request(TORRC_PREFIX + self.user)

    def create(self):
        if self.exists: return
        standard_port = find_sock()
        ssl_port      = find_sock([standard_port])

        make_request(TORRC_PREFIX + self.user, 'create')
        make_request(TORRC_PREFIX + self.user, 'map',
            6667, config.get(None, 'default_address'), standard_port)
        make_request(TORRC_PREFIX + self.user, 'map', 6697,
            config.get(None, 'default_address'), ssl_port)

        config.get(None, 'listen').append({
            'bind_address': config.get(None, 'default_address'),
            'bind_port': standard_port,
            'user': self.user
        })

        config.get(None, 'listen').append({
            'bind_address': config.get(None, 'default_address'),
            'bind_port': ssl_port,
            'user': self.user,
            'ssl': 1
        })

        config.write_config()
        return [ (config.get(None, 'default_address'), standard_port, 0),
            (config.get(None, 'default_address'), ssl_port, 1) ]

    def banish(self):
        if not self.exists: return
        make_request(TORRC_PREFIX + self.user, 'delete')

        ports = []

        block = get_block({
            'user': self.user
        })
        ports.append((block['bind_address'], block['bind_port']))
        config.get(None, 'listen').remove(block)

        block = get_block({
            'user': self.user,
            'ssl': 1
        })
        ports.append((block['bind_address'], block['bind_port']))
        config.get(None, 'listen').remove(block)

        config.write_config()
        return ports

    def new_onion(self):
        if not self.exists: return
        self.banish()
        self.create()

class Onions(Module):
    def module_load(self):
        self.on_command('banish', self.banish)
        self.on_command('spawn', self.spawn)

    def banish(self, user, line):
        if not config.get(user, 'oper') or utilities.validate(line, 2):
            return

        def _banish():
            user.srv_notice('%s : [*] Banishing %s!' % (user.info['nick'], line[1]))
            u = GetUser(line[1])
            if u.exists:
                for port in u.banish():
                    self.trigger('close_server_sock', port[0], port[1])
                user.srv_notice('%s : - Banished %s!' % (user.info['nick'], line[1]))
            else:
                user.srv_notice('%s : - User %s does not exist!' %
                    (user.info['nick'], line[1]))
            self.thread = None

        if hasattr(self, 'thread') and self.thread:
            user.srv_notice('%s : [!] Spawn or banish already in progress.' %
                user.info['nick'])
        else:
            user.thread = threading.Thread(target=_banish)
            user.thread.start()

    def spawn(self, user, line):
        if not config.get(user, 'oper') or utilities.validate(line, 2):
            return

        def _spawn():
            user.srv_notice('%s : [*] Spawning onion for %s' %
                (user.info['nick'], line[1]))

            u = GetUser(line[1])
            if not u.exists:
                u.create()
                user.srv_notice('%s : - Added user %s onion: %s' % (user.info['nick'],
                    line[1], u.onion()))
            else:
                user.srv_notice('%s : - User %s already exists!' % (user.info['nick'],
                    line[1]))
            self.thread = None

        if hasattr(self, 'thread') and self.thread:
            user.srv_notice('%s : [!] Spawn or banish already in progress.' %
                user.info['nick'])
        else:
            self.thread = threading.Thread(target=_spawn)
            self.thread.start()
