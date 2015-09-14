from modules.Module import Module
from modules.ChannelsModule import channels
import lib.config as config

class Numerics(Module):
    def module_load(self):
        self.register('welcome', self.welcome)
        self.register('welcome_version', self.welcome_version)
        self.register('isupport', self.isupport)
        self.register('user_modes', self.user_modes)
        self.register('not_away', self.not_away)
        self.register('marked_away', self.marked_away)
        self.register('whois_user', self.whois_user)
        self.register('end_whois', self.end_whois)
        self.register('start_list', self.start_list)
        self.register('list_item', self.list_item)
        self.register('end_list', self.end_list)
        self.register('lusers_channels', self.lusers_channels)
        self.register('lusers_users', self.lusers_users)
        self.register('channel_mode_msg', self.channel_modes)
        self.register('channel_time_created', self.channel_time_created)
        self.register('channel_no_topic', self.channel_no_topic)
        self.register('channel_exist_topic', self.channel_exist_topic)
        self.register('channel_topic_time', self.channel_topic_time)
        self.register('send_user_who', self.send_user_who)
        self.register('names_list', self.names_list)
        self.register('end_names', self.end_names)
        self.register('end_channel_ban_list', self.end_channel_ban_list)
        self.register('end_who', self.end_who)
        self.register('motd_start', self.motd_start)
        self.register('motd_text', self.motd_text)
        self.register('motd_end', self.motd_end)
        self.register('no_external_msg', self.no_external_msg)
        self.register('no_such_nick', self.no_such_nick)
        self.register('no_recip', self.no_recip)
        self.register('no_text', self.no_text)
        self.register('msg_blocked', self.msg_blocked)
        self.register('cannot_join', self.cannot_join)
        self.register('not_enough_params', self.not_enough_params)
        self.register('no_nickname', self.no_nickname)
        self.register('bad_nick', self.bad_nick)
        self.register('nick_in_use', self.nick_in_use)
        self.register('bad_host', self.bad_host)
        self.register('not_on_channel', self.not_on_channel)
        self.register('not_chan_op', self.not_chan_op)

    def welcome(self, user):
        user.numeric(1, ':Welcome to the %s IRC Network %s' %
            (config.get(user, 'network_name'), user.umask()))

    def welcome_version(self, user):
        user.numeric(2, ':Your host is %s, running version %s' %
            (config.get(user, 'server_name'), config.get(user, 'server_version')))

    def isupport(self, user):
        user.numeric(5, 'PREFIX=(o)@ CHANTYPES=# CHANMODES=o,,k,as NICKLEN=15' + \
            ' NETWORK=%s CHANNELLEN=30' % (config.get(user, 'network_name')))

    def user_modes(self, user, nick, modes):
        user.numeric(221, '%s +%s' % (nick, modes))

    def not_away(self, user):
        user.numeric(305, '%s :You are no longer marked as being away' %
            user.info['nick'])

    def marked_away(self, user):
        user.numeric(306, '%s :You have been marked as being away' %
            user.info['nick'])

    def whois_user(self, user, nick, uname, hname, rname):
        user.numeric(311, '%s %s %s * :%s' % (nick, uname, hname, rname))

    def end_whois(self, user, nick):
        user.numeric(318, '%s :End of /WHOIS list.' % nick)

    def start_list(self, user):
        user.numeric(321, 'Channel :Users  Name')

    def list_item(self, user, channel, num_users, modes, topic):
        user.numeric(322, '%s %s :[%s] %s' % (channel, num_users, modes, topic))

    def end_list(self, user):
        user.numeric(323, ':End of /LIST')

    def end_who(self, user, channel):
        user.numeric(315, '%s :End of /WHO list.' % channel)

    def channel_modes(self, user, channel, modes):
        user.numeric(324, '%s +%s' % (channel, modes))

    def channel_time_created(self, user, channel, time):
        user.numeric(329, '%s %d' % (channel, time))

    def channel_no_topic(self, user, channel):
        user.numeric(331, '%s :No topic is set.' % channel)

    def channel_exist_topic(self, user, channel, topic):
        user.numeric(332, '%s :%s' % (channel, topic))

    def channel_topic_time(self, user, channel, setter, time):
        user.numeric(333, '%s %s %d' % (channel, setter, time))

    def send_user_who(self, user, chan, uname, hname, sname, nick, rname):
        user.numeric(352, '%s %s %s %s %s H :0 %s' % (chan, uname, hname, sname, nick,
            rname))

    def names_list(self, user, chan, users):
        msg       = '@ %s :' % chan
        tmp_users = []

        for u in users:
            tmp = msg + ' '.join(tmp_users)
            if len(tmp + u) > 450:
                user.numeric(353, tmp)
                tmp_users = []
            tmp_users.append(u)

        user.numeric(353, msg + ' '.join(tmp_users))

    def end_names(self, user, chan):
        user.numeric(366, '%s :End of /NAMES list.' % chan)

    def end_channel_ban_list(self, user, channel):
        user.numeric(368, '%s :End of Channel Ban List' % channel)

    def motd_start(self, user):
        user.numeric(375, ':- %s Message of the Day -' % config.get(user, 'server_name'))

    def motd_text(self, user, motd):
        for line in motd:
            user.numeric(372, ':- %s' % line.rstrip()[:80])

    def motd_end(self, user):
        user.numeric(376, ':End of /MOTD command.')

    def lusers_channels(self, user):
        user.numeric(254, '%d :channels formed' % len(channels))

    def lusers_users(self, user):
        user.numeric(255, ':I have %d clients and 0 servers' % self.trigger('num_users'))

    def no_such_nick(self, user, name):
        user.numeric(401, '%s :No such nick/channel' % name)

    def no_external_msg(self, user, channel):
        user.numeric(404, '%s :No external channel messages (%s)' % (channel, channel))

    def no_recip(self, user):
        user.numeric(411, ':No recipient given (PRIVMSG)')

    def no_text(self, user):
        user.numeric(412, ':No text to send')

    def msg_blocked(self, user, channel, reason):
        user.numeric(413, '%s :Message to %s blocked (%s)' % (channel, channel, reason))

    def cannot_join(self, user, channel):
        user.numeric(474, '%s :Cannot join channel' % channel)

    def not_enough_params(self, user, command):
        user.numeric(461, '%s :Not enough parameters' % command)

    def no_nickname(self, user):
        user.numeric(431, ':No nickname given.')

    def bad_nick(self, user, nick):
        user.numeric(432, '%s :Erroneous Nickname: Illegal characters' % nick)

    def nick_in_use(self, user, nick):
        user.numeric(433, '%s :Nickname is already in use.' % nick)

    def bad_host(self, user, host):
        user.numeric(434, '%s :Erroneous Hostname: Illegal characters' % host)

    def not_on_channel(self, user, channel):
        user.numeric(442, "%s :You're not on that channel" % channel)

    def not_chan_op(self, user, channel):
        user.numeric(482, "%s :You're not channel operator" % channel)
