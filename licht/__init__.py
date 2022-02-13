"""
licht.__init__

@author: phdenzel
"""
from types import ModuleType
import licht
import licht.parsing
import licht.data
import licht.utils
import licht.constants
import licht.rest


config_path = 'licht.yml'
config_section = 'Defaults'
bridge_ip = None
username = None
output_file = '/tmp/licht'


parser, args = licht.parsing.read_args()
licht.parsing.read_configs()
licht.parsing.load_configs(args.config_section)
licht.parsing.load_args()


def env():
    """
    All variables from licht module as dictionary
    """
    env_d = {}
    for vstr in dir(licht):
        if vstr in ('configs', 'args', 'parser'):
            continue
        v = getattr(globals()['licht'], vstr)
        if not vstr.startswith("__") and not isinstance(v, (type, ModuleType)) and not callable(v):
            env_d[vstr] = v
    return env_d
