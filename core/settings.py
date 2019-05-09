import os
import yaml

__all__ = ('load_config',)


def load_config(config_file=None):
    default_file = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(default_file, 'r') as f:
        config = yaml.safe_load(f)
    cf_dict = {}
    if config_file:
        cf_dict = yaml.safe_load(config_file)
    config.update(**cf_dict)
    return config





