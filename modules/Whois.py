from modules.Module import Module
import lib.utilities as utilities
import lib.config as config

class Whois(Module):
    def module_load(self):
        self.on_command('who', self.who)
        self.on_command('whois', self.whois)
        self.register('channel_who', self.channel_who)
        self.register('user_who', self.user_who)
        self.register('user_whois', self.user_whois)

    def whois(self, user, line):
        if utilities.validate(line, 2):
            self.trigger('no_nickname', user)
            return

        self.trigger('user_whois', user, line[1][:15])

    def who(self, user, line):
        if utilities.validate(line, 2):
            self.trigger('not_enough_params', user, 'WHO')
            return

        if not line[1].startswith('#'):
            self.trigger('user_who', user, line[1][:15], line[1][:15])
        else:
            chan = line[1][:30]
            if utilities.chan_re.match(chan):
                self.trigger('channels_who', user, chan)

        self.trigger('end_who', user, line[1])

    def user_whois(self, user, nick):
        u = self.trigger('find_user', nick)
        if not u:
            self.trigger('no_such_nick', user, nick)
        else:
            self.trigger('whois_user', user, u.info['nick'], u.info['user'],
                u.info['hostname'], u.info['realname'])
        self.trigger('end_whois', user, nick)

    def channel_who(self, user, chan):
        for u in chan.users:
            self.trigger('user_who', user, chan, u)

    def user_who(self, user, t, target):
        if hasattr(t, 'name'):
            t = t.name
        else:
            target = self.trigger('find_user', target)
            if not target:
                return

        self.trigger('send_user_who', user, t, target.info['user'],
            target.info['hostname'], config.get(target, 'server_name'),
            target.info['nick'], target.info['realname'])
