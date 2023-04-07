from django.test.runner import DiscoverRunner
from django.core.management import call_command


class CustomTestRunner(DiscoverRunner):
    """
    Override for customize some step with override runner in settings by variable:
        TEST_RUNNER = 'misapi.testrunner.CustomTestRunner'
    Active by command: python manage.py test
    """

    def setup_test_environment(self):
        super().setup_test_environment()
        call_command('migrate')

    def setup_databases(self, **kwargs):
        """
        Step 1: Get parent setup_database (called migrate in parent) => push to _db
        Step 2: Customize data in here | init data
        Step 3: Return _db
        """
        _db = super().setup_databases(**kwargs)
        call_command('init_data')
        return _db

    def teardown_test_environment(self):
        # Your code to teardown the test environment
        super().teardown_test_environment()
