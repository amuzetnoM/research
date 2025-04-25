# Hybrid Serverless Database: Documentation

## Introduction

This document provides comprehensive documentation for the Hybrid Serverless Database, a custom-built, single-document database system designed for flexibility, efficiency, and self-describability. This database is particularly well-suited for scenarios where a NoSQL approach with dynamic indexing is preferred, such as in our research project focused on advanced AI, self-awareness, and emergent behavior.

## What is the Hybrid Serverless Database?

The Hybrid Serverless Database is a custom-built, single-document database system. Instead of relying on traditional relational database structures, it stores data in a flexible, schema-on-read format (like JSON documents). It is "hybrid" because, while it operates like a NoSQL database, it also incorporates features found in relational databases, like indexing. It is "serverless" in that it does not require a separate database server process; the entire database resides in files and memory that can be accessed directly by your application.

## Why Was It Created?

We created this database for several reasons:

1.  **Flexibility:** Our research project often involves rapidly evolving data structures. Traditional relational databases require predefined schemas, which can become restrictive. The Hybrid Serverless Database allows us to adapt to changing needs without constant schema migrations.
2.  **Dynamic Indexing:** Our queries are diverse, and the ability to create new indexes on-the-fly is critical for optimizing performance.
3.  **Self-Describing:** We wanted a system where the data structure, indexes, and API endpoints could be queried to understand the current state of the database. This is crucial for complex systems where components need to discover and interact with each other.
4.  **Simplicity:** For research and rapid prototyping, a serverless, single-file approach is more straightforward than setting up and managing a separate database server.
5. **Performance**: Our use case requires high performance, and a system tailor-made to fit can help us achieve this.
6. **Integration**: Since we created the database, we can implement any kind of function to be used on the data.

## Design Choices

1.  **Single Document:** Data is stored in a single JSON file (or similar format). Each record is a document (dictionary in Python).
2.  **In-Memory Indexing:** Indexes are primarily maintained in memory for speed. They can be persisted to disk for recovery.
3.  **Registry System:** A registry stores metadata about indexes, schemas, and API endpoints, making the database self-describing.
4.  **Python-Based:** Python is our primary language for this project, and it's a great fit for a database like this.

## Core Principles

1.  **Flexibility:** Adapt to changing data and query needs.
2.  **Efficiency:** Optimize for speed and efficient resource use.
3.  **Self-Describability:** Provide metadata to understand the database's state.
4.  **Simplicity:** Be easy to set up and use.
5. **Integration:** Fit seamlessly into the projects structure and requirements.

## Structure

The database is divided into these main components:

1.  **`db_core.py`:**
    *   **`DocumentDatabase` Class:**
        *   `data`: Stores the actual document data.
        *   `load_data()`: Loads data from a JSON file.
        *   `save_data()`: Saves data to a JSON file.
        *   `create_index(index_name, field)`: Creates an index on a field.
        *   `get_index(index_name)`: Gets an index.
        *   `delete_index(index_name)`: Deletes an index.
        *   `add_data(data)`: Adds new data.
        *   `update_data(doc_id, updated_data)`: Updates data.
        *   `delete_data(doc_id)`: Deletes data.
        *   `get_data(doc_id)`: Gets data.
        *   `query(index_name, query=None)`: Queries the database.
        * `create_query(index_name, query)`: Creates the query.
2.  **`db_registry.py`:**
    *   **`DatabaseRegistry` Class:**
        *   `indexes`: Stores index metadata.
        *   `schema`: Stores data schema metadata.
        *   `endpoints`: Stores API endpoint metadata.
        *   `load_registry()`: Loads the registry from a JSON file.
        *   `save_registry()`: Saves the registry to a JSON file.
        *   `add_index_info(index_name, field, index_type, description)`: Adds index metadata.
        *   `get_index_info(index_name)`: Retrieves index metadata.
        *   `delete_index_info(index_name)`: Deletes index metadata.
        *   `add_schema_info(field, data_type, description)`: Adds schema metadata.
        *   `get_schema_info(field)`: Retrieves schema metadata.
        *   `delete_schema_info(field)`: Deletes schema metadata.
        *   `add_endpoint_info(endpoint_name, description, parameters)`: Adds endpoint metadata.
        *   `get_endpoint_info(endpoint_name)`: Retrieves endpoint metadata.
        *   `delete_endpoint_info(endpoint_name)`: Deletes endpoint metadata.

