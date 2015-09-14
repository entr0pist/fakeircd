from modules.Module import Module

class DisableCommands(Module):
    def module_load(self):
        self.register('allowed_command', self.allowed_command)

    def allowed_command(self, user, line):
        allowed_cmds = [
            'pong', 'nick', 'user', 'post', 'delete', 'get', 'trace',
            'put', 'patch'
        ]

        if line[0].lower() not in allowed_cmds and not user.connected():
            return True
