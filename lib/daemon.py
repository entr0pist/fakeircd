import os
import signal
import sys

from lib.Sockets       import sockets
from lib.module_driver import modules

pid_file = 'data/pid'

def check_pid(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True

def read_pid():
    return int(open(pid_file).read().rstrip())

def write_pid():
    try:
        dirs = os.path.split(pid_file)[0]
        os.makedirs(dirs)
    except:
        pass

    open(pid_file, 'w').write(str(os.getpid()))

def start():
    print('[*] Starting server..')

    try:
        if check_pid(read_pid()):
            print('[!] Process already started!')
            return
    except:
        pass

    try:
        modules.load_all()
        sockets.spawn_all()
    except Exception as e:
        print('[!] Server boot failed: %s' % e)
        return

    print('[*] Server successfully started.')

    if os.fork(): quit()
    if os.fork(): quit()

    write_pid()

    os.setsid()

    sys.stdout = open('/dev/null', 'w')
    sys.stderr = open('data/errors', 'w')
    sys.stdin  = open('/dev/null')

    sockets.serve()

def stop():
    print('[*] Stopping server.')

    try:
        pid = read_pid()
    except Exception as e:
        print('[!] Could not read PID file: %s' % e)
        return

    try:
        os.kill(pid, signal.SIGTERM)
    except Exception as e:
        print('[!] Could not stop server: %s' % e)
        return

    os.remove(pid_file)

def restart():
    print('[*] Restarting server.')

    stop()
    start()

def reload():
    print('[*] Reloading server.')

    try:
        pid = read_pid()
    except Exception as e:
        print('[!] Could not read PID file: %s' % e)
        return

    try:
        os.kill(pid, signal.SIGHUP)
    except Exception as e:
        print('[!] Could not reload server: %s' % e)
