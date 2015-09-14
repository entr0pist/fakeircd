#!/usr/bin/python2
import lib.daemon as daemon
import sys

if __name__ == '__main__':
    actions = [ 'start', 'stop', 'restart', 'reload' ]

    if len(sys.argv) < 2 or sys.argv[1] not in actions:
       print('Usage: %s [%s]' % (sys.argv[0], '|'.join(actions)))
       quit()

    getattr(daemon, sys.argv[1])()
