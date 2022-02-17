"""
licht.parsing

@author: phdenzel
"""
import os
import sys
import site
from argparse import ArgumentParser, RawTextHelpFormatter
import yaml
import licht


def default_config_file(basename='licht.yml'):
    """
    Get the path of the configuration with the highest priority
    """
    paths = licht.constants.default_config_paths
    for p in paths:
        p = os.path.expanduser(p)
        if not p.endswith("."):
            filename = os.path.join(p, basename)
        else:
            bn = '.' + basename
            p = os.path.dirname(p)
            filename = os.path.join(p, bn)
        if os.path.exists(filename):
            return filename
    return basename


def find_icon_path(basename='assets/licht_icon.svg'):
    basename = os.path.expanduser(basename)
    if os.path.exists(basename):
        return basename
    for directories in (sys.prefix, site.USER_BASE,
                        '~/.config/licht', '~/.licht'):
        filename = os.path.join(os.path.expanduser(directories), basename)
        if os.path.exists(filename):
            return filename
    return basename


def read_args():
    """
    Parse command-line arguments
    """
    p = ArgumentParser(prog='licht', formatter_class=RawTextHelpFormatter)

    # LichtApplet
    p.add_argument("-d", "--daemon", dest="as_daemon", action="store_true",
                   help="Run the Licht applet as a daemon process")
    p.add_argument("-a", "--app", "--applet", dest="app_mode", action="store_true",
                   help="Run the Licht applet")

    # LichtClient.fetch_data
    p.add_argument("--lights", "--list-lights", dest="list_lights",
                   action="store_true",
                   help="List the index of lights in the network")
    p.add_argument("--groups", "--list-groups", dest="list_groups",
                   action="store_true",
                   help="List the index of groups in the network")
    p.add_argument("--scenes", "--list-scenes", dest="list_scenes",
                   action="store_true",
                   help="List the index of groups in the network")

    # LichtClient.state_change
    p.add_argument("-l", "--light", "--light-id", dest="light",
                   metavar="<light-id>", type=str,
                   help="Light-id for state change")
    p.add_argument("-g", "--group", "--group-id", dest="group",
                   metavar="<group-id>", type=str,
                   help="Group-id for state change")
    p.add_argument("-s", "--scene", "--scene-id", dest="scene",
                   metavar="<scene-id>", type=str,
                   help="Scene-id for state change")
    p.add_argument("-p", "--subpath", dest="subpath",
                   metavar="<subpath>", type=str,
                   help="Subpath for state change")
    p.add_argument("-o", "--on", dest="on", type=licht.utils.str2bool_explicit,
                   default=None,
                   choices=['true', 'false', 1, 0, 'yes', 'no', 'y', 'n'],
                   help="Toggle lights on")
    p.add_argument("-b", "--bri", dest="bri", metavar="<bri-value>",
                   type=int,
                   help="Update for the brightness value [0-255]")
    p.add_argument("-t", "--ct", dest="ct", metavar="<color-temp-value>",
                   type=int,
                   help="Update for the color temperature value [0-65535]")
    p.add_argument("-u", "--update", metavar="<json-string>", type=str,
                   help="Update body for the PUT request")

    # Configuration settings
    p.add_argument("--register", dest="register", action="store_true",
                   help="Authenticate licht and receive a username from bridge")
    p.add_argument("-c", "--config", dest="config_path", metavar="<path>",
                   type=str, default=default_config_file(),
                   help="Path to the config file")
    p.add_argument("--section", dest="config_section", metavar="<section>",
                   type=str, default="Defaults",
                   help="Section in the yaml file to be parsed")
    p.add_argument("--dark-icon", dest="dark_icon", action="store_true",
                   help="Use a dark icon on systray (for light themes)")
    p.add_argument("--output", dest="output_file", metavar="<path>", type=str,
                   help="Set the path of the output log-file")
    p.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                   help="Run program in verbose mode")
    args = p.parse_args()
    licht.parser = p
    licht.args = args
    return p, args


def load_args(args=None):
    """
    Load command-line arguments into main module

    Kwargs:
        args <Namespace>
    """
    if args is None:
        args = licht.args
    for a in vars(args):
        val = getattr(args, a)
        if val is not None:
            setattr(licht, a, val)


def read_configs(config_path=None):
    """
    Parse the configuration file

    Kwargs:
        config_path <str>
    """
    if config_path is None:
        config_path = licht.args.config_path
    with open(config_path, 'r') as c:
        configs = yaml.safe_load(c)
    licht.configs = configs
    return configs


def write_configs(configs=None, config_path=None):
    """
    Write or update the configuration file

    Kwargs:
        config_path <str>
    """
    if configs is None:
        configs = licht.configs
    if config_path is None:
        config_path = licht.args.config_path
    with open(config_path, 'w') as c:
        d = yaml.dump(configs, c)
    return d


def load_configs(config_section='Defaults'):
    """
    Load section from parsed configuration file into main module
    """
    confs = licht.configs[config_section]
    for k in confs:
        if confs[k] is not None:
            setattr(licht, k, confs[k])
