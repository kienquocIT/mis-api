__all__ = [
    'get_env_var',
]

import os


def get_env_var(env_key, default=None):
    return os.getenv(env_key, default=default)
