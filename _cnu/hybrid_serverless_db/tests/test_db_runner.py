import unittest
from _cnu.hybrid_serverless_db.tests.test_db import TestHybridServerlessDB


def main():
    """
    Runs all test cases in the TestHybridServerlessDB class, one by one.
    """
    test_suite = TestHybridServerlessDB()
    test_methods = [
        method for method in dir(TestHybridServerlessDB) if method.startswith("test_")
    ]

    for method_name in test_methods:
        test_method = getattr(test_suite, method_name)
        print(f"Starting test: {method_name}")
        try:
            # Setup before the test
            test_suite.setUp()
            test_method()
            print(f"Finished test: {method_name}")
        except Exception as e:
            print(f"Error in test {method_name}: {e}")
        finally:
            # Teardown after the test
            test_suite.tearDown()


if __name__ == "__main__":
    main()