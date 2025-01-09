import abc
from datetime import timedelta

import requests
from django.utils import timezone
from rest_framework import serializers

from apps.core.chat3rd.models import MessengerToken, MessengerPageToken, MessengerMessage, MessengerPerson
from apps.core.chat3rd.msg import Chat3rdMsg
from misapi.mongo_client import mongo_log_call_fb_api


# Trường            → Ý nghĩa/Topic
# message           → Tin nhắn văn bản hoặc đa phương tiện được gửi bởi người dùng.
# delivery          → Tin nhắn từ bot đã được chuyển đến người dùng.
# read              → Tin nhắn từ bot đã được người dùng đọc.
# postback          → Người dùng tương tác với một nút hoặc hành động có kèm postback payload.
# optin             → Người dùng opt-in (đăng ký nhận tin nhắn) thông qua quảng cáo hoặc mã giới thiệu Messenger.
# referral          → Người dùng được dẫn đến bot qua một liên kết giới thiệu hoặc quảng cáo click-to-Messenger.
# handover          → Các sự kiện chuyển giao cuộc trò chuyện giữa bot của bạn và các ứng dụng khác.
# policy_enforcement → Thông báo liên quan đến vi phạm chính sách hoặc thực thi chính sách từ Facebook.


class SenderSerializer(serializers.Serializer):  # noqa
    id = serializers.CharField()


class RecipientSerializer(serializers.Serializer):  # noqa
    id = serializers.CharField()


class BaseHookSerializer(serializers.Serializer):  # noqa
    sender = SenderSerializer()
    recipient = RecipientSerializer()
    timestamp = serializers.CharField()

    @classmethod
    def get_sender_recipient(cls, page_obj: MessengerPageToken, sender_data, recipient_data):
        sender_id = sender_data['id']
        recipient_id = recipient_data['id']
        create_data = {
            'tenant_id': page_obj.tenant_id,
            'company_id': page_obj.company_id,
            'page': page_obj,
            'account_id': None,
        }

        if sender_id != page_obj.account_id:
            create_data['account_id'] = sender_id
        elif recipient_id != page_obj.account_id:
            create_data['account_id'] = recipient_id

        if create_data['account_id']:
            person_obj = None

            try:
                person_obj = MessengerPerson.objects.get(**create_data)
                person_obj.last_updated = timezone.now()
                person_obj.save(update_fields=['last_updated'])
            except MessengerPerson.DoesNotExist:
                account_data = GraphFbApi(page_obj=page_obj).get_profile(account_id=create_data['account_id'])
                if account_data:
                    create_data = {
                        **create_data,
                        'name': f'{account_data["first_name"]} {account_data["last_name"]}',
                        'avatar': account_data['profile_pic'],
                        'last_updated': timezone.now(),
                    }
                    person_obj = MessengerPerson.objects.create(**create_data)

            if person_obj:
                return {
                    'page': page_obj,
                    'person': person_obj,
                    'sender': sender_id,
                    'recipient': recipient_id,
                }
        return None

    @classmethod
    def validate_timestamp(cls, attrs):
        try:
            return int(attrs)
        except ValueError:
            pass
        raise serializers.ValidationError(
            {
                'timestamp': Chat3rdMsg.TIMESTAMP_INCORRECT,
            }
        )


class AttachmentPayloadSerializer(serializers.Serializer):  # noqa
    url = serializers.CharField()
    sticker_id = serializers.CharField(required=False, default=None)


class AttachmentItemSerializer(serializers.Serializer):  # noqa
    type = serializers.CharField()
    payload = AttachmentPayloadSerializer()


class MesssageSerializer(serializers.Serializer):  # noqa
    mid = serializers.CharField()
    text = serializers.CharField(required=False, default='')
    attachments = AttachmentItemSerializer(many=True, required=False, default=[])
    is_echo = serializers.BooleanField(default=False)
    app_id = serializers.IntegerField(default=None)


