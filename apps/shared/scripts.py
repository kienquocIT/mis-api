from apps.core.company.models import CompanyUserEmployee


def update_company_created_user():
    company_user_emp = CompanyUserEmployee.object_normal.filter(user__isnull=False)
    if company_user_emp:
        for item in company_user_emp:
            item.is_created_company = True
            item.save()
    print('update done.')
    return True
