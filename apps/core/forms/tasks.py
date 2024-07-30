import string
import urllib.parse

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.core.forms.models import FormPublished, FormPublishedEntries
from apps.core.mailer.tasks import send_mail_form


@shared_task
def check_and_update_active_publish_form():
    now = timezone.now()
    ids_deactivate = []
    for obj in FormPublished.objects.filter(is_active=True):
        if obj.date_publish_finish and obj.date_publish_finish <= now:
            obj.is_active = False
            obj.save(update_fields=['is_active'])
            ids_deactivate.append(str(obj.id))
    return ids_deactivate


def form_get_creator_email(entry_obj, creator_receiver_from, creator_field) -> str or None:
    if creator_receiver_from == 'authenticated':
        if entry_obj.employee_created:
            return entry_obj.employee_created.email
    if creator_receiver_from == 'field' and creator_field:
        field_data = entry_obj.body_data.get(creator_field, None)
        if field_data and isinstance(field_data, str) and '@' in field_data:
            return field_data
    return None


EMAIL_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title></title>
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            table, th, td {
                border: 1px solid #bfcbd0;
            }
            table tr th {
                background-color: #293372;
                color: #fff;
                padding: 10px;
                border-color: #293372;
            }
            table tr td {
                padding: 5px;
            }
            table tr td:nth-child(1) {
                width: 50%;
            }
            table tr td:nth-child(2) {
                color: #7e7e7e;
            }
        </style>
    </head>
    <body>
        <h1>${companyName}</h1>
        <p>We're grateful for the information you sent.</p>
        ${formSummary}
        <br/>
        ${formData}
        <br/>
        <hr style="border: 0; border-top: 1px solid #7c7c7c;width: 100%;">
        <p>
            IMPORTANT: The contents of this email and any attachments are confidential.
            They are intended for the named recipient(s) only. If you have received this
            email by mistake, please notify the sender immediately and do not disclose
            the contents to anyone or make copies thereof.
        </p>
        <p>This is an automated message. If the reply address is no-reply@*, please do not reply to this email.</p>
        <p>&copy; 2024 BFlow Form. All rights reserved.</p>
    </body>
    </html>
