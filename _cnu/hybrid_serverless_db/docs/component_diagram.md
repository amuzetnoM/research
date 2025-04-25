# Component Diagram

This diagram illustrates the high-level components of the `hybrid_serverless_db` system and their relationships.
```
mermaid
graph TD
    A[db_api] -- Uses --> B(db_core)
    A -- Uses --> C(db_registry)
    D(init_db) -- Initializes --> A
    E(test_db) -- Tests --> A
    B -- Reads/Writes --> F[db.json]
    C -- Reads/Writes --> G[registry.json]
    classDef component fill:#f9f,stroke:#333,stroke-width:2px
    classDef file fill:#ccf,stroke:#333,stroke-width:2px
    class A,B,C,D,E component;
    class F,G file;
```
## Components

*   **`db_api` (DatabaseAPI):** This is the central interface for interacting with the database. It exposes functions to clients for data manipulation, querying, and index/schema/endpoint management.
    *   **Responsibilities:**
        *   Receiving requests from clients.
        *   Coordinating with `db_core` and `db_registry` to fulfill requests.
        *   Validating inputs and handling errors.
    *   **Connections:**
        *   `Uses` `db_core`: It relies on `db_core` for core database operations.
        *   `Uses` `db_registry`: It uses `db_registry` for managing index, schema, and endpoint metadata.
        * `Initialized by` `init_db`: It is initialized by the init_db module.
        * `Tested by` `test_db`: It is tested by the test_db module.
*   **`db_core` (DocumentDatabase):** This component handles the core database logic, including data storage, indexing, and querying.
    *   **Responsibilities:**
        *   Storing data in the `db.json` file.
        *   Creating, maintaining, and deleting indexes.
        *   Handling data addition, retrieval, update, and deletion.
        *   Querying data using indexes.
    *   **Connections:**
        *   `Reads/Writes` `db.json`: It reads from and writes to `db.json` to persist the database data.
        * `Used by` `db_api`: It is used by the db_api module.
*   **`db_registry` (DatabaseRegistry):** This component manages the registry metadata, including index definitions, data schema, and API endpoint information.
    *   **Responsibilities:**
        *   Storing metadata about indexes.
        *   Storing schema information.
        *   Storing API endpoint information.
    *   **Connections:**
        *   `Reads/Writes` `registry.json`: It reads from and writes to `registry.json` to persist the registry data.
        * `Used by` `db_api`: It is used by the db_api module.
*   **`init_db` (Database Initialization):** This is a utility module responsible for setting up the database initially.
    *   **Responsibilities:**
        *   Creating the `db.json` and `registry.json` files (if they don't exist).
        *   Defining and creating initial indexes.
        *   Defining and registering the initial data schema.
        *   Defining and registering the initial api endpoints.
        *   Adding some sample data to the database.
    *   **Connections:**
        *   `Initializes` `db_api`: It sets up and initializes an instance of the `db_api` module.
*   **`test_db` (Database tests):** This is a utility module responsible for testing the proper functioning of the system.
    * **Responsibilities:**
        * Testing initialization.
        * Testing index creation.
        * Testing schema creation.
        * Testing endpoint creation.
        * Testing data creation.
        * Testing data manipulation.
        * Testing data retrieval.
        * Testing data deletion.
        * Testing saving and loading data.
        * Testing getting all data from the registry.
        * Testing for errors.
    * **Connections:**
        * `Tests` `db_api`: It calls the db_api to test it.
*   **`db.json`:** This is the main data file.
    *   **Content:** Stores the actual document data.
    *   **Connections:**
        * `Read/Written by` `db_core`: It is read and written by the db_core module.
*   **`registry.json`:** This is the registry metadata file.
    *   **Content:** Stores metadata about indexes, schema, and endpoints.
    *   **Connections:**
        * `Read/Written by` `db_registry`: It is read and written by the db_registry module.

## Connections

*   **`-- Uses -->`:** Indicates that one component utilizes the functionality of another component.
*   **`-- Reads/Writes -->`:** Indicates that a component reads data from or writes data to a file.
*   **`-- Initializes -->`**: Indicates that a component is initialized by another.
*   **`-- Tests -->`**: Indicates that a component tests another.

This diagram and its associated documentation provide a clear, high-level view of the `hybrid_serverless_db` system's architecture.