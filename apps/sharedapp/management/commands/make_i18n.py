import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

po_content = '''# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2023-06-05 00:08+0700\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"Language: \\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=1; plural=0;\\n"

#
'''


class Command(BaseCommand):
    help = 'Kiểm tra xem một ứng dụng có tồn tại không và tạo một thư mục locale nếu có'

    def add_arguments(self, parser):
        parser.add_argument('app_path', type=str, help='Đường dẫn đến ứng dụng')
        parser.add_argument('--file_name', dest='file_name', type=str, default='django.po')

    def handle(self, *args, **kwargs):
        app_label = kwargs['app_path']
        file_name = kwargs['file_name']
        self.stdout.write(self.style.SUCCESS(f'Processing: {app_label} → {file_name}'))

        app_path = app_label.replace('.', '/')

        if app_label not in settings.INSTALLED_APPS:
            raise CommandError(f'Ứng dụng {app_label} không có trong INSTALLED_APPS')

        if not os.path.exists(app_path):
            raise CommandError(f'Thư mục {app_path} không tồn tại')

        locale_dir = os.path.join(app_path, 'locale/vi/LC_MESSAGES')
        os.makedirs(locale_dir, exist_ok=True)

        file_dir = os.path.join(locale_dir, file_name)
        if not os.path.isfile(file_dir):
            self.stdout.write(self.style.SUCCESS(f'Đang thực hiện tại file tạo file *.po: {file_dir}'))
            with open(file_dir, 'w') as f:
                f.write(po_content)
            self.stdout.write(self.style.SUCCESS(f'Đã tạo thành công thư mục locale trong {app_label}'))
        else:
            self.stdout.write(self.style.ERROR(f'Đã tồn tại file *.po: {app_label}'))
