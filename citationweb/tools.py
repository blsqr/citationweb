"""Collection of tool functions"""

import collections

from pkg_resources import resource_filename

import yaml

# Local constants
CFG_PATH = resource_filename('citationweb', 'cfg.yml')

# -----------------------------------------------------------------------------

def load_cfg(modstr: str=None) -> dict:
    """Loads the config file for the citationweb package"""
    with open(CFG_PATH) as cfg_file:
        cfg = yaml.safe_load(cfg_file.read())

    if modstr:
        # From the modstr, get the module
        module = ".".join(modstr.split(".")[1:])

        # Extract the config for the corresponding module
        cfg = cfg[module]

    return cfg

def recursive_update(d: dict, u: dict) -> dict:
    """Recursively updates the Mapping-like object `d` with the Mapping-like
    object `u` and returns it. Note that this does not create a copy of `d`!
    
    Based on: http://stackoverflow.com/a/32357112/1827608
    
    Args:
        d (dict): The mapping to update
        u (dict): The mapping whose values are used to update `d`
    
    Returns:
        dict: The updated dict `d`
    """
    for k, v in u.items():
        if isinstance(d, collections.abc.Mapping):
            # Already a Mapping
            if isinstance(v, collections.abc.Mapping):
                # Already a Mapping, continue recursion
                d[k] = recursive_update(d.get(k, {}), v)
                # This already creates a mapping if the key was not available
            else:
                # Not a mapping -> at leaf -> update value
                d[k] = v    # ... which is just u[k]

        else:
            # Not a mapping -> create one
            d = {k: u[k]}
    return d