3.  **`db_api.py`:**
    *   **`DatabaseAPI` Class:**
        *   `data_db`: An instance of `DocumentDatabase`.
        *   `registry`: An instance of `DatabaseRegistry`.
        *   `load_db()`: Loads the database.
        *   `save_db()`: Saves the database.
        *   `add_index(index_name, field, index_type, description)`: Adds an index.
        *   `get_index(index_name)`: Gets an index.
        *   `delete_index(index_name)`: Deletes an index.
        *   `add_data(data)`: Adds data.
        *   `update_data(doc_id, updated_data)`: Updates data.
        *   `delete_data(doc_id)`: Deletes data.
        *   `get_data(doc_id)`: Gets data.
        *   `query(index_name, query=None)`: Queries data.
        *   `get_indexes()`: Gets all index metadata.
        *   `get_schema()`: Gets all schema metadata.
        *   `get_endpoints()`: Gets all endpoint metadata.

4. **`init_db.py`**
    *   This file handles the creation of the database and registry, and populates them.
    *   `initialize_database`: Is called to perform this.

5. **`__init__.py`**
    * An empty file that is used to make the folder into a package.

## Index Types

Currently, the database supports the following index types:

*   **Hash Table:** Provides fast lookups for exact value matching.
    * This will be the default index type.

In the future, we may add:

*   **B-Tree:** For range queries.
*   **Inverted Index:** For text searching.

## Schemas

The schema in this database is more flexible than in traditional databases. Instead of rigidly enforcing it during data entry, it's used to describe the data:

*   **Schema Definition:**
    *   Fields and their expected data types (e.g., `id`: integer, `timestamp`: datetime, `type`: string, `category`: string).
    *   A description of each field.
*   **Schema-on-Read:** The database doesn't enforce the schema. You can add documents with new fields, but the schema registry helps to understand what data is available.

## Endpoints

Endpoints describe the API functions available to interact with the data and the database.

*   **Endpoint Definition:**
    *   `add_data`: Add new data to the database.
    * `update_data`: Updates data in the database.
    * `delete_data`: Deletes data from the database.
    * `get_data`: Gets data from the database.
    *  `query`: Queries the data.
* **Metadata**: For each endpoint, the registry will store the name, description, and parameters.

## Query System

The `query()` method allows you to retrieve data using an index and an optional query string:

*   **Index-Based:** Queries must use an index. You can't just do a full table scan.
* **Query creation**: The `create_query` function helps create the query and validate it.
*   **Query String:** The query string, if provided, filters the results from the index.

## How to Use It

### Initialization

1.  Run `init_db.py` to create the database and registry files, set up the initial schema and indexes, create initial endpoints, and add some initial data:
```
bash
    python init_db.py
    
```
### Creating Indexes

1.  Import the `DatabaseAPI` class.
2.  Create an instance of the `DatabaseAPI` class.
3.  Use the `add_index()` method:
```
python
    from hybrid_serverless_db.db_api import DatabaseAPI

    db_api = DatabaseAPI("data.json", "registry.json")
    db_api.load_db()

    db_api.add_index("name_index", "name", "hash_table", "Index for quick lookups by name.")
    db_api.save_db()
    
```
### Creating Data

1.  Import the `DatabaseAPI` class.
2.  Create an instance of the `DatabaseAPI` class.
3.  Use the `add_data()` method:
```
python
    from hybrid_serverless_db.db_api import DatabaseAPI

    db_api = DatabaseAPI("data.json", "registry.json")
    db_api.load_db()

    new_data = {"id": 1, "name": "Document 1", "category":"Category 1"}
    db_api.add_data(new_data)
    db_api.save_db()
    
```
### Updating Data

