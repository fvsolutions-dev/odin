import os

CURR_DIR = os.path.dirname(os.path.abspath(__file__))


def abs_path(path):
    return os.path.join(CURR_DIR, path)


MINIMAL_CONFIG = abs_path("minimal_config.yaml")
