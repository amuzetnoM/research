"""
This module contains the test suite for the Hybrid Serverless Database.
It uses the unittest framework to define and run various test cases.
"""
import unittest
import os
import json

from _cnu.hybrid_serverless_db.db_api import DatabaseAPI


class TestHybridServerlessDB(unittest.TestCase):
    """
    Test suite for the Hybrid Serverless Database, testing various functionalities.
    """

    def setUp(self):
        """
        Setup method to be executed before each test case.

        This method initializes the test environment by creating a new DatabaseAPI
        instance, defining absolute paths for the database and registry files,
        and ensuring the database and registry start empty.
        """
        self.db_file = os.path.abspath("test_db.json")
        self.registry_file = os.path.abspath("test_registry.json")

        self.api = DatabaseAPI(self.db_file, self.registry_file)
        # Clear existing data in the registry
        self.api.registry.indexes = {}
        self.api.registry.schema = {}
        self.api.registry.endpoints = {}

        # Save the empty registry to ensure a clean state
        self.api.save_db()

        # clear the existing data in the database.
        self.api.data_db.data = {} 
        self.api.save_db()

    def tearDown(self):
        """
        Teardown after each test case. Removes the test database and registry files.
        """
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
        if os.path.exists(self.registry_file):
            os.remove(self.registry_file)

    def test_initialization(self):
        """
        Test the initialization of the DatabaseAPI.

        Verifies that the DatabaseAPI is correctly initialized and that the
        database and registry files are created and empty.
        """
        self.assertTrue(isinstance(self.api, DatabaseAPI))
        self.assertTrue(os.path.exists(self.db_file))
        self.assertTrue(os.path.exists(self.registry_file))

        with open(self.db_file, "r") as f:
            db_data = json.load(f)
            self.assertEqual(db_data, {})

        with open(self.registry_file, "r") as f:
            reg_data = json.load(f)
            self.assertEqual(reg_data, {"indexes": {}, "schema": {}, "endpoints": {}})

    def test_create_index(self):
        """
        Test creating an index.

        Verifies that an index can be created with the specified name, field, and type.
        """
        self.api.add_index("test_index", "test_field", "hash")
        index_info = self.api.get_indexes()["test_index"]
        self.assertEqual(index_info["field"], "test_field")
        self.assertEqual(index_info["index_type"], "hash")    

    def test_create_schema(self):
        """
        Test creating schema information.
        """
        self.api.registry.add_schema_info("test_field", "string", "Test Field")
        schema_info = self.api.get_schema()["test_field"]
        self.assertEqual(schema_info["data_type"], "string")
        self.assertEqual(schema_info["description"], "Test Field")

    def test_create_endpoint(self):
        """
        Test creating endpoint information.
        """
        self.api.registry.add_endpoint_info("test_endpoint", "Test Endpoint", {"param1": "value1"})
        endpoint_info = self.api.get_endpoints()["test_endpoint"]
        self.assertEqual(endpoint_info["description"], "Test Endpoint")
        self.assertEqual(endpoint_info["parameters"], {"param1": "value1"})

    def test_create_data(self):
        """
        Test adding new data to the database.
        """
        data = {"id": "1", "value": "test"}
        self.api.add_data(data)
        db_data = self.api.data_db.data
        self.assertEqual(len(db_data), 1)
        self.assertEqual(db_data[0], {"id": "1", "value": "test"})

    def test_get_data(self):
        """
        Test getting data from the database.
        """
        data = {"id": "1", "value": "test"}
        self.api.add_data(data)
        retrieved_data = self.api.get_data("1")
        self.assertEqual(retrieved_data, data)

    def test_update_data(self):
        """
        Test updating data in the database.
        """
        data = {"id": "1", "value": "test"}
        self.api.add_data(data)
        updated_data = {"id": "1", "value": "updated"}
        self.api.update_data("1", updated_data)
        retrieved_data = self.api.get_data("1")
        self.assertEqual(retrieved_data, updated_data)

    def test_delete_data(self):
        """
        Test deleting data from the database.
        """
        data = {"id": "1", "value": "test"}
        self.api.add_data(data)
        self.api.delete_data("1")
        retrieved_data = self.api.get_data("1")
        self.assertIsNone(retrieved_data)

    def test_query(self):
        """
        Test querying the database using an index.
        """
        data1 = {"id": "1", "type": "type1", "value": "test1"}
        data2 = {"id": "2", "type": "type2", "value": "test2"}
        self.api.add_data(data1)
        self.api.add_data(data2)
        self.api.add_index("type_index", "type", "hash")
        results = self.api.query("type_index", "type1")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], data1)

    def test_get_registry_data(self):
        """
        Test retrieving all indexes and endpoints from the registry.

        Verifies that all indexes, and endpoints can be retrieved from the registry.
        """
        self.api.add_index("test_index", "test_field", "hash")        
        indexes = self.api.get_indexes()
        schema = self.api.get_schema()
        endpoints = self.api.get_endpoints()
        self.assertIn("test_index", indexes)
        self.assertIn("test_field", schema)
        self.assertIn("test_endpoint", endpoints)

    def test_save_and_load_db(self):
        """Test saving and loading the database and registry."""
        data1 = {"id": "1", "type": "type1", "value": "test1", "category": "category1", "timestamp": 123456}
        data2 = {"id": "2", "type": "type2", "value": "test2", "category": "category2", "timestamp": 654321}
        self.api.add_data(data1)
        self.api.add_data(data2)
        self.api.add_index("type_index", "type", "hash")
        self.api.registry.add_schema_info("id", "string", "Unique identifier")
        self.api.registry.add_schema_info("timestamp", "number", "Document creation time")
        self.api.registry.add_schema_info("type", "string", "Document type")
        self.api.registry.add_schema_info("category", "string", "Document category")

        self.api.registry.add_endpoint_info("test_endpoint", "Test Endpoint", {"param1": "value1"})
        self.api.save_db()

        new_api = DatabaseAPI(self.db_file, self.registry_file)
        new_api.data_db.load_data(self.db_file)
        new_api.registry.load_registry(self.registry_file)
        retrieved_data = new_api.get_data("1")
        self.assertEqual(retrieved_data, data1)
        indexes = new_api.get_indexes()
        schema = new_api.get_schema()
        endpoints = new_api.get_endpoints()
        self.assertIn("type_index", indexes)
        self.assertIn("test_field", schema)
        self.assertIn("test_endpoint", endpoints)

    def test_error_cases(self):
        """
        Test various error cases, such as duplicate indexes or invalid data.
        """
        self.api.add_index("test_index", "test_field", "hash")
        with self.assertRaises(ValueError):
            self.api.add_index("test_index", "other_field", "hash")
        with self.assertRaises(ValueError):
            self.api.query("nonexistent_index", "some_value")


if __name__ == '__main__':
    unittest.main()