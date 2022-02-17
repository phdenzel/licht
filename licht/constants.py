# -*- coding: utf-8 -*-
"""
licht.constants

@author: phdenzel
"""
import licht


default_config_paths = [
    "~/.config/licht",
    "~/.config/.",
    "~/.licht",
    "~/.",
    "./"
]

limits_system = {
    'bri': (0, 255),
    'hue': (0, 65535),
    'sat': (0, 255),
    'xy': ((0, 1), (0, 1)),
    'ct': (153, 500),  # mired
}

# transformations to licht units / to system units
transformations = {
    'bri': (licht.utils.percentages_bit8, licht.utils.bit8),
    'hue': (licht.utils.percentages_bit16, licht.utils.bit16),
    'sat': (licht.utils.percentages_bit8, licht.utils.bit8),
    'xy': None,
    'ct': (licht.utils.blackbody, licht.utils.mired)
}

limits_transf = {
    key: sorted(transformations[key][0](lim) for lim in limits_system[key])
    for key in limits_system
    if transformations[key]
}
