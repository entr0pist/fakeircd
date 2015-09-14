from lib import config
from lib import linechat

from lib.User import User

class Sockets:
    def __init__(self):
        self.server = linechat.Serve()

    def add_sock(self, sock):
        self.server.add_sock(sock)

    def rm_sock(self, sock):
        self.server.rm_sock(sock)

    def serve(self):
        self.server.serve()

    def spawn_all(self):
        for server in config.get(None, 'listen'):
            if self.server.sock_by_address(server['bind_address'], server['bind_port']):
                continue

            ssl = False
            if 'ssl' in server:
                ssl = server['ssl']

            s = linechat.Server(User, port=server['bind_port'],
                hostname=server['bind_address'], ssl=ssl)
            self.server.add_sock(s)

        for server in self.server.socks:
            try:
                sock = server.sock.getsockname()
            except:
                return

            if not config.get_listen_by_host_port(sock):
                self.server.rm_sock_by_address(*sock)

    def shutdown_all(self):
        self.server.close_all()

sockets = Sockets()
