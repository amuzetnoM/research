import json
import os

class DatabaseRegistry:
    """
    Manages the registry for database indexes, schema, and API endpoints.
    """

    def __init__(self, registry_file="registry.json"):
        """
        Initializes the DatabaseRegistry.

        Args:
            registry_file (str): The path to the JSON file used for persistence.
        """
        self.registry_file = registry_file
        self.indexes = {}  # Stores metadata about indexes
        self.schema = {}  # Stores metadata about the data schema
        self.endpoints = {}  # Stores metadata about API endpoints
        self.load_registry()

    def load_registry(self):
        """
        Loads the registry from a JSON file.
        """
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    self.indexes = data.get("indexes", {})
                    self.schema = data.get("schema", {})
                    self.endpoints = data.get("endpoints", {})
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in registry file: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while loading the registry: {e}")
        else:
            print(f"Registry file not found, creating a new one at {self.registry_file}")
            self.save_registry()

    def save_registry(self):
        """
        Saves the registry to a JSON file.
        """
        try:
            with open(self.registry_file, 'w') as f:
                json.dump({"indexes": self.indexes, "schema": self.schema, "endpoints": self.endpoints}, f, indent=4)
        except Exception as e:
            print(f"Error saving registry to JSON file: {e}")

    def add_index_info(self, index_name, index_info):
        """
        Adds information about an index.

        Args:
            index_name (str): The name of the index.
            index_info (dict): A dictionary containing metadata about the index.

        Raises:
            ValueError: If index_name already exists
            TypeError: If index_info is not a dict
        """
        if not isinstance(index_info, dict):
            raise TypeError("index_info must be a dictionary")
        if index_name in self.indexes:
            raise ValueError(f"Index '{index_name}' already exists")
        self.indexes[index_name] = index_info
        self.save_registry()

    def get_index_info(self, index_name):
        """
        Retrieves information about an index.

        Args:
            index_name (str): The name of the index.

        Returns:
            dict: A dictionary containing the index metadata, or None if not found.
        """
        return self.indexes.get(index_name)

    def delete_index_info(self, index_name):
        """
        Deletes information about an index.

        Args:
            index_name (str): The name of the index.

        Raises:
            ValueError: If index_name does not exists
        """
        if index_name not in self.indexes:
            raise ValueError(f"Index '{index_name}' does not exists")
        if index_name in self.indexes:
            del self.indexes[index_name]
            self.save_registry()

    def add_schema_info(self, schema_name, schema_info):
        """
        Adds schema information.

        Args:
            schema_name (str): The name of the schema.
            schema_info (dict): A dictionary containing the schema metadata.

        Raises:
            ValueError: If schema_name already exists
            TypeError: If schema_info is not a dict
        """
        if not isinstance(schema_info, dict):
            raise TypeError("schema_info must be a dictionary")
        if schema_name in self.schema:
            raise ValueError(f"Schema '{schema_name}' already exists")
        self.schema[schema_name] = schema_info
        self.save_registry()

    def get_schema_info(self, schema_name):
        """
        Retrieves schema information.

        Args:
            schema_name (str): The name of the schema.

        Returns:
            dict: A dictionary containing the schema metadata, or None if not found.
        """
        return self.schema.get(schema_name)

    def delete_schema_info(self, schema_name):
        """
        Deletes schema information.

        Args:
            schema_name (str): The name of the schema.

        Raises:
            ValueError: If schema_name does not exists
        """
        if schema_name not in self.schema:
            raise ValueError(f"Schema '{schema_name}' does not exists")
        if schema_name in self.schema:
            del self.schema[schema_name]
            self.save_registry()

    def add_endpoint_info(self, endpoint_name, endpoint_info):
        """
        Adds API endpoint information.

        Args:
            endpoint_name (str): The name of the API endpoint.
            endpoint_info (dict): A dictionary containing the endpoint metadata.

        Raises:
            ValueError: If endpoint_name already exists
            TypeError: If endpoint_info is not a dict
        """
        if not isinstance(endpoint_info, dict):
            raise TypeError("endpoint_info must be a dictionary")
        if endpoint_name in self.endpoints:
            raise ValueError(f"Endpoint '{endpoint_name}' already exists")
        self.endpoints[endpoint_name] = endpoint_info
        self.save_registry()

    def get_endpoint_info(self, endpoint_name):
        """
        Retrieves API endpoint information.

        Args:
            endpoint_name (str): The name of the API endpoint.

        Returns:
            dict: A dictionary containing the endpoint metadata, or None if not found.
        """
        return self.endpoints.get(endpoint_name)

    def delete_endpoint_info(self, endpoint_name):
        """
        Deletes API endpoint information.

        Args:
            endpoint_name (str): The name of the API endpoint.

        Raises:
            ValueError: If endpoint_name does not exists
        """
        if endpoint_name not in self.endpoints:
            raise ValueError(f"Endpoint '{endpoint_name}' does not exists")
        if endpoint_name in self.endpoints:
            del self.endpoints[endpoint_name]
            self.save_registry()