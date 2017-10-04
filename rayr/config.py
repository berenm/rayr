import json

config = {
    'gitlab': {
        'client': None,
        'secret': None,
        'enabled': False,
    },
    'bitbucket': {
        'client': None,
        'secret': None,
        'enabled': False,
    },
    'github': {
        'client': None,
        'secret': None,
        'enabled': False,
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
