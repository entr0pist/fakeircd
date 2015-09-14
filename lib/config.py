import json
config = None

def get(user, option, nick=False):
    if user:
        server = get_listen(user, nick=nick)
        if server and option in server:
            return server[option]

    if option in config:
        return config[option]

    return None

def get_listen_by_host_port((hostname, port)):
    for server in config['listen']:
        if (server['bind_address'], server['bind_port']) == (hostname, port):
            return server

def get_listen(user, nick=False):
    if not nick:
        return get_listen_by_host_port(user.saddr)
    else:
        for server in config['listen']:
            if 'user' in server and server['user'] == user:
                return server

def load_config():
    global config
    config = json.load(open("config.json"))

def write_config():
    json.dump(config, open("config.json", "w"), indent=4)

load_config()
