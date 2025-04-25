## Data Flow Diagram

This diagram illustrates how data flows through the hybrid serverless database system. It shows the interactions between the client, the API, the core database, and the registry.
```
mermaid
graph TD
    A[Client/Application] -- API Call (e.g., add_data, query) --> B(db_api)
    B -- Data Manipulation --> C(db_core)
    B -- Registry Management --> D(db_registry)
    C -- Reads/Writes --> E[db.json]
    D -- Reads/Writes --> F[registry.json]
    style E fill:#ccf,stroke:#333,stroke-width:2px
    style F fill:#ccf,stroke:#333,stroke-width:2px
```
### Components

*   **`Client/Application`:**
    *   Represents any external system, user, or application that interacts with the hybrid serverless database.
    *   Initiates data-related operations through API calls.

*   **`db_api` (DatabaseAPI):**
    *   Serves as the main entry point for clients to interact with the database.
    *   Receives API calls from the client, such as `add_data`, `query`, `update_data`, `delete_data`, etc.
    *   Delegates data-related operations to `db_core` for document storage and retrieval.
    *   Delegates registry-related operations to `db_registry` for managing indexes, schemas, and endpoints.

*   **`db_core` (DocumentDatabase):**
    *   Manages the core document storage and retrieval logic.
    *   Handles operations such as adding, updating, deleting, and querying documents.
    *   Interacts directly with the `db.json` file to persist data.

*   **`db_registry` (DatabaseRegistry):**
    *   Manages the metadata registry for indexes, schemas, and API endpoints.
    *   Handles operations such as adding, retrieving, and deleting index, schema, and endpoint information.
    *   Interacts directly with the `registry.json` file to persist registry metadata.

*   **`db.json`:**
    *   The JSON file that serves as the primary data store for the database.
    *   Stores the documents and their data.

*   **`registry.json`:**
    *   The JSON file that stores the registry metadata.
    *   Includes information about indexes, schemas, and API endpoints.

### Connections and Data Flow

1.  **API Calls:**
    *   The `Client/Application` initiates data operations by sending API calls to `db_api`.
    *   Examples of API calls include `add_data`, `get_data`, `update_data`, `delete_data`, `query`, `add_index`, etc.

2.  **Data Manipulation:**
    *   `db_api` receives the API call and determines whether it's a data-related or registry-related operation.
    *   For data-related operations, `db_api` delegates the task to `db_core` for document manipulation.
    *   `db_core` performs the requested data operation.

3.  **Registry Management:**
    *   For registry-related operations, `db_api` delegates the task to `db_registry`.
    *   `db_registry` performs the requested registry operation.

4.  **Reads/Writes:**
    *   `db_core` reads and writes document data to `db.json`.
    *   `db_registry` reads and writes registry metadata to `registry.json`.

### Summary

This data flow diagram provides a clear picture of how data and operations move through the hybrid serverless database system. It emphasizes the separation of concerns between the API, core database logic, and registry management. It also highlights the role of the `db.json` and `registry.json` files for data persistence.