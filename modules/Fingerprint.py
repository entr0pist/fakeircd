from modules.Module import Module
from lib.structs import Struct
import struct
import hashlib
import json
import os

class SSLVersion(Struct):
    align = '>'
    data  = [
        [ 'major', 'B' ],
        [ 'minor', 'B' ]
    ]

    def __repr__(self):
        if self.minor < 0 or self.minor > 3 or self.major != 3:
            return 'UNKNOWN'

        return [ 'SSLv3', 'TLSv1.0', 'TLSv1.1', 'TLSv1.2' ][self.minor]

class SSLMessage(Struct):
    align = '>'
    data  = [
        [ 'type', 'B' ],
        [ 'version', 'H' ],
        [ 'length', 'H' ]
    ]

class Handshake(Struct):
    align = '>'
    data = [
        [ 'ssl_header', SSLMessage ],
        [ 'type', 'B' ],
        [ 'length', '3s' ],
        [ 'version', SSLVersion ],
        [ 'time', 'I' ],
        [ 'random_bytes', '28s' ],
        [ 'session_id', 'B' ],
        [ 'len_ciphers', 'H' ]
    ]

class Extension(Struct):
    align = '>'
    data  = [
        [ 'type', 'H' ],
        [ 'length', 'H' ]
    ]

class ParseHandshake:
    def __init__(self, hello):
        self.hello   = hello
        self.ciphers = []
        self.extens  = []
        self.comps   = []

        if len(hello[:46]) != 46:
            return

        shake = Handshake(hello[:46], unpack=True)
        hello = hello[46:]

        self.shake = shake
        version    = ('%04x' % self.shake.ssl_header.version).decode('hex')

        self.shake.ssl_header.version = SSLVersion(version, unpack=True)

        #if shake.ssl_header.version != 0x0301:
        #    return

        if len(hello) < shake.len_ciphers:
            return

        self.ciphers = struct.unpack('>' + 'H' * (shake.len_ciphers / 2),
            hello[:shake.len_ciphers])
        hello = hello[shake.len_ciphers:]

        if len(hello) < 1:
            return

        len_comps = struct.unpack('>B', hello[:1])[0]
        hello     = hello[1:]

        if len(hello) < len_comps:
            return

        self.comps = struct.unpack('>' + 'B' * len_comps, hello[:len_comps])
        hello = hello[len_comps:]

        if len(hello) < 2:
            return

        len_extens = struct.unpack('>H', hello[:2])[0]
        hello  = hello[2:]

        if len_extens != len(hello):
            return

        while len_extens:
            ext   = Extension(hello[:4], unpack = True)
            hello = hello[4:]

            ext.ext_data = hello[:ext.length]
            hello        = hello[ext.length:]

            self.extens.append(ext)
            len_extens -= 4 + ext.length


    def gen_fingerprint(self):
        fingerprint = ''

        if hasattr(self, 'shake'):
            fingerprint += str(self.shake.ssl_header.version.major)
            fingerprint += str(self.shake.ssl_header.version.minor)

        if hasattr(self, 'ciphers'):
            fingerprint += str(self.ciphers)

        if hasattr(self, 'comps'):
            fingerprint += str(self.comps)

        if hasattr(self, 'extens'):
            fingerprint += str(self.extens)

        return hashlib.md5(fingerprint).hexdigest()

    def p(self):
        print('---- New Client ----')

        print('Fingerprint: %s' % self.gen_fingerprint())

        print('Version: %s' % self.shake.ssl_header.version)
        print('Version: %s' % self.shake.version)
        print('Time: 0x%08x' % self.shake.time)
        print('Session ID: 0x%02x' % self.shake.session_id)

        print('Cipher suites: (' + hashlib.md5(str(self.ciphers)).hexdigest() + ')')
        print([ hex(cipher) for cipher in self.ciphers ])

        print('Compression methods: (' + hashlib.md5(str(self.comps)).hexdigest() + ')')
        print([ hex(comp) for comp in self.comps ])

        print('Extensions: (' + hashlib.md5(str(self.extens)).hexdigest() + ')')
        print([ hex(exten.type) for exten in self.extens ])

        print('')

class Fingerprint(Module):
    def module_load(self):
        self.register('ssl_client_hello', self.ssl)
        self.register('user_nicked', self.nicked)
        self.register('user_registered', self.nicked)

    def ssl(self, user, hello):
        if hasattr(user, 'ssl_info'):
            return

        user.ssl_info = ParseHandshake(hello)
        # user.ssl_info.p()

    def nicked(self, user, nick=None):
        if not hasattr(user, 'ssl_info'):
            return

        fingerprint = user.ssl_info.gen_fingerprint()

        if not nick:
            self.trigger('send_to_opers', '%s is %s' % (user.info['nick'], fingerprint))

        if os.path.exists('data/fingerprints.json'):
            fingerprints = json.load(open('data/fingerprints.json'))
        else:
            fingerprints = {}

        if not nick:
            nick = user.info['nick']

        if fingerprint in fingerprints:
            if nick not in fingerprints[fingerprint]:
                fingerprints[fingerprint].append(nick)
        else:
            fingerprints[fingerprint] = [ nick ]

        json.dump(fingerprints, open('data/fingerprints.json', 'w'))
