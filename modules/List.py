from modules.Module import Module

class List(Module):
    def module_load(self):
        self.on_command('list', self.list)
        self.register('channel_list', self.channel_list)

    def list(self, user, line):
        self.trigger('start_list', user)
        self.trigger('channels_list', user)
        self.trigger('end_list', user)

    def channel_list(self, user, channel):
        self.trigger('list_item', user, channel.name, len(channel.users),
            self.trigger('mode_string', channel) or '',
            self.trigger('get_topic', channel) or '')
