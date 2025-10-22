class CompanyHandler:

    @classmethod
    def get_currency_rule(cls, company):
        currency_rule = {}
        if company:
            company_config = company.config
            if company_config:
                currency_rule = company_config.currency_rule
        return currency_rule

    @classmethod
    def round_by_company_config(cls, company, value):
        round_num = int(CompanyHandler.get_currency_rule(company=company).get('precision', '0'))
        return round(value, round_num) if round_num or round_num == 0 else value

    @classmethod
    def exchange_to_company_currency(cls, obj, value):
        if obj.is_currency_exchange is True and obj.currency_exchange_id:
            value = value * obj.currency_exchange_rate
        return value

    @classmethod
    def parse_currency(cls, obj, value):
        currency_rule = CompanyHandler.get_currency_rule(company=obj.company)
        prefix = currency_rule.get('prefix', '').replace(' ', '')
        suffix = currency_rule.get('suffix', '').replace(' ', '')
        precision = int(currency_rule.get('precision', 0))
        thousands = currency_rule.get('thousands', ',')
        decimal = currency_rule.get('decimal', '.')
        allow_negative = currency_rule.get('allowNegative', True)

        if hasattr(obj, 'currency_exchange_id'):
            if obj.currency_exchange_id:
                exchange = obj.currency_exchange_data.get('abbreviation', '')
                prefix = exchange if prefix else ''
                suffix = exchange if suffix else ''
        if not allow_negative and value < 0:
            value = abs(value)
        if float(value).is_integer():
            formatted = f"{int(value):,}"
        else:
            formatted = f"{value:,.{precision}f}"
        formatted = formatted.replace(',', 'TEMP')  # giữ chỗ
        formatted = formatted.replace('.', decimal)  # đổi dấu thập phân
        formatted = formatted.replace('TEMP', thousands)  # đổi dấu phần nghìn
        return f"{prefix}{formatted}{(' ' + suffix) if suffix else ''}"
