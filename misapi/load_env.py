import os
from dotenv import load_dotenv

__all__ = ['load_env']


def load_env(base_dir=''):
    # load env file
    env_path = os.path.join(
        base_dir, '.env'
    )
    load_dotenv(env_path)

    if os.environ.get('TEST_ENABLED', '0') in [1, '1']:
        print('Load environment... change value some variable...')
        os.environ.update({
            'ENABLE_LOGGING': '0',
            'ENABLE_TRACING': '0',
            'MEDIA_ENABLED': '0',
            'CACHE_ENABLED': '0',
            'CELERY_TASK_ALWAYS_EAGER': '1',
        })

    print('[load_env] Load environment... done')
    return True