class MessengerReceiveSerializer(BaseHookSerializer):  # noqa
    message = MesssageSerializer()

    def save(self, page_obj: MessengerPageToken, **kwargs) -> MessengerMessage or None:  # pylint: disable=W0221
        validated_data = {**self.validated_data, **kwargs}
        sender = validated_data['sender']
        recipient = validated_data['recipient']
        timestamp = validated_data['timestamp']
        message = validated_data['message']

        mid = message['mid']
        text = message['text']
        attachments = message['attachments']
        is_echo = message['is_echo']

        obj = MessengerMessage.objects.filter(mid=mid).first()
        if not obj:
            sender_recipient = self.get_sender_recipient(
                page_obj=page_obj,
                sender_data=sender,
                recipient_data=recipient,
            )
            if not sender_recipient:
                return None
            obj = MessengerMessage.objects.create(
                tenant_id=page_obj.tenant_id,
                company_id=page_obj.company_id,
                **sender_recipient,
                timestamp=timestamp,
                mid=mid,
                text=text,
                attachments=attachments,
                is_echo=is_echo,
            )
        return obj

    class Meta:
        fields = ('sender', 'recipient', 'timestamp', 'message')


class MessengerDeliverySerializer(BaseHookSerializer):  # noqa
    class Meta:
        fields = ('sender', 'recipient', 'timestamp', 'message')


class MessengerControl:
    _data: dict
    _entry: list[dict]
    _page_obj: dict[str, MessengerPageToken]

    def get_page(self, page_id):
        if page_id:
            if page_id in self._page_obj:
                return self._page_obj[page_id]
            try:
                return MessengerPageToken.objects.get(account_id=page_id)
            except MessengerPageToken.DoesNotExist:
                pass
        return None

    def __init__(self, data: dict):
        self._page_obj = {}
        self._data = data
        if data and isinstance(data, dict):
            val_obj = data.get('object', None)
            val_entry = data.get('entry', None)
            if val_obj and val_entry:
                self._entry = val_entry
            else:
                raise ValueError(f'[MessengerControl][receive] Format not support: {str(data)}')
        else:
            raise ValueError(f'[MessengerControl][receive] Format not support: {str(data)}')

    @classmethod
    def get_serial_by_topic(cls, messaging_item: dict):
        if 'message' in messaging_item:
            return MessengerReceiveSerializer(data=messaging_item)
        # if 'delivery' in messaging_item:
        #     return MessengerDeliverySerializer(data=messaging_item)
        return None

    def active(self):
        if self._entry:  # pylint: disable=R1702
            errs = []
            for item in self._entry:
                page_obj = self.get_page(page_id=item.get('id', None))
                messaging = item.get('messaging', [])
                if page_obj and isinstance(messaging, list):
                    for messaging_item in messaging:
                        ser = self.get_serial_by_topic(messaging_item=messaging_item)
                        if ser:
                            ser.is_valid(raise_exception=False)
                            if ser.errors:
                                errs.append(ser.errors)
                            else:
                                ser.save(page_obj=page_obj)
            if errs:
                raise ValueError(str(errs))
            return True
        return False


class MessengerHook:
    _page_obj: MessengerPageToken

    def __init__(self, page_obj: MessengerPageToken):
        self._page_obj = page_obj

    class Meta:
        abstract = True


class GraphAbstract(abc.ABC):
    schema: str
    domain: str
    fb_version: str
    _url: str or None

    @property
    def url(self):
        if self._url is None:
            self._url = f'{self.schema.lower()}://{self.domain.lower()}/{self.fb_version.lower()}'
        return self._url

    def __init__(self, schema: str = 'https', domain: str = 'graph.facebook.com', fb_version: str = 'v21.0', **kwargs):
        self.schema = schema
        self.domain = domain
        self.fb_version = fb_version
        self._url = None


FB_MAX_CALL_PER_HOUR = 200


def get_called(company_id):
    one_hour_ago = timezone.now() - timedelta(hours=1)
    return mongo_log_call_fb_api.count_documents(
        {
            "metadata.company_id": str(company_id),
            "timestamp": {"$gte": one_hour_ago},
        }
    )


def check_available_call(company_id):
    count = get_called(company_id)
    if count < FB_MAX_CALL_PER_HOUR:
        return True
    return False


def call_graph_api(
        company_id, url, method='get', params: dict = None, payload: dict = None
) -> requests or None or ValueError:
    if not params:
        params = {}
    if not payload:
        payload = {}

    if check_available_call(company_id) is True:
        resp = None
        method = method.upper()
        if method == 'GET':
            resp = requests.get(url=url, params=params, timeout=30)
        elif method == 'POST':
            resp = requests.post(url=url, params=params, data=payload, timeout=30)

        if resp:
            mongo_log_call_fb_api.insert_one(
                metadata=mongo_log_call_fb_api.metadata(company_id=str(company_id)),
                url=url,
                method=method,
                resp_status=resp.status_code,
            )
            return resp
        raise ValueError('NOT_ENOUGH')
    return None


