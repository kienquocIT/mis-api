import os
from dotenv import load_dotenv

__all__ = ['load_env']


def load_env(base_dir=''):
    env_default_path = os.path.join(base_dir, 'env', '.env.default')
    if os.path.exists(env_default_path):
        load_dotenv(env_default_path)

    env_path = os.path.join(base_dir, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)

    return True
