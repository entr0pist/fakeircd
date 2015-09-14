import socket
import select
import re
import ssl
import sys

class Serve:
    def __init__(self):
        self.socks = []

    def add_sock(self, sock):
        self.socks.append(sock)

    def rm_sock(self, sock):
        if sock in self.socks:
            self.socks.remove(sock)

    def sock_by_address(self, hostname, port):
        socks = []

        for sock in self.socks:
            try:
                if not sock.closed and sock.sock.getsockname() == (hostname, port):
                    socks.append(sock)
            except:
                pass

        return socks

    def rm_sock_by_address(self, hostname, port):
        for sock in self.sock_by_address(hostname, port):
            sock.close()

    def serve(self):
        while self.socks:
            try:
                self.select()
            except KeyboardInterrupt:
                self.close_all()
                sys.exit()

    def select(self):
        try:
            r, w, x = select.select(self.socks, [], [])
        except socket.error as e:
            for sock in self.socks:
                if sock.closed:
                    self.rm_sock(sock)
            return
        except select.error:
            return

        for sock in x:
            self.rm_sock(sock)

        for sock in r:
            if isinstance(sock, Server):
                csock = sock.accept()
                if csock:
                   self.add_sock(csock)
            else:
                if sock.read():
                    self.rm_sock(sock)

                    try:
                        sock.close()
                    except socket.error:
                        pass

    def close_all(self):
        for sock in self.socks:
            if isinstance(sock, LineClient):
                sock.close()
        for sock in self.socks:
            if isinstance(sock, Server):
                sock.close()

class Server:
    def __init__(self, client_class, hostname='127.0.0.1', port=6669, ssl=False):
        self.closed = False
        self.ssl    = ssl
        self.sock   = socket.socket()
        self.sock.bind((hostname, port))
        self.sock.listen(5)

        print("[*] Listening on: %s:%d" % self.sock.getsockname())
        self.client_class = client_class

    def accept(self):
        try:
            csock, addr = self.sock.accept()
        except socket.error:
            return

        csock.setblocking(0)

        if self.ssl:
            try:
                csock = ssl.wrap_socket(csock, server_side=True, certfile="ircd.pem",
                    keyfile="ircd.pem", do_handshake_on_connect=False)
            except:
                csock.close()
                return

        return self.client_class(csock, self.sock.getsockname(), ssl=self.ssl)

    def close(self):
        self.closed = True
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def fileno(self):
        return self.sock.fileno()

class LineClient:
    def __init__(self, sock, saddr, ssl=False):
        self.closed = False
        self.saddr  = saddr
        self.sock   = sock
        self.buffer = ''
        self.ssl    = ssl

        if self.ssl:
            self.handshook = False
        else:
            self.call('handle_connect')

    def read(self):
        if self.ssl and not self.handshook:
            try:
                self.call('client_hello', self.sock._sock.recv(65535, socket.MSG_PEEK))
                self.sock.do_handshake()
                self.handshook = True
                self.call('handle_connect')
            except ssl.SSLError as err:
                if err.args[0] == ssl.SSL_ERROR_WANT_READ:
                    pass
                else:
                    return True
            except socket.error:
                return True

            return

        try:
            data = self.sock.recv(65535).decode('utf-8', 'ignore')
        except socket.error:
            data = None

        if not data:
            self.call('handle_close')
            return True

        self.buffer += data
        lines = re.split('[\r\n]+', self.buffer)

        self.buffer = lines[-1]
        for line in lines[:-1]:
            if self.handle_line(line):
                return True

    def close(self):
        self.closed = True
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def fileno(self):
        return self.sock.fileno()

    def call(self, func, *args, **kwargs):
        if hasattr(self, func):
            getattr(self, func)(*args, **kwargs)

    def send(self, message):
        try:
            return self.sock.send(message[:510].encode('utf-8') + '\r\n')
        except socket.error:
            pass


