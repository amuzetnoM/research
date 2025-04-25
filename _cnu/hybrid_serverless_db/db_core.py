import json


class DocumentDatabase:
    """
    A simple document database that stores data in a JSON file.

    Attributes:
        data (dict): The in-memory representation of the database.
        db_file (str): The path to the JSON file where data is stored.
        indexes (dict): A dictionary to store indexes.
    """

    def __init__(self, db_file="database.json"):
        """
        Initializes the DocumentDatabase.

        Args:
            db_file (str): The path to the JSON file for data storage.
        """
        self.db_file = db_file
        self.data = {}
        self.indexes = {}    
        self.load_data()
        self.save_data(self.db_file)

    def load_data(self, db_file):
        """
        Loads data from the JSON file into memory.
        If the file doesn't exist, initializes an empty database.
        
        Args:

        """
        try:
            with open(self.db_file, "r") as f:
                    self.data = json.load(f)
        except json.JSONDecodeError as e:
            self.data = {}
            raise ValueError(f"Error decoding JSON from {db_file}: {e}")
        except Exception as e:
            raise RuntimeError(f"An error occurred while loading data: {e}")

    def save_data(self, db_file):
        """
        Saves the current in-memory data to the JSON file.

        """
        try:
            with open(self.db_file, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            raise RuntimeError(f"An error occurred while saving data: {e}")

    def create_index(self, field):
        """
        Creates an index on a specified field.

        Args:
            field (str): The field to create an index on.

        Raises:
            ValueError: If the field is already indexed.
            ValueError: if the field is not present in the data.
        """
        if field in self.indexes:
            raise ValueError(f"Index already exists for field: {field}")
        
        if not all(field in doc for doc in self.data.values()):
            raise ValueError(f"Field '{field}' is not present in all documents.")

        self.indexes[field] = {}
        for doc_id, doc in self.data.items():
            self.indexes[field].setdefault(doc[field], []).append(doc_id)

    def get_index(self, field):
        """
        Retrieves an index for a given field.

        Args:
            field (str): The field to get the index for.

        Returns:
            dict: The index for the given field.

        Raises:
            ValueError: If no index exists for the specified field.
        """
        if field not in self.indexes:
            raise ValueError(f"No index found for field: {field}")
        return self.indexes[field]

    def delete_index(self, field):
        """
        Deletes the index for a given field.

        Args:
            field (str): The field to delete the index for.

        Raises:
            ValueError: If no index exists for the specified field.
        """
        if field not in self.indexes:
            raise ValueError(f"No index found for field: {field}")
        del self.indexes[field]

    def add_data(self, doc):
        """
        Adds new data to the database.

        Args:
            doc (dict): The document data.

        
        Raises:
            ValueError: If the document ID already exists.
        """
        if doc_id in self.data:
            raise ValueError(f"Document ID '{doc_id}' already exists")

        self.data[doc_id] = doc
        for field in self.indexes:
            self.indexes[field].setdefault(doc[field], []).append(doc_id)
        self.save_data()
        
    def update_data(self, doc_id, doc):
        """
        Updates data in the database.

        Args:
            doc_id (str): The unique ID of the document to update.
            doc (dict): The new document data.

        Raises:
            ValueError: If the document ID does not exist.
        """
        if doc_id not in self.data:
            raise ValueError(f"Document ID '{doc_id}' not found")

        old_doc = self.data[doc_id]
        self.data[doc_id] = doc

        for field in self.indexes:
            if old_doc.get(field) != doc.get(field):
                self.indexes[field][old_doc[field]].remove(doc_id)
                self.indexes[field].setdefault(doc[field], []).append(doc_id)
        self.save_data()

    def delete_data(self, doc_id):
        """
        Deletes data from the database.

        Args:
            doc_id (str): The unique ID of the document to delete.

        Raises:
            ValueError: If the document ID does not exist.
        """
        if doc_id not in self.data:
            raise ValueError(f"Document ID '{doc_id}' not found")

        doc = self.data[doc_id]
        del self.data[doc_id]

        for field in self.indexes:
            if doc[field] in self.indexes[field]:
                self.indexes[field][doc[field]].remove(doc_id)

        self.save_data()

    def get_data(self, doc_id):
        """
        Gets data from the database.

        Args:
            doc_id (str): The unique ID of the document to retrieve.

        Returns:
            dict: The document data.

        Raises:
            ValueError: If the document ID does not exist.
        """
        if doc_id not in self.data:
            raise ValueError(f"Document ID '{doc_id}' not found")
        return self.data[doc_id]

    def create_query(self, index_field, query_value):
        """
        Creates a query using index information.

        Args:
            index_field (str): The field to use for the index.
            query_value: The value to query for.

        Returns:
            list: The list of document IDs that match the query.

        Raises:
            ValueError: If no index exists for the specified field.
        """
        if index_field not in self.indexes:
            raise ValueError(f"No index found for field: {index_field}")
        return self.indexes[index_field].get(query_value, [])

    def query(self, index_field, query_value, query=None):
        """
        Queries the database using an index and an optional filter.

        Args:
            index_field (str): The field to use for the index.
            query_value: The value to query for.
            query (callable, optional): An optional filter function.

        Returns:
            list: The list of documents that match the query.

        Raises:
            ValueError: If no index exists for the specified field.
        """
        doc_ids = self.create_query(index_field, query_value)

        results = []
        for doc_id in doc_ids:
            doc = self.data[doc_id]
            if query is None or query(doc):
                results.append(doc)
        return results