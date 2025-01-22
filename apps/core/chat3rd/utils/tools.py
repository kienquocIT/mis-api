__all__ = ['ChatTools']

from django.conf import settings

from apps.shared import SimpleEncryptor
from apps.shared.extends.env import get_env_var


class ChatTools:
    @staticmethod
    def cryptor() -> SimpleEncryptor:
        password = SimpleEncryptor().generate_key(
            password=get_env_var('CHAT_ENCRYPT_PASSWORD', settings.PASSWORD_TOTP_2FA)
        )
        return SimpleEncryptor(key=password)

    @staticmethod
    def encrypt(secret_data) -> str:
        return ChatTools.cryptor().encrypt(secret_data)

    @staticmethod
    def decrypt(encrypted_data):
        return ChatTools.cryptor().decrypt(encrypted_data)
