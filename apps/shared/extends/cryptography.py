__all__ = [
    'SimpleEncryptor',
]

import base64

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

from django.conf import settings


class SimpleEncryptor:
    @classmethod
    def generate_key(cls, password=None):
        # salt = os.urandom(16)
        salt = b'(8\xb1\xdc\xed?ea5\x90\xce\xa1\xb5dW\x05'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(
            (
                password if password else settings.SECRET_KEY
            ).encode()
        )

    def __init__(self, key=None):
        if not key:
            key = self.generate_key()

        self.key = base64.urlsafe_b64encode(key)
        self.cipher_suite = Fernet(self.key)

    def encrypt(self, data, to_string: bool = True):
        cipher_text = self.cipher_suite.encrypt(data.encode())
        return base64.urlsafe_b64encode(cipher_text).decode() if to_string else cipher_text

    def decrypt(self, cipher_text):
        plain_text = self.cipher_suite.decrypt(cipher_text)
        return plain_text.decode()
