"""
This module manually runs the test cases defined in TestHybridServerlessDB,
providing detailed logging for each test's execution and results.
"""

from _cnu.hybrid_serverless_db.db_api import DatabaseAPI
from _cnu.hybrid_serverless_db.tests.test_db import TestHybridServerlessDB


def main():
    """
    Manually executes each test case in the TestHybridServerlessDB class.
    This function iterates through the test methods, calling setUp before
    each test, executing the test method, and calling tearDown afterwards.
    It provides detailed logging for the start, end, success, or failure of
    each test.
    """
    test_suite = TestHybridServerlessDB()
    test_methods = [
        method
        for method in dir(TestHybridServerlessDB)
        if method.startswith("test_") and callable(getattr(TestHybridServerlessDB, method)) # Check if is a valid function
    ]

    for method_name in test_methods:
        test_method = getattr(test_suite, method_name)
        print(f"Starting test: {method_name}")
        try:
            print(f"    Calling setUp for {method_name}")
            test_suite.setUp()
            print(f"    setUp completed for {method_name}")
            test_method()
            print(f"Finished test: {method_name}. Test ran successfully.")

        except Exception as e:
            print(f"Error in test {method_name}: {e}")
        finally:
            print(f"    Calling tearDown for {method_name}")
            test_suite.tearDown()
            print(f"    tearDown completed for {method_name}")


if __name__ == "__main__":
    main()