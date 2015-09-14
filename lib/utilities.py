import re
import collections

nick_re = re.compile(r'^[a-zA-Z\[\]\{\}`_\|\^\\]([a-zA-Z0-9\[\]\{\}`\^\|\\_-]+)?$')
chan_re = re.compile('^[a-zA-Z0-9@!_#$&-]+$')
host_re = re.compile('^[a-zA-Z0-9._-]+$')
ctcp_re = re.compile('^\x01(?!ACTION )', re.I)

def join_msg(msg):
    msg = ' '.join(msg)

    if msg.startswith(':') and len(msg) > 1:
        return msg[1:]
    elif not msg.startswith(':'):
        return msg
    else:
        return ''

def validate(line, length):
    if len(line) < length:
        return True
    for word in line[:length]:
        if not word:
            return True

class CaseInsensitiveDict(collections.MutableMapping):
    def __init__(self, data=None, **kwargs):
        self._store = dict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.lower()][1]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (casedkey for casedkey, mappedvalue in self._store.values())

    def __len__(self):
        return len(self._store)

    def lower_items(self):
        """Like iteritems(), but with all lowercase keys."""
        return (
            (lowerkey, keyval[1])
            for (lowerkey, keyval)
            in self._store.items()
        )

    def __eq__(self, other):
        if isinstance(other, collections.Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return NotImplemented
        return dict(self.lower_items()) == dict(other.lower_items())

    def copy(self):
         return CaseInsensitiveDict(self._store.values())

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, dict(self.items()))


