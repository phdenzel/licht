"""
licht.__init__

@author: phdenzel
"""
from types import ModuleType
import logging
import licht
import licht.parsing
import licht.data
import licht.utils
import licht.constants
import licht.rest
import licht.app


config_path = 'licht.yml'
config_section = 'Defaults'
icon_path = 'assets/licht_icon.svg'
output_file = '/tmp/licht.log'
bridge_ip = None
username = None


parser, args = licht.parsing.read_args()
licht.parsing.read_configs()
licht.parsing.load_configs(args.config_section)
licht.parsing.load_args()

if licht.args.dark_icon:
    licht.icon_path = licht.icon_path.replace('.svg', '_dark.svg')
licht.icon_path = licht.parsing.find_icon_path(licht.icon_path)

logging.basicConfig(
    level=logging.DEBUG, filename=licht.output_file,
    filemode="a+", style="{", format="{asctime:<15} {levelname:<8} {message}")
logging.info(f'Using log-file {licht.output_file}')
logging.info(f'Loading configurations from {licht.config_path}:{licht.config_section}')


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
