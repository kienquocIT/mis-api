import os

from rest_framework import serializers
from rest_framework.views import APIView
from openai import OpenAI
import tiktoken

from apps.shared import mask_view, ResponseController


# from apps.core.chatbot.serializers import ChatbotHistorySerializer
# from apps.core.chatbot.models import ChatbotHistory


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)
OPENAI_PROJECT_ID = os.getenv('OPENAI_PROJECT_ID', None)


class ChatbotView(APIView):
    @staticmethod
    def num_tokens_from_string(string: str, encoding_name: str = 'o200k_base') -> int:
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    @mask_view(login_require=True, employee_require=True)
    def get(self, request, *args, **kwargs):
        # chatbots = ChatbotHistory.objects.filter_current(
        #     fill__tenant=True, fill__company=True, employee_inherit_id=request.user.employee_current_id
        # )
        # ser = ChatbotHistorySerializer(instance=chatbots, many=True)
        # return ResponseController.success_200(data=ser.data)
        return ResponseController.success_200(data={})

    @mask_view(login_require=True, employee_require=True)
    def post(self, request, *args, **kwargs):
        if OPENAI_API_KEY:
            data = request.data
            user_input = data.get('message')

            user_input_token_len = self.num_tokens_from_string(string=user_input)
            if user_input_token_len > 100:
                raise serializers.ValidationError({
                    'detail': 'This question is too long',
                })

            # obj = ChatbotHistory.objects.create(
            #     tenant_id=request.user.tenant_current_id,
            #     company_id=request.user.company_current_id,
            #     employee_inherit_id=request.user.employee_current_id,
            #     answer=user_input,
            # )

            client = OpenAI(api_key=OPENAI_API_KEY, project=OPENAI_PROJECT_ID)

            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": user_input,
                    },
                    {
                        "role": "system",
                        "content": "Bflow là Nhà cung cấp hệ thống quản trị doanh nghiệp hợp nhất và toàn diện, "
                                   "giúp doanh nghiệp quản lý và vận hành hiệu quả, thúc đẩy tăng trưởng bền vững.",
                    },
                    {
                        "role": "system",
                        "content": "Bflow có trang chủ website tại https://www.bflow.vn .",
                    },
                    {
                        "role": "system",
                        "content": "Giá dịch vụ sử dụng Bflow cần phải liên hệ để được tư vấn và biết thêm thông tin.",
                    },
                    {
                        "role": "system",
                        "content": "Tầm nhìn của Bflow là Thay đổi văn hóa quản trị của doanh nghiệp Việt: minh "
                                   "bạch, dựa vào dữ liệu để ra quyết định, thông qua việc cung cấp hệ thống "
                                   "quản trị doanh nghiệp hợp nhất và toàn diện.",
                    },
                    {
                        "role": "system",
                        "content": "Sứ mệnh của Bflow là Mang lại giải pháp quản trị doanh nghiệp hợp nhất và "
                                   "toàn diện, hướng tới cải tiến quy trình, tối ưu chi phí và tăng tốc độ "
                                   "chuyển đổi số cho mọi doanh nghiệp.",
                    },
                    {
                        "role": "system",
                        "content": "Trụ sở của Bflow tại 20 Đường số 22 KDC Him Lam, Bình Hưng, Bình Chánh, Thành phố Hồ "
                                   "Chí Minh 70000, Việt Nam.",
                    },
                    {
                        "role": "system",
                        "content": "Thông tin liên hệ của Bflow là email support@bflow.vn và số điện thoại 0903 608 494",
                    },
                ],
                model="gpt-4o-mini",
            )

            # obj.answer = chat_completion.dict()

            return ResponseController.success_200(
                data=chat_completion.dict(),
            )
        raise serializers.ValidationError({
            'detail': 'The chatbot is not ready',
        })
