import os
from dotenv import load_dotenv

__all__ = ['load_env']


def load_env(base_dir=''):
    # load default env
    env_default_path = os.path.join(base_dir, 'env', '.env.default')
    if os.path.exists(env_default_path):
        state = load_dotenv(env_default_path)
        print('[ENV_DEFAULT] loaded: ', state)
    else:
        print('[ENV_DEFAULT] Not found environment file: ', env_default_path)

    # load env file
    env_path = os.path.join(base_dir, '.env')
    if os.path.exists(env_path):
        state = load_dotenv(env_path, override=True)
        print('[ENV_EXTEND] Loaded: ', state)
    else:
        print('[ENV_EXTEND] Not found environment file: ', env_path)

    if os.environ.get('TEST_ENABLED', '0') in [1, '1']:
        print('Load environment... change value some variable...')
        os.environ.update({
            'ENABLE_LOGGING': '0',
            'ENABLE_TRACING': '0',
            'MEDIA_ENABLED': '0',
            'CACHE_ENABLED': '0',
            'CELERY_TASK_ALWAYS_EAGER': '1',
        })
    print('********************************')
    return True
