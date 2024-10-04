__all__ = [
    'MailLogController',
]

from uuid import UUID

from django.db import models

from apps.core.mailer.models import MailLog, MailLogData, MailLogEmployeeTo, MailLogEmployeeCC, MailLogEmployeeBCC


class MailLogController:  # pylint: disable=R0902
    def __init__(
            self,
            tenant_id: UUID = None, company_id: UUID = None,
            application_id: UUID = None, doc_id: UUID = None, system_code: int = 0,
            subject: str = '',
            commit: bool = False,
            **kwargs
    ):
        self.tenant_id = tenant_id
        self.company_id = company_id
        self.application_id = application_id
        self.doc_id = doc_id
        self.system_code = system_code
        self.subject = subject
        self.commit = commit
        self.kwargs = kwargs

        self._obj: MailLog or None = None
        self._log_data: MailLogData or None = None
        self._employee_to: list[MailLogEmployeeTo] = []
        self._address_to: list = []
        self._employee_cc: list[MailLogEmployeeCC] = []
        self._address_cc: list = []
        self._employee_bcc: list[MailLogEmployeeBCC] = []
        self._address_bcc: list = []

    @property
    def obj(self):
        return self._obj

    @obj.setter
    def obj(self, value: MailLog):
        self._obj = value

    @property
    def log_data(self):
        return self._log_data

    @log_data.setter
    def log_data(self, value: MailLogData):
        self._log_data = value

    @property
    def employee_to(self):
        return self._employee_to

    @employee_to.setter
    def employee_to(self, value: MailLogEmployeeTo):
        self._employee_to.append(value)

    @property
    def address_to(self):
        return self._address_to

    @address_to.setter
    def address_to(self, value: list[str] or str):
        if isinstance(value, str) and '@' in value:
            self._address_to.append(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str) and '@' in item:
                    self._address_to.append(item)

    @property
    def employee_cc(self):
        return self._employee_cc

    @employee_cc.setter
    def employee_cc(self, value: MailLogEmployeeCC):
        self._employee_cc.append(value)

    @property
    def address_cc(self):
        return self._address_cc

    @address_cc.setter
    def address_cc(self, value: list or str):
        if isinstance(value, str) and '@' in value:
            self._address_cc.append(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str) and '@' in item:
                    self._address_cc.append(item)

    @property
    def employee_bcc(self):
        return self._employee_bcc

    @employee_bcc.setter
    def employee_bcc(self, value: MailLogEmployeeBCC):
        self._employee_bcc.append(value)

    @property
    def address_bcc(self):
        return self._address_bcc

    @address_bcc.setter
    def address_bcc(self, value: list or str):
        if isinstance(value, str) and '@' in value:
            self._address_bcc.append(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str) and '@' in item:
                    self._address_bcc.append(item)

    def create(
            self,
            commit: bool = True,
            **kwargs
    ):
        self.obj = MailLog(
            tenant_id=self.tenant_id,
            company_id=self.company_id,
            application_id=self.application_id,
            doc_id=self.doc_id,
            system_code=self.system_code,
            subject=self.subject,
        )

        if commit is True or (commit is None and self.commit is True):
            self.save()
        return self.obj

    def update_employee_to(self, employee_to, address_to_init: list = None):
        if not address_to_init:
            address_to_init = []

        for item in employee_to:
            obj_employee_to = None
            if isinstance(item, UUID):
                obj_employee_to = MailLogEmployeeTo(company_id=self.company_id, mail_log=self.obj, employee_id=item)
            elif isinstance(item, models.Model):
                obj_employee_to = MailLogEmployeeTo(company_id=self.company_id, mail_log=self.obj, employee=item)
            else:
                print('[MailLogController] Skip employee_to: ', item)
            if obj_employee_to:
                if obj_employee_to.employee.email:
                    address_to_init.append(obj_employee_to.employee.email)
                self.employee_to = obj_employee_to
        if address_to_init:
            self.address_to = address_to_init
        return self.employee_to

    def update_employee_cc(self, employee_cc, address_cc_init: list = None):
        if not address_cc_init:
            address_cc_init = []

        for item in employee_cc:
            obj_employee_cc = None
            if isinstance(item, UUID):
                obj_employee_cc = MailLogEmployeeCC(company_id=self.company_id, mail_log=self.obj, employee_id=item)
            elif isinstance(item, models.Model):
                obj_employee_cc = MailLogEmployeeCC(company_id=self.company_id, mail_log=self.obj, employee=item)
            else:
                print('[MailLogController] Skip employee_cc: ', item)
            if obj_employee_cc:
                if obj_employee_cc.employee.email:
                    address_cc_init.append(obj_employee_cc.employee.email)
                self.employee_cc = obj_employee_cc
        if address_cc_init:
            self.address_cc = address_cc_init
        return self.employee_cc

    def update_employee_bcc(self, employee_bcc, address_bcc_init: list = None):
        if not address_bcc_init:
            address_bcc_init = []

        for item in employee_bcc:
            obj_employee_bcc = None
            if isinstance(item, UUID):
                obj_employee_bcc = MailLogEmployeeBCC(company_id=self.company_id, mail_log=self.obj, employee_id=item)
            elif isinstance(item, models.Model):
                obj_employee_bcc = MailLogEmployeeBCC(company_id=self.company_id, mail_log=self.obj, employee=item)
            else:
                print('[MailLogController] Skip employee_cc: ', item)
            if obj_employee_bcc:
                if obj_employee_bcc.employee.email:
                    address_bcc_init.append(obj_employee_bcc.employee.email)
                self.employee_bcc = obj_employee_bcc
        if address_bcc_init:
            self.address_bcc = address_bcc_init
        return self.employee_bcc

    def update_log_data(self, **kwargs):
        if not self.log_data:
            self.log_data = MailLogData(log=self.obj)
        for key, value in kwargs.items():
            setattr(self.log_data, key, value)
        return self.log_data

    def update(
            self,
            commit: bool = True,
            **kwargs
    ):
        for key, value in kwargs.items():
            setattr(self._obj, key, value)
        if commit is True or (commit is None and self.commit is True):
            self.save()
        return self.obj

    def save(self, **kwargs):
        if self.obj:
            self.obj.address_to = self.address_to
            self.obj.address_cc = self.address_cc
            self.obj.address_bcc = self.address_bcc
            self.obj.save(**kwargs)
            for obj in self.employee_to:
                obj.save()
            for obj in self.employee_cc:
                obj.save()
            for obj in self.employee_bcc:
                obj.save()
            # skip log_data until confirm key data will be saved log.
            # if self.log_data:
            #     self.log_data.save()
        return self.obj
