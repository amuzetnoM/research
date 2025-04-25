# Hybrid Serverless Database System Diagram

This document provides a comprehensive diagram of the Hybrid Serverless Database system, illustrating its components, data flow, and interactions. The diagram is created using Mermaid.
```
mermaid
graph TD
    %% Components
    subgraph "Hybrid Serverless Database"
        subgraph db_api [DatabaseAPI]
            A[add_data]
            B[get_data]
            C[update_data]
            D[delete_data]
            E[query]
            F[add_index]
            G[get_index]
            H[delete_index]
            I[get_indexes]
            J[get_schema]
            K[get_endpoints]
        end
        
        subgraph db_core [DocumentDatabase]
            L[load_data]
            M[save_data]
            N[create_index]
            O[get_index]
            P[delete_index]
            Q[add_data]
            R[get_data]
            S[update_data]
            T[delete_data]
            U[create_query]
            V[query]
        end
        
        subgraph db_registry [DatabaseRegistry]
            W[load_registry]
            X[save_registry]
            Y[add_index_info]
            Z[get_index_info]
            AA[delete_index_info]
            AB[add_schema_info]
            AC[get_schema_info]
            AD[delete_schema_info]
            AE[add_endpoint_info]
            AF[get_endpoint_info]
            AG[delete_endpoint_info]
        end
    end
    
    %% Files
    subgraph Files
    dbjson[db.json]
    regjson[registry.json]
    end
    
    %% Other Modules
    initdb[init_db]
    testdb[test_db]

    client[Client/Application]

    
    %% Connections - Data Flow
    client -- API Call --> A
    client -- API Call --> B
    client -- API Call --> C
    client -- API Call --> D
    client -- API Call --> E

    A -- Calls --> Q
    B -- Calls --> R
    C -- Calls --> S
    D -- Calls --> T
    E -- Calls --> V
    F -- Calls --> N
    G -- Calls --> O
    H -- Calls --> P
    
    Q -- Data Manipulation --> dbjson
    R -- Data Retrieval --> dbjson
    S -- Data Manipulation --> dbjson
    T -- Data Manipulation --> dbjson
    V -- Data Retrieval --> dbjson

    N -- Index Manipulation --> regjson
    O -- Index Retrieval --> regjson
    P -- Index Manipulation --> regjson

    L -- load --> dbjson
    M -- save --> dbjson
    W -- load --> regjson
    X -- save --> regjson

    %% Connections - Registry
    A -- Adds Info --> Y
    F -- Adds Info --> Y
    G -- Gets Info --> Z
    H -- Deletes Info --> AA
    I -- Gets Info --> Z
    J -- Gets Info --> AC
    K -- Gets Info --> AF

    Y--save-->X
    Z--load-->W
    AA--save-->X
    AB--save-->X
    AC--load-->W
    AD--save-->X
    AE--save-->X
    AF--load-->W
    AG--save-->X
    
    %% Initialization
    initdb -- Initializes --> db_api
    
    %% Testing
    testdb -- Tests --> db_api
    
    %% Styling
    classDef component fill:#f9f,stroke:#333,stroke-width:2px
    classDef file fill:#ccf,stroke:#333,stroke-width:2px
    class db_api,db_core,db_registry,initdb,testdb component;
    class dbjson,regjson file;
```
## Diagram Components

### Modules

*   **`DatabaseAPI` (`db_api`)**
    *   **Purpose:** The `DatabaseAPI` serves as the primary interface for clients to interact with the database. It exposes functions for managing data and indexes, as well as querying the database.
    *   **Functions:**
        *   `add_data`: Adds new data to the database.
        *   `get_data`: Retrieves data from the database by ID.
        *   `update_data`: Updates existing data in the database.
        *   `delete_data`: Deletes data from the database.
        *   `query`: Queries the database using an index.
        *   `add_index`: Adds a new index to the database.
        *   `get_index`: Retrieves information about an index.
        *   `delete_index`: Deletes an index.
        *   `get_indexes`: Retrieves all index information from the registry.
        *   `get_schema`: Retrieves all schema information from the registry.
        *   `get_endpoints`: Retrieves all endpoint information from the registry.

