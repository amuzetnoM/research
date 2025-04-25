from typing import Any, Dict, List, Optional, Union

from _cnu.hybrid_serverless_db.db_core import DocumentDatabase
from _cnu.hybrid_serverless_db.db_registry import DatabaseRegistry


class DatabaseAPI:
    """
    DatabaseAPI class to handle the database API.
    """

    def __init__(self, db_file: str, registry_file: str):
        """
        Initializes the DatabaseAPI, DocumentDatabase, and DatabaseRegistry.

        This method initializes the DocumentDatabase and DatabaseRegistry, which
        will load the data and registry from their respective files.
        Initializes the DatabaseAPI.

        Args:
            data_db: An instance of the DocumentDatabase class.
            registry: An instance of the DatabaseRegistry class.
        """
        self.data_db = data_db
        self.registry = DatabaseRegistry(registry_file)
        self.data_db = DocumentDatabase(db_file)
    
    def save_db(self) -> None:
        self.data_db.save_data()
        self.registry.save_registry()

    def add_index(self, index_name: str, field: str, index_type: str = "hash") -> None:
        """
        Adds an index.

        Args:
            index_name: The name of the index.
            field: The field to index.
            index_type: The type of index to create.

        Raises:
            ValueError: If the index type is invalid or the index already exists.
        """
        if index_type not in ["hash"]:
            raise ValueError(f"Invalid index type: {index_type}")

        if index_name in self.registry.indexes:
            raise ValueError(f"Index '{index_name}' already exists")
        self.data_db.create_index(field, index_type)
        self.registry.add_index_info(index_name, field, index_type)

    def get_index(self, index_name: str) -> Dict[str, Any]:
        """
        Gets an index.

        Args:
            index_name: The name of the index.

        Returns:
            A dictionary containing index information.

        Raises:
            ValueError: If the index is not found.
        """
        index_info = self.registry.get_index_info(index_name)
        if not index_info:
            raise ValueError(f"Index '{index_name}' not found")
        return index_info

    def delete_index(self, index_name: str) -> None:
        """
        Deletes an index.

        Args:
            index_name: The name of the index to delete.

        Raises:
            ValueError: If the index is not found.
        """
        index_info = self.registry.get_index_info(index_name)
        if not index_info:
            raise ValueError(f"Index '{index_name}' not found")
        self.data_db.delete_index(index_info["field"])
        self.registry.delete_index_info(index_name)

    def add_data(self, data: Dict[str, Any]) -> None:
        """
        Adds new data to the database.

        Args:
            data: The data to add.

        Raises:
            ValueError: If the data is invalid.
        """
        if not isinstance(data, dict):
            raise ValueError(f"Invalid data: {data}")

        self.data_db.add_data(data)

    def update_data(self, data_id: Any, new_data: Dict[str, Any]) -> None:
        """
        Updates existing data.

        Args:
            data_id: The ID of the data to update.
            new_data: The new data.

        Raises:
            ValueError: If the data or data_id is invalid.
        """
        if not isinstance(new_data, dict):
            raise ValueError("Invalid data format for updating")
        
        self.data_db.update_data(data_id, new_data)

    def delete_data(self, data_id: Any) -> None:
        """
        Deletes data.

        Args:
            data_id: The ID of the data to delete.

        Raises:
            ValueError: If the data_id is invalid.
        """
        if data_id is None:
            raise ValueError("Invalid data_id for deletion")
        self.data_db.delete_data(data_id)

    def get_data(self, data_id: Any) -> Optional[Dict[str, Any]]:
        """
        Gets data by ID.

        Args:
            data_id: The ID of the data to get.

        Returns:
            The data if found, otherwise None.

        Raises:
            ValueError: If the data_id is invalid.
        """
        if data_id is None:
            raise ValueError("Invalid data_id for get")
        return self.data_db.get_data(data_id)

    def query(self, index_name: str, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Queries data using an index and optional query.

        Args:
            index_name: The name of the index to use.
            query: The query to use.

        Returns:
            A list of data matching the query.

        Raises:
            ValueError: If the index is not found.
        """
        index_info = self.registry.get_index_info(index_name)
        if not index_info:
            raise ValueError(f"Index '{index_name}' not found")
        
        return self.data_db.query(index_info["field"], query)
    
    def get_indexes(self) -> Dict[str, Any]:
        """
        Gets all index information from the registry.

        Returns:
            A dictionary containing all index information.
        """
        return self.registry.indexes

    def get_schema(self) -> Dict[str, Any]:
        """
        Gets all schema information from the registry.

        Returns:
            A dictionary containing all schema information.
        """
        return self.registry.schema

    def get_endpoints(self) -> Dict[str, Any]:
        """
        Gets all endpoints information from the registry.

        Returns:
            A dictionary containing all endpoints information.
        """
        return self.registry.endpoints