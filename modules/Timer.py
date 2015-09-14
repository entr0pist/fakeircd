from modules.Module import Module
from lib.Sockets import sockets

import ctypes
import os

libc = ctypes.CDLL('libc.so.6')

CLOCK_REALTIME = 0
CLOCK_MONOTONIC = 1

TFD_CLOEXEC  = 524288
TFD_NONBLOCK = 2048

class timespec(ctypes.Structure):
    _fields_ = [ ('tv_sec', ctypes.c_int), ('tv_nsec', ctypes.c_long)]

class itimerspec(ctypes.Structure):
    _fields_ = [ ('it_interval', timespec), ('it_value', timespec)]

class _timer:
    def __init__(self, callback, args):
        self.closed = False
        self.fd = os.fdopen(libc.timerfd_create(CLOCK_REALTIME, TFD_NONBLOCK), 'r')
        self.callback = callback
        self.args = args

    def settimer(self, secs, nanosecs=0, repeat=True):
        timer = itimerspec()

        timer.it_value.tv_sec  = secs
        timer.it_value.tv_nsec = nanosecs

        if repeat:
            timer.it_interval.tv_sec  = secs
            timer.it_interval.tv_nsec = nanosecs

        self.__settime(timer)

    def unsettimer(self):
        self.__settime(itimerspec())

    def __settime(self, timer):
        libc.timerfd_settime(self.fd.fileno(), 0, ctypes.byref(timer), None)

    def read(self):
        self.fd.read(8)

        if not self.args:
            self.callback(self)
        else:
            self.callback(self, *self.args)

    def close(self):
        if not self.closed:
            sockets.rm_sock(self)
            return self.fd.close()

    def fileno(self):
        return self.fd.fileno()

class Timer(Module):
    def module_load(self):
        self.timers = []
        self.register('timer', self.timer)
        self.register('unset_timer', self.unset_timer)

    def module_unload(self):
        for timer in self.timers:
            timer.unsettimer()
            timer.close()
        self.timers = []

    def unset_timer(self, t):
        t.unsettimer()
        t.close()
        self.timers.remove(t)

    def timer(self, func, time, repeat=True, args=None):
        t = _timer(func, args)
        t.settimer(time, repeat=repeat)
        sockets.add_sock(t)
        self.timers.append(t)
