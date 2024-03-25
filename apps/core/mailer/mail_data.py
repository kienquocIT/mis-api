__all__ = ['MailDataResolver']


class MailDataResolver:
    @classmethod
    def welcome(cls, user_obj):
        return {
            '_user': {
                'full_name': user_obj.get_full_name(),
                'user_name': user_obj.username,
            },
        }

    @classmethod
    def otp_verify(cls, user_obj, otp):
        return {
            'full_name': user_obj.get_full_name(),
            'user_name': user_obj.username,
            '_otp': str(otp) if otp else '',
        }

    @classmethod
    def calendar(cls):
        return {}
