import os
import django
from django.conf import settings
from django.test.utils import get_runner


def main():
    # 1. Set the environment variable for your settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

    # 2. Initialize Django
    django.setup()

    # 3. Get the test runner (defaults to DiscoverRunner)
    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    # 4. Run the tests (pass a list of labels/paths or empty for all)
    failures = test_runner.run_tests(["tests"])

    if failures:
        exit(1)