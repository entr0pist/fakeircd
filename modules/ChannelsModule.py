from modules.Module import Module
from lib.globals import channels
import time

class Channel:
    def __init__(self, name):
        self.created = int(time.time())
        self.name   = name
        self.users  = []
        self._topic = {
            'topic'  : '',
            'setter' : '',
            'time'   : 0
        }
        self.modes = { 'a': True }

    def on(self, nick):
        if hasattr(nick, 'info'):
            nick = nick.info['nick']

        for user in self.users:
            if user.info['nick'].lower() == nick.lower():
                return user

class ChannelsModule(Module):
    def module_load(self):
        self.register('channels_join', self.channel_join)
        self.register('channels_mode', self.channel_mode)
        self.register('channels_who', self.channel_who)
        self.register('channels_privmsg', self.channel_privmsg)
        self.register('channels_names', self.channel_names)
        self.register('channels_part', self.channel_part)
        self.register('channels_kick', self.channel_kick)
        self.register('channels_topic', self.channel_topic)
        self.register('channels_list', self.channel_list)
        self.register('channel_send_to_all', self.channel_send_to_all)
        self.register('channel_send_to_all_but_one', self.channel_send_to_all_but_one)
        self.register('send_to_all_shared', self.send_to_all_shared)
        self.register('get_all_chans', self.get_all_chans)

    def get(self, channel):
        if channel and channels and channel in channels:
            return channels[channel]

    def do_channel(self, user, channel, command, *args, **kwargs):
        chan = self.get(channel)
        if chan and chan.on(user):
            self.trigger('channel_' + command, user, chan, *args, **kwargs)
            if not len(chan.users):
                self.trigger('channel_destroyed', channel)
                del channels[channel]
            return chan

        self.trigger('not_on_channel', user, channel)

    def channel_join(self, user, channel):
        if self.trigger('check_ban', user, channel):
            self.trigger('cannot_join', user, channel)
            return True

        chan = self.get(channel)
        if not chan:
            channels[channel] = Channel(channel)
            chan = channels[channel]
            self.trigger('channel_created', user, chan)

        if chan.on(user):
            return True

        self.trigger('channel_join', user, chan)

    def channel_mode(self, user, channel, modes):
        self.do_channel(user, channel, 'mode', modes)

    def channel_who(self, user, channel):
        chan = self.get(channel)
        if chan and chan.on(user):
            self.trigger('channel_who', user, chan)

    def channel_privmsg(self, user, channel, message):
        self.do_channel(user, channel, 'privmsg', message)

    def channel_names(self, user, channel):
        self.do_channel(user, channel, 'names')

    def channel_part(self, user, channel, message):
        self.do_channel(user, channel, 'part', message)

    def channel_kick(self, user, channel, nick, message):
        self.do_channel(user, channel, 'kick', nick, message)

    def channel_topic(self, user, channel, new_topic):
        self.do_channel(user, channel, 'topic', new_topic)

    def channel_list(self, user):
        for chan in channels:
            self.trigger('channel_list', user, channels[chan])

    def channel_send_to_all(self, user, channel, cmd, message):
        if hasattr(user, 'umask'):
            umask = user.umask()
        else:
            umask = user

        for user in channel.users:
            user.send(':%s %s :%s' % (umask, cmd, message))

    def channel_send_to_all_but_one(self, user, channel, cmd, msg):
        for u in channel.users:
            if u == user:
                continue
            u.send(':%s %s :%s' % (user.umask(), cmd, msg))

    def send_to_all_shared(self, user, cmd, msg):
        sent = [ user ]
        for chan in channels.values():
            if user not in chan.users:
                continue

            for u in chan.users:
                if u in sent:
                    continue
                u.send(':%s %s :%s' % (user.umask(), cmd, msg))
                sent.append(u)

    def get_all_chans(self):
        return channels
