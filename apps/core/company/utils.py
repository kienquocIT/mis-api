class CompanyHandler:

    @classmethod
    def round_by_company_config(cls, company, value):
        round_num = None
        if company:
            company_config = company.config
            if company_config:
                round_num = int(company_config.currency_rule.get('precision', '0'))
        return round(value, round_num) if round_num or round_num == 0 else value
