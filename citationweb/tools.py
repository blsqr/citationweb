"""Collection of tool functions"""

from pkg_resources import resource_filename

import yaml

# Local constants
CFG_PATH = resource_filename('citationweb', 'cfg.yml')

# -----------------------------------------------------------------------------

def load_cfg(modstr: str=None) -> dict:
    """Loads the config file for the citationweb package"""
    with open(CFG_PATH) as cfg_file:
        cfg = yaml.load(cfg_file.read())

    if modstr:
        # From the modstr, get the module
        module = ".".join(modstr.split(".")[1:])

        # Extract the config for the corresponding module
        cfg = cfg[module]

    return cfg
