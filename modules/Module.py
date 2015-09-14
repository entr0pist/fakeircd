from lib.events import events

class Module(object):
    def __init__(self):
        self.events = events

    def module_load(self):
        pass

    def module_unload(self):
        pass

    def on_command(self, command, function):
        self.events.register('command_%s' % command, function)

    def run_command(self, command, *args, **kwargs):
        return self.events.trigger('command_%s' % command, *args, **kwargs)

    def register(self, event, function):
        self.events.register(event, function)

    def register_first(self, event, function):
        self.events.register_first(event, function)

    def trigger(self, event, *args, **kwargs):
        return self.events.trigger(event, *args, **kwargs)

    def trigger_avail(self, event, *args, **kwargs):
        return self.events.trigger_avail(event, *args, **kwargs)
