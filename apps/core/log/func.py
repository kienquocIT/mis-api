# from typing import Union
# from uuid import UUID
#
# from django.utils import timezone
#
# from apps.shared import TypeCheck
# from .models import LengthyProcessLog
#
#
# class ProcessLog:
#     @classmethod
#     def get_or_create_log(cls, defaults: dict = dict, **kwargs):
#         obj, _created = LengthyProcessLog.objects.get_or_create(**kwargs, defaults=defaults)
#         return obj
#
#     def __init__(
#             self, log_id: Union[UUID, str] = None,
#             doc_id_following: Union[UUID, str] = None,
#             total_stage: int = 0,
#             total_step: int = 0,
#     ):
#         # setup
#         get_kwargs = {}
#         if log_id and TypeCheck.check_uuid(log_id):
#             get_kwargs['id'] = log_id
#         elif doc_id_following and TypeCheck.check_uuid(doc_id_following):
#             get_kwargs['doc_id_following'] = doc_id_following
#         else:
#             raise AttributeError('The ProcessLog must be required log_id or doc_id_following arguments')
#
#         # get or create obj log
#         self.obj = self.get_or_create_log(
#             **get_kwargs,
#             defaults={'total_stage': total_stage, 'total_step': 'total_step'},
#         )
#
#     def push_stage_and_step(
#             self, number_of_stage: int = None, number_of_step: int = None, is_finish: bool = None
#     ) -> bool:
#         update_fields = []
#         # stage
#         if number_of_stage is not None:
#             self.obj.current_stage = number_of_stage
#             update_fields += ['current_stage']
#
#         # step
#         if number_of_step is not None:
#             self.obj.current_step = number_of_step
#             update_fields += ['current_step']
#
#         # finish
#         if is_finish is not None:
#             self.obj.is_finish = is_finish
#             self.obj.date_finish = timezone.now()
#             update_fields += ['is_finish', 'date_finish']
#
#         # force save
#         if len(update_fields) > 0:
#             self.obj.save()  # (update_fields=update_fields)
#             return True
#         return False
#
#     def push_errors(self, msg: str) -> bool:
#         self.obj.is_errors = True
#         self.obj.errors = {'datetime': str(timezone.now()), 'msg': str(msg)}
#         self.obj.save()
#         return True