"""


def form_get_summary_data_html(company_sub_domain, publish_obj, entry_obj, create_or_edit):
    def get_text_date_submission():
        if create_or_edit == 'create':
            return 'Created date'
        if create_or_edit == 'edit':
            return 'Modified date'
        return 'Date'

    def get_date_submission():
        if create_or_edit == 'create':
            return entry_obj.date_created.strftime('%d/%m/%Y, %H:%M:%S')
        if create_or_edit == 'edit':
            return entry_obj.date_modified.strftime('%d/%m/%Y, %H:%M:%S')
        return ''

    detail_link = '#'
    form_link = '#'
    # reverse_page = '#'
    # reverse_page = f'{full_domain}{settings.UI_DOMAIN_PATH_REVERSE_PAGE}'

    if settings.UI_DOMAIN_SUFFIX:
        if company_sub_domain and publish_obj.code and settings.UI_DOMAIN_SUFFIX:
            full_domain = f'{settings.UI_DOMAIN_PROTOCOL}://{company_sub_domain}{settings.UI_DOMAIN_SUFFIX}'
            params_detail = urllib.parse.urlencode(
                {
                    'form_code': publish_obj.code,
                    'form_record': str(entry_obj.id),
                }
            )
            detail_link = f'{full_domain}{settings.UI_DOMAIN_PATH_REVERSE}?{params_detail}'

            params_form = urllib.parse.urlencode(
                {
                    'form_code': publish_obj.code
                }
            )
            form_link = f'{full_domain}{settings.UI_DOMAIN_PATH_REVERSE}?{params_form}'

    return f'''
        <table>
            <tr>
                <th colspan="2">Submission</th>
            </tr>
            <tr>
                <td>{get_text_date_submission()}</td>
                <td>{get_date_submission()}</td>
            </tr>
            <tr>
                <td>Form</td>
                <td>{form_link}</td>
            </tr>
            <tr>
                <td>Record</td>
                <td><a href="{detail_link}">{detail_link}</a></td>
            </tr>
        </table>
    '''


def form_get_form_data_to_html(company_sub_domain, publish_obj, entry_obj):  # pylint: disable=W0613,W0613
    return f'''
        <table>
            <tr>
                <th colspan="2">{publish_obj.form.title}</th>
            </tr>
            <tr><td colspan="2">Data only supports live viewing, no preview version.</td></tr>
        </table>
    '''


def form_get_template(data):
    # language
    # title
    data = {
        'companyName': '',
        'formData': '',
        'formSummary': '',
        **data,
    }
    try:
        return string.Template(EMAIL_TEMPLATE).safe_substitute(data)
    except KeyError as err:
        print('form_get_template: keyError:', err)
    return None


@shared_task
def notifications_form_with_new(entry_id):
    try:
        entry_obj = FormPublishedEntries.objects.get(pk=entry_id)
    except FormPublishedEntries.DoesNotExist:
        raise ValueError(f'Form Entry not found: {entry_id}')

    publish_obj = entry_obj.published
    if publish_obj:
        company_obj = getattr(publish_obj, 'company', None)
        notifications = publish_obj.notifications
        if notifications and isinstance(notifications, dict) and company_obj:
            creator_enable_new = notifications.get('user_management_enable_new', False)
            creator_receiver_from = notifications.get('creator_receiver_from', False)
            creator_field = notifications.get('creator_field', False)
            creator_email = form_get_creator_email(
                entry_obj, creator_receiver_from=creator_receiver_from, creator_field=creator_field
            )

            user_management_enable_new = notifications.get('user_management_enable_new', False)
            user_management_destination = notifications.get('user_management_destination', False)

            subject = 'Thank you for providing the information.'
            template_filled = form_get_template(
                {
                    'companyName': publish_obj.company.title if publish_obj.company else 'BFlow',
                    'formData': form_get_form_data_to_html(
                        company_sub_domain=company_obj.sub_domain,
                        publish_obj=publish_obj,
                        entry_obj=entry_obj
                    ),
                    'formSummary': form_get_summary_data_html(
                        company_sub_domain=company_obj.sub_domain,
                        publish_obj=publish_obj,
                        entry_obj=entry_obj,
                        create_or_edit='create',
                    ),
                }
            )

            state_management = False
            state_creator = False

            if user_management_enable_new and user_management_destination:
                state_management = send_mail_form(
                    tenant_id=publish_obj.tenant_id,
                    company_id=publish_obj.company_id,
                    subject=subject,
                    to_main=user_management_destination,
                    contents=template_filled,
                )

            if creator_enable_new and creator_email:
                state_creator = send_mail_form(
                    tenant_id=publish_obj.tenant_id,
                    company_id=publish_obj.company_id,
                    subject=subject,
                    to_main=creator_email,
                    contents=template_filled,
                )
            return {
                'management': state_management,
                'creator': state_creator
            }
    raise ValueError(f'Form Published not found from entry: {entry_id}')


@shared_task
def notifications_form_with_change(entry_id):
    try:
        entry_obj = FormPublishedEntries.objects.get(pk=entry_id)
    except FormPublishedEntries.DoesNotExist:
        raise ValueError(f'Form Entry not found: {entry_id}')

    publish_obj = entry_obj.published
    if publish_obj:
        company_obj = getattr(publish_obj, 'company', None)
        notifications = publish_obj.notifications
        if notifications and isinstance(notifications, dict) and company_obj:
            creator_enable_change = notifications.get('user_management_enable_new', False)
            creator_receiver_from = notifications.get('creator_receiver_from', False)
            creator_field = notifications.get('creator_field', False)
            creator_email = form_get_creator_email(
                entry_obj, creator_receiver_from=creator_receiver_from, creator_field=creator_field
            )

            user_management_enable_change = notifications.get('user_management_enable_new', False)
            user_management_destination = notifications.get('user_management_destination', False)

            subject = 'Update received: Your information has been updated.'
            template_filled = form_get_template(
                {
                    'companyName': publish_obj.company.title if publish_obj.company else 'BFlow',
                    'formData': form_get_form_data_to_html(
                        company_sub_domain=company_obj.sub_domain,
                        publish_obj=publish_obj,
                        entry_obj=entry_obj
                    ),
                    'formSummary': form_get_summary_data_html(
                        company_sub_domain=company_obj.sub_domain,
                        publish_obj=publish_obj,
                        entry_obj=entry_obj,
                        create_or_edit='edit',
                    ),
                }
            )

            state_management = False
            state_creator = False
            if user_management_enable_change and user_management_destination:
                state_management = send_mail_form(
                    tenant_id=publish_obj.tenant_id,
                    company_id=publish_obj.company_id,
                    subject=subject,
                    to_main=user_management_destination,
                    contents=template_filled,
                )

            if creator_enable_change and creator_email:
                state_creator = send_mail_form(
                    tenant_id=publish_obj.tenant_id,
                    company_id=publish_obj.company_id,
                    subject=subject,
                    to_main=creator_email,
                    contents=template_filled,
                )
            return {
                'management': state_management,
                'creator': state_creator
            }
    raise ValueError(f'Form Published not found from entry: {entry_id}')
