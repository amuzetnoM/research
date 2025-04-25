"""
This module initializes the hybrid serverless database, setting up the database file, 
registry file, initial indexes, schemas, endpoints, and sample data.
"""
import random
import string
import time

from _cnu.hybrid_serverless_db.db_api import DatabaseAPI


def initialize_database():
    """
    Initializes the database with initial indexes, schema, endpoints, and sample data.

    This function creates a new database file and registry file if they don't exist,
    sets up initial indexes, schemas, and API endpoints, and adds some sample data.
    It then saves the database and registry to their respective files.
    """
    db_file = "/_cnu/hybrid_serverless_db/db.json"
    registry_file = "/_cnu/hybrid_serverless_db/registry.json"

    db_api = DatabaseAPI(db_file, registry_file)
    
    # Define initial indexes
    initial_indexes = [
        {"name": "id", "field": "id", "index_type": "hash", "description": "Unique identifier"},
        {"name": "timestamp", "field": "timestamp", "index_type": "b-tree", "description": "Document creation time"},
        {"name": "type", "field": "type", "index_type": "hash", "description": "Document type"},
        {"name": "category", "field": "category", "index_type": "hash", "description": "Document category"},
    ]

    # Define initial schema
    initial_schema = [
        {"field": "id", "data_type": "string", "description": "Unique identifier"},
        {"field": "timestamp", "data_type": "number", "description": "Document creation time"},
        {"field": "type", "data_type": "string", "description": "Document type"},
        {"field": "category", "data_type": "string", "description": "Document category"},
    ]

    # Define initial endpoints
    initial_endpoints = [
        {"name": "add_data", "description": "Add a new document", "parameters": ["data"]},
        {"name": "update_data", "description": "Update an existing document", "parameters": ["doc_id", "updated_data"]},
        {"name": "delete_data", "description": "Delete a document", "parameters": ["doc_id"]},
        {"name": "get_data", "description": "Get a document", "parameters": ["doc_id"]},
    ]

    # Create indexes, schema and endpoints
    for index in initial_indexes:
        db_api.add_index(**index)
    for schema in initial_schema:
        db_api.registry.add_schema_info(**schema)
    for endpoint in initial_endpoints:
        db_api.registry.add_endpoint_info(**endpoint)

    # Add some initial data
    for _ in range(5):
        sample_data = {
            "id": ''.join(random.choices(string.ascii_lowercase, k=10)),
            "timestamp": time.time(),
            "type": random.choice(["event", "log", "record"]),
            "category": random.choice(["system", "user", "network"]),
        }
        db_api.add_data(sample_data)

    # Save the database and registry
    db_api.save_db()


if __name__ == "__main__":
    initialize_database()