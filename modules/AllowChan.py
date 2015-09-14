from sets import Set
from modules.Module import Module
import lib.config as config
import lib.utilities as utilities
import re

class AllowChan(Module):
    def module_load(self):
        self.on_command('allow_chan', self.allow_chan)
        self.on_command('deny_chan', self.deny_chan)
        self.on_command('list_chans', self.list_chans)
        self.register('check_ban', self.banned)

    def banned(self, user, channel):
        ban = False

        deny = config.get(user, 'chan_deny')
        if deny:
            for chan in deny:
                if re.match(chan, channel):
                    ban = True

        allow = config.get(user, 'chan_allow')
        if allow:
            for chan in allow:
                if re.match(chan, channel):
                    ban = False

        return ban

    def allow_chan(self, user, line):
        self.manage_chan(user, line, False)

    def deny_chan(self, user, line):
        self.manage_chan(user, line)

    def manage_chan(self, user, line, deny=True):
        if not config.get(user, 'oper') or utilities.validate(line, 2):
            return

        allow_chans = Set([])
        deny_chans  = Set([])
        blocks      = []

        for listen in config.get(None, 'listen'):
            if 'user' in listen and listen['user'] == line[1]:
                blocks.append(listen)

        if not blocks:
            user.srv_notice('%s: [!] User not found: %s' % (user.info['nick'], line[1]))
            return

        action = 'Allow'
        if deny:
            action = 'Deny'

        user.srv_notice('%s : [*] %sing channel: %s' % (user.info['nick'], action, line[2]))

        for block in blocks:
            def merge(elem, chans):
                if elem not in block:
                    return
                chans.update(block[elem])

            merge('chan_allow', allow_chans)
            merge('chan_deny', deny_chans)

        if deny:
            allow_chans.discard(line[2])
            deny_chans.add(line[2])
        else:
            allow_chans.add(line[2])
            deny_chans.discard(line[2])

        for block in blocks:
            block['chan_allow'] = list(allow_chans)
            block['chan_deny'] = list(deny_chans)

        config.write_config()

    def list_chans(self, user, line):
        if not config.get(user, 'oper') or utilities.validate(line, 2):
            return

        allow_chans = config.get(line[1], 'chan_allow', True) or []
        deny_chans = config.get(line[1], 'chan_deny', True) or []

        for chan in allow_chans:
            if chan in deny_chans:
                deny_chans.remove(chan)

        user.srv_notice('%s : [*] Allowed channels:' % (user.info['nick']))
        for chan in allow_chans:
            user.srv_notice('%s : - %s' % (user.info['nick'], chan))

        user.srv_notice('%s : [*] Denied channels:' % (user.info['nick']))
        for chan in deny_chans:
            user.srv_notice('%s : - %s' % (user.info['nick'], chan))
