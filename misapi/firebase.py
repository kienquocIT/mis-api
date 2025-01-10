import os

import firebase_admin
from firebase_admin import credentials


def init_firebase(base_dir):
    cred = credentials.Certificate(os.path.join(base_dir, 'serviceAccountKey.json'))
    firebase_admin.initialize_app(cred)
