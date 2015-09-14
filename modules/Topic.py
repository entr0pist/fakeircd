from modules.Module import Module
import lib.utilities as utilities
import time

class Topic(Module):
    def module_load(self):
        self.on_command('topic', self.topic)
        self.register('send_topic', self.send_topic)
        self.register('setting_topic', self.setting_topic)
        self.register('channel_topic', self.handle_topic)
        self.register('get_topic', self.get_topic)

    def topic(self, user, line):
        if utilities.validate(line, 2):
            self.trigger('not_enough_params', user, 'TOPIC')
            return

        if not utilities.validate(line, 3):
            new_topic = utilities.join_msg(line[2:])
        else:
            new_topic = None

        if not line[1].startswith('#'):
            channel = '#' + line[1]
        else:
            channel = line[1]

        channel = channel[:30]
        if utilities.chan_re.match(channel):
            self.trigger('channels_topic', user, channel, new_topic)

    def send_topic(self, user, channel, joining=False):
        if channel._topic['topic']:
            self.trigger('channel_exist_topic', user, channel.name,
                channel._topic['topic'])
            self.trigger('channel_topic_time', user, channel.name,
                channel._topic['setter'], channel._topic['time'])
        elif not joining:
            self.trigger('channel_no_topic', user, channel.name)

    def get_topic(self, channel):
        return channel._topic['topic']

    def setting_topic(self, user, channel, new_topic):
        channel._topic['setter'] = user.info['nick']
        channel._topic['time']   = int(time.time())
        channel._topic['topic'] = new_topic
        self.trigger('channel_send_to_all', user, channel,
            'TOPIC %s' % channel.name, new_topic)

    def handle_topic(self, user, channel, new_topic):
        if new_topic:
            self.trigger('setting_topic', user, channel, new_topic)
        else:
            self.trigger('send_topic', user, channel)
