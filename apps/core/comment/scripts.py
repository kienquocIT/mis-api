import random

from faker import Faker

from .models import Comments


class FakeData:
    def __init__(self, tenant_id, company_id, app_id, doc_id):
        self.faker = Faker('vi_VN')

        self.tenant_id = tenant_id
        self.company_id = company_id
        self.app_id = app_id
        self.doc_id = doc_id

    def _create_comment(self, **kwargs):
        return Comments.objects.create(
            tenant_id=self.tenant_id,
            company_id=self.company_id,
            doc_id=self.doc_id,
            application_id=self.app_id,
            contents=self.faker.text(max_nb_chars=200),
            employee_created_id="442e1a4d1efa45c992cc2f1a7d4a90d2",
            **kwargs
        )

    @classmethod
    def dividers(cls):
        print(
            ' {0: <5}*{1:<40}*{2: <5}*'.format(
                '*' * 5,
                '*' * 40,
                '*' * 5,
            )
        )

    def init(self, counter, child_num_max=0):
        self.dividers()
        for idx in range(counter):
            obj_parent = self._create_comment()
            child_num = 0
            if child_num_max:
                child_num = random.randint(0, child_num_max)
                for idc in range(child_num):
                    self._create_comment(parent_n=obj_parent)
            print(
                '|{0: <5}|{1:<40}|{2: <5}|'.format(
                    str(idx),
                    str(obj_parent.id),
                    str(child_num)
                )
            )
        self.dividers()


def init(counter, child_num_max=0):
    tenant_id = "d362f12dce8348d59f750915380af2e3"
    company_id = "2a9b19cd935b4900bc5d20971d0861e2"
    app_id = "b9650500aba744e3b6e02542622702a3"
    doc_id = "6e4caee4-3cd9-4a3e-a447-e48332e7a878"

    FakeData(tenant_id=tenant_id, company_id=company_id, doc_id=doc_id, app_id=app_id).init(counter, child_num_max)
