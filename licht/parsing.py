"""
licht.parsing

@author: phdenzel
"""
import os
from argparse import ArgumentParser, RawTextHelpFormatter
import yaml
import licht


def default_config_file(basename='licht.yml'):
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


def read_args():
    """
    Parse command-line arguments
    """
    p = ArgumentParser(prog='licht', formatter_class=RawTextHelpFormatter)

    p.add_argument("-c", "--config", dest="config_path", metavar="<path>",
                   type=str, default=default_config_file(),
                   help="Path to the config file")
    p.add_argument("-o", "--output", dest="output_file", metavar="<path>",
                   type=str, default="/tmp/licht",
                   help="Path to the output file")
    p.add_argument("-s", "--section", dest="config_section", metavar="<section>",
                   type=str, default="Defaults",
                   help="Section in the yaml file to be parsed")
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
