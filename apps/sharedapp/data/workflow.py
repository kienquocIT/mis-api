<<<<<<<< HEAD:apps/sharedapp/data/workflow.py
Node_data = {
    'abccf657-7dce-4a14-9601-f6c4c4f2722a': {
        'id': 'abccf657-7dce-4a14-9601-f6c4c4f2722a',
        'title': 'Initial Node',
        'code': 'Initial',
        'code_node_system': 'initial',
        'is_system': True,
        'order': 1,
        'workflow': None,
    },
    '1fbb680e-3521-424a-8523-9f7a34ce867e': {
        'id': '1fbb680e-3521-424a-8523-9f7a34ce867e',
        'title': 'Approved Node',
        'code': 'Approved',
        'code_node_system': 'approved',
        'is_system': True,
        'order': 2,
        'workflow': None,
    },
    '580f887c-1280-44ea-b275-8cb916543b10': {
        'id': '580f887c-1280-44ea-b275-8cb916543b10',
        'title': 'Completed Node',
        'code': 'Completed',
        'code_node_system': 'completed',
        'is_system': True,
        'order': 3,
        'workflow': None,
    }
}
========
from apps.core.workflow.models import Node

NODE_SYSTEM_DATA = [
    Node(**{
        'id': 'abccf657-7dce-4a14-9601-f6c4c4f2722a',
        'title': 'Initial Node',
        'code': 'initial',
        'is_system': True,
        'order': 1,
    }),
    Node(**{
        'id': '1fbb680e-3521-424a-8523-9f7a34ce867e',
        'title': 'Approved Node',
        'code': 'approved',
        'is_system': True,
        'order': 2,
    }),
    Node(**{
        'id': '580f887c-1280-44ea-b275-8cb916543b10',
        'title': 'Completed Node',
        'code': 'completed',
        'is_system': True,
        'order': 3,
    })
]
>>>>>>>> 05a8f8b93ad6ac83070d60bd409ac215d3c41aa0:apps/shared/initials/data/workflow.py
