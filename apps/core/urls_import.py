from django.urls import path

from apps.core.account.views_import import CoreAccountUserImport
from apps.core.hr.views.fimport import (
    GroupLevelImport, GroupImport, RoleImport, EmployeeImport,
)
from apps.masterdata.saledata.views.fimport import (
    SalutationImport, ContactImport, CurrencyImport,
    AccountGroupImport,
    AccountTypeImport, IndustryImport, PaymentTermImport,
    AccountImport,
)

urlpatterns = [
    # core
    path('core/account/user', CoreAccountUserImport.as_view(), name='CoreAccountUserImport'),
    # hr
    path('hr/group-level', GroupLevelImport.as_view(), name='GroupLevelImport'),
    path('hr/group', GroupImport.as_view(), name='GroupImport'),
    path('hr/role', RoleImport.as_view(), name='RoleImport'),
    path('hr/employee', EmployeeImport.as_view(), name='EmployeeImport'),
    # sale data
    path('saledata/currency', CurrencyImport.as_view(), name='CurrencyImport'),
    path('saledata/account/group', AccountGroupImport.as_view(), name='AccountGroupImport'),
    path('saledata/account/type', AccountTypeImport.as_view(), name='AccountTypeImport'),
    path('saledata/industry', IndustryImport.as_view(), name='IndustryImport'),
    path('saledata/payment-term', PaymentTermImport.as_view(), name='PaymentTermImport'),
    path('saledata/salutation', SalutationImport.as_view(), name='SalutationImport'),
    path('saledata/contact', ContactImport.as_view(), name='ContactImport'),
    path('saledata/account', AccountImport.as_view(), name='AccountImport'),
]
