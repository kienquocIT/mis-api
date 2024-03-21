__all__ = [
    'SimpleEncryptor',
]

import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet, InvalidToken, InvalidSignature

from django.conf import settings


class SimpleEncryptor:
    @classmethod
    def generate_key(cls, salt=None, password=None):
        if not salt:
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

    @classmethod
    def test(cls, data_test="abc123"):
        try:
            salt = os.urandom(16)
            key = cls.generate_key(salt=salt, password=settings.SECRET_KEY)

            enc_data = cls(key=key).encrypt(data_test)
            print('Encrypt Data: ', enc_data)

            dec_data = cls(key=key).decrypt(enc_data)
            print('Decrypt Data: ', dec_data)

            print('Successfully')
            return True
        except Exception as err:
            print('Errors:', str(err))
        return False

    def __init__(self, key=None):
        if not key:
            key = self.generate_key()

        self.key = base64.urlsafe_b64encode(key)
        self.cipher_suite = Fernet(self.key)

    def encrypt(self, data, to_string: bool = True):
        cipher_text = self.cipher_suite.encrypt(data.encode('utf-8'))
        return cipher_text.decode('utf-8') if to_string else cipher_text

    def decrypt(self, cipher_text, invalid_token_return=None, invalid_signature_return=None):
        try:
            if not isinstance(cipher_text, (bytes, bytearray)):
                cipher_text = str(cipher_text).encode('utf-8')
            plain_text = self.cipher_suite.decrypt(cipher_text)
            return plain_text.decode()
        except InvalidToken:
            return invalid_token_return
        except InvalidSignature:
            return invalid_signature_return
        except Exception as err:
            raise err
