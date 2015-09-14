
class Events(object):
    def __init__(self):
        self.events  = {}
        self.pending = {}

    def register(self, event, function, append=True):
        if event not in self.events:
            self.events[event] = []

        # print('[*] Registering event: ' + event)

        if function not in self.events[event]:
            if append:
                self.events[event].append(function)
            else:
                self.events[event] = [ function ] + self.events[event]

        if event in self.pending:
            for pending in self.pending[event]:
                self.trigger(event, *pending[0], **pending[1])
            del self.pending[event]

    def register_first(self, event, function):
        self.register(event, function, False)

    def unregister(self, event, function):
        if event not in self.events:
            return

        if function in self.events[event]:
            self.events[event].remove(function)

    def unregister_all(self):
        self.events  = {}
        self.pending = {}

    def trigger_avail(self, event, *args, **kwargs):
        if event not in self.events:
            if event in self.pending:
                self.pending[event].append([ args, kwargs ])
            else:
                self.pending[event] = [ [ args, kwargs] ]
        else:
            self.trigger(event, *args, **kwargs)

    def trigger(self, event, *args, **kwargs):
        if event not in self.events:
            return

        # print('[*] Raising event: ' + event)

        for function in self.events[event]:
            ret = function(*args, **kwargs)
            if ret:
                return ret

events = Events()