class GraphFbMigrate(GraphAbstract):
    code: str
    redirect_uri: str

    def __init__(self, code: str, redirect_uri: str, **kwargs):
        self.code = code
        self.redirect_uri = redirect_uri
        super().__init__(**kwargs)

    def get_token_long_lived(self, tenant_id, company_id, employee_id) -> MessengerToken or None:
        response = call_graph_api(
            company_id=company_id,
            method='get',
            url='https://graph.facebook.com/v21.0/oauth/access_token',
            params={
                'client_id': '1125911575074544',
                'client_secret': 'a850c0de503e318e73226393e6bca549',
                'redirect_uri': self.redirect_uri,
                'code': self.code,
            }
        )
        if response:
            if response.status_code == 200:
                data = response.json()
                obj_token, _created = MessengerToken.objects.get_or_create(
                    company_id=company_id,
                    defaults={
                        'tenant_id': tenant_id,
                        'company_id': company_id,
                        'employee_created_id': employee_id,
                    }
                )
                obj_token.token = data['access_token']
                if 'expires_in' in data:
                    obj_token.expires = timezone.now() + timedelta(seconds=data['expires_in'] - 60 * 4)
                obj_token.employee_modified_id = employee_id
                obj_token.save()
                return obj_token
        return None


class GraphFbAccount(GraphAbstract):
    token_obj: MessengerToken

    def __init__(self, token_obj: MessengerToken, **kwargs):
        self.token_obj = token_obj
        super().__init__(**kwargs)

    @property
    def params(self):
        return {
            'access_token': self.token_obj.token
        }

    def sync_accounts_token(self) -> int or None:  # pylint: disable=R0914
        count = None
        if self.token_obj:  # pylint: disable=R1702
            full_url = self.url + '/me/accounts?fields=access_token,category,category_list,name,id,tasks,picture{url,' \
                                  'height,width},link'
            response = call_graph_api(
                company_id=self.token_obj.company_id,
                method='get',
                url=full_url,
                params=self.params,
            )
            if response:
                if response.status_code == 200:
                    keep_account_ids = None

                    # re-get accounts
                    count = 0
                    response_data = response.json()
                    if 'data' in response_data:
                        data = response_data['data']
                        if data and isinstance(data, list):
                            keep_account_ids = []
                            for item in data:
                                count += 1

                                account_id = item.get('id', '')
                                token_code = item.get('access_token', '')
                                category = item.get('category', '')
                                name = item.get('name', '')
                                picture = item.get('picture', None)
                                link = item.get('link', None)

                                account_obj, created = MessengerPageToken.objects.get_or_create(
                                    tenant=self.token_obj.tenant,
                                    company=self.token_obj.company,
                                    parent=self.token_obj,
                                    account_id=account_id,
                                    defaults={
                                        'token': token_code,
                                        'category': category,
                                        'name': name,
                                        'picture': picture,
                                        'link': link,
                                    }
                                )
                                if created is False:
                                    account_obj.token = token_code
                                    account_obj.category = category
                                    account_obj.name = name
                                    account_obj.picture = picture
                                    account_obj.link = link
                                    account_obj.save()
                                keep_account_ids.append(str(account_id))

                    # clear account
                    accounts = MessengerPageToken.objects.filter(
                        parent=self.token_obj
                    )
                    if isinstance(keep_account_ids, list):
                        accounts = accounts.exclude(account_id__in=keep_account_ids)
                    if accounts:
                        accounts.delete()

                    self.token_obj.is_sync_accounts = True
                self.token_obj.is_syncing = False
                self.token_obj.save(update_fields=['is_syncing', 'is_sync_accounts'])
        return count


class GraphFbApi(GraphAbstract):
    page_obj = MessengerPageToken

    def __init__(self, page_obj: MessengerPageToken, **kwargs):
        self.page_obj = page_obj
        self._url = ''
        super().__init__(**kwargs)

    @property
    def params(self):
        return {
            'access_token': self.page_obj.token
        }

    def get_profile(self, account_id):
        full_url = self.url + '/' + account_id
        response = call_graph_api(
            company_id=self.page_obj.company_id,
            method='get',
            url=full_url,
            params={
                **self.params,

            },
        )
        if response:
            if response.status_code == 200:
                return response.json()
        return None

    def conversations(self):
        full_url = self.url + f'/{self.page_obj.account_id}/conversations'
        response = call_graph_api(
            company_id=self.page_obj.company_id,
            method='get',
            url=full_url,
        )
        if response:
            return response.json()
        return {}