*   **`DocumentDatabase` (`db_core`)**
    *   **Purpose:** The `DocumentDatabase` handles the core operations of the database, including loading, saving, indexing, and querying data.
    *   **Functions:**
        *   `load_data`: Loads data from `db.json` into memory.
        *   `save_data`: Saves data from memory to `db.json`.
        *   `create_index`: Creates an index on a specified field.
        *   `get_index`: Retrieves an existing index.
        *   `delete_index`: Deletes an existing index.
        *   `add_data`: Adds new data to the database.
        *   `get_data`: Retrieves data from the database by ID.
        *   `update_data`: Updates data in the database.
        *   `delete_data`: Deletes data from the database.
        *   `create_query`: Creates a query using index information.
        *   `query`: Queries the database using an index and an optional filter.

*   **`DatabaseRegistry` (`db_registry`)**
    *   **Purpose:** The `DatabaseRegistry` manages metadata about the database, including indexes, schemas, and API endpoints.
    *   **Functions:**
        *   `load_registry`: Loads registry metadata from `registry.json`.
        *   `save_registry`: Saves registry metadata to `registry.json`.
        *   `add_index_info`: Adds metadata about a new index.
        *   `get_index_info`: Retrieves metadata about an index.
        *   `delete_index_info`: Deletes metadata about an index.
        *   `add_schema_info`: Adds schema metadata.
        *   `get_schema_info`: Retrieves schema metadata.
        *   `delete_schema_info`: Deletes schema metadata.
        *   `add_endpoint_info`: Adds metadata about an API endpoint.
        *   `get_endpoint_info`: Retrieves metadata about an API endpoint.
        *   `delete_endpoint_info`: Deletes metadata about an API endpoint.

* **`init_db`**
    * **Purpose**: Initializes the database. Creates all files if needed and populates the database with initial information.
* **`test_db`**
    * **Purpose**: Contains the tests for the database.

### Files

*   **`db.json`**
    *   **Purpose:** Stores the main data of the database in JSON format.
*   **`registry.json`**
    *   **Purpose:** Stores the registry metadata (indexes, schemas, endpoints) in JSON format.

### Client

* **`Client/Application`**
    * **Purpose**: Represents the external user or application that will use our database.

## Data Flow and Connections

### Data Flow

1.  **Client Interaction:** The `Client/Application` interacts with the `DatabaseAPI` through API calls (`add_data`, `get_data`, `update_data`, `delete_data`, `query`).
2.  **API to Core:** The `DatabaseAPI` calls functions in the `DocumentDatabase` to perform data manipulation (`add_data`, `update_data`, `delete_data`) or retrieval (`get_data`, `query`).
3.  **Core to Files:** The `DocumentDatabase` loads data from and saves data to `db.json`.
4.  **API to Registry:** The `DatabaseAPI` interacts with the `DatabaseRegistry` to manage index, schema, and endpoint metadata.
5. **Registry Manipulation**: The `DatabaseAPI` adds, modifies and deletes data in the registry.
6.  **Registry to Files:** The `DatabaseRegistry` loads data from and saves data to `registry.json`.

### Module Interactions

*   **`DatabaseAPI` and `DocumentDatabase`:**
    *   `DatabaseAPI` uses `DocumentDatabase` to perform core data operations.
    *   API calls are translated into `DocumentDatabase` function calls.
*   **`DatabaseAPI` and `DatabaseRegistry`:**
    *   `DatabaseAPI` uses `DatabaseRegistry` to manage metadata.
    *   API functions related to indexes, schemas, and endpoints are handled by `DatabaseRegistry`.
* **`DocumentDatabase` and `Files`**:
    * The `DocumentDatabase` loads data from and saves data to the `db.json` file.
* **`DatabaseRegistry` and `Files`**:
    * The `DatabaseRegistry` loads data from and saves data to the `registry.json` file.
* **`init_db` and `DatabaseAPI`**:
    * The `init_db` module creates an instance of the `DatabaseAPI`.
* **`test_db` and `DatabaseAPI`**:
    * The `test_db` module tests the functions of the `DatabaseAPI`.

### Initialization

*   The `init_db` module initializes the `DatabaseAPI`, sets up initial indexes, schemas, endpoints, and adds sample data.

### Testing

* The `test_db` module tests the database.

### Styling

* **Components** (`db_api`, `db_core`, `db_registry`, `init_db`, `test_db`): These are styled with a light green background and a dark gray border.
* **Files** (`db.json`, `registry.json`): These are styled with a light blue background and a dark gray border.