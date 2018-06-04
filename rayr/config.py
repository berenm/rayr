import json

config = {
    'gitlab': {
        'client': None,
        'secret': None,
        'enabled': False,
        'private': False,
    },
    'bitbucket': {
        'client': None,
        'secret': None,
        'enabled': False,
        'private': False,
    },
    'github': {
        'client': None,
        'secret': None,
        'enabled': False,
        'private': False,
    },
    'exclude': {
        'groups': [],
        'repos': [],
    }
}

try:
    config.update(json.load(open('.rayrrc', 'r')))
except FileNotFoundError:
    pass
