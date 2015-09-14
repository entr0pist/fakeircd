import os
import sys
import importlib

class Modules(object):
    def __init__(self):
        self.modules = {}

    def load_all(self):
        for module_name in os.listdir('modules'):
            if not module_name.endswith('.py'):
                continue

            module_name = '.'.join(module_name.split('.')[:-1])

            if module_name in [ '__init__', 'Module' ]:
                continue

            self.load_module(module_name)

    def load_module(self, module_name):
        if module_name in self.modules:
            self.unload_module(module_name)

        module = importlib.import_module('modules.' + module_name)

        self.modules[module_name] = getattr(module, module_name)()
        self.modules[module_name].module_load()

    def unload_module(self, module_name):
        if module_name not in self.modules:
            return

        self.modules[module_name].module_unload()
        del sys.modules['modules.' + module_name]
        del self.modules[module_name]

modules = Modules()