1.  Import the `DatabaseAPI` class.
2.  Create an instance of the `DatabaseAPI` class.
3.  Use the `update_data()` method:
```
python
    from hybrid_serverless_db.db_api import DatabaseAPI

    db_api = DatabaseAPI("data.json", "registry.json")
    db_api.load_db()

    updated_data = {"name": "Updated Document 1", "category":"New Category"}
    db_api.update_data(1, updated_data) #Updates the document with id 1.
    db_api.save_db()
    
```
### Querying Data

1.  Import the `DatabaseAPI` class.
2.  Create an instance of the `DatabaseAPI` class.
3.  Use the `query()` method:
```
python
    from hybrid_serverless_db.db_api import DatabaseAPI

    db_api = DatabaseAPI("data.json", "registry.json")
    db_api.load_db()

    results = db_api.query("name_index", {"name":"Updated Document 1"})
    print(results)
    
```
### Getting Data
1. Import the `DatabaseAPI` class.
2. Create an instance of the `DatabaseAPI` class.
3. Use the `get_data()` method:
```
python
    from hybrid_serverless_db.db_api import DatabaseAPI

    db_api = DatabaseAPI("data.json", "registry.json")
    db_api.load_db()

    results = db_api.get_data(1)
    print(results)
    
```
### Modifying Schema

1.  Import the `DatabaseAPI` class.
2.  Create an instance of the `DatabaseAPI` class.
3.  Use the registry functions:
```
python
    from hybrid_serverless_db.db_api import DatabaseAPI

    db_api = DatabaseAPI("data.json", "registry.json")
    db_api.load_db()

    db_api.registry.add_schema_info("new_field", "string", "This is a new field")
    db_api.save_db()
    
```
### Modifying endpoints
1.  Import the `DatabaseAPI` class.
2.  Create an instance of the `DatabaseAPI` class.
3.  Use the registry functions:
```
python
    from hybrid_serverless_db.db_api import DatabaseAPI

    db_api = DatabaseAPI("data.json", "registry.json")
    db_api.load_db()

    db_api.registry.add_endpoint_info("new_endpoint", "This is a new endpoint", {"param1":"data_type", "param2":"data_type"})
    db_api.save_db()
    
```
## Hybrid Serverless DB vs. PostgreSQL and Other Relational Databases

For our specific use case (advanced AI research), the Hybrid Serverless Database offers some advantages over typical relational databases like PostgreSQL:

1.  **Schema Flexibility:** In research, we often don't know the final structure of our data ahead of time. Relational databases require strict schemas, which can become restrictive.
2.  **Dynamic Indexing:** The ability to create and delete indexes on the fly is critical for optimizing different queries. Relational databases also have indexes, but adding new ones can be a more involved process.
3.  **Self-Describing:** The built-in registry is a major advantage. It's like having a dynamic metadata catalog for your database. Relational databases have schema information, but they don't usually have a registry of API endpoints or similar information.
4.  **Serverless:** No separate database server to set up and manage. This simplifies development and deployment.
5. **Customization**: This system is completely tailormade to fit our needs, it can be adapted for any scenario.
6. **Simple setup**: Setting up a relational database can be a challenge, this is much easier.

**When PostgreSQL is Better:**

*   **Complex Relationships:** If you have highly complex relationships between data, relational databases are better.
*   **ACID Compliance:** Relational databases are usually designed with ACID compliance (Atomicity, Consistency, Isolation, Durability) as a high priority. For us, ACID is not as critical.
* **Concurrency**: If you need lots of concurrency, PostgreSQL will provide a much better solution.

## Conclusion

The Hybrid Serverless Database is a powerful tool for our research project, offering flexibility, efficiency, and self-describability. While it's not a replacement for relational databases in all scenarios, it's well-suited for our specific needs.