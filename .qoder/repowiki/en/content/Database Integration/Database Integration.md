# Database Integration

<cite>
**Referenced Files in This Document**   
- [driver.py](file://graphiti_core/driver/driver.py)
- [falkordb_driver.py](file://graphiti_core/driver/falkordb_driver.py)
- [kuzu_driver.py](file://graphiti_core/driver/kuzu_driver.py)
- [neo4j_driver.py](file://graphiti_core/driver/neo4j_driver.py)
- [neptune_driver.py](file://graphiti_core/driver/neptune_driver.py)
- [graph_operations.py](file://graphiti_core/driver/graph_operations/graph_operations.py)
- [search_interface.py](file://graphiti_core/driver/search_interface/search_interface.py)
- [graphiti.py](file://graphiti_core/graphiti.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Driver Abstraction Layer](#driver-abstraction-layer)
3. [Factory Pattern Implementation](#factory-pattern-implementation)
4. [Supported Database Drivers](#supported-database-drivers)
5. [Common Graph Operations Interface](#common-graph-operations-interface)
6. [Connection Pooling and Transaction Management](#connection-pooling-and-transaction-management)
7. [Error Handling Strategies](#error-handling-strategies)
8. [Database Selection Guidance](#database-selection-guidance)
9. [Migration Considerations](#migration-considerations)

## Introduction
Graphiti provides a multi-database support system that enables seamless integration with various graph databases through a unified interface. This documentation details the architecture of the database integration layer, focusing on the driver abstraction, factory pattern implementation, and support for multiple database backends including Neo4j, FalkorDB, Kuzu, and Neptune. The system is designed to provide database-agnostic development capabilities while maintaining optimal performance characteristics for each supported database.

## Driver Abstraction Layer
The driver abstraction layer in Graphiti provides a unified interface across different graph databases through a well-defined class hierarchy. At the core of this abstraction is the `GraphDriver` abstract base class, which defines the common interface for all database drivers.

```mermaid
classDiagram
class GraphDriver {
<<abstract>>
+provider : GraphProvider
+fulltext_syntax : str
+_database : str
+search_interface : SearchInterface
+graph_operations_interface : GraphOperationsInterface
+execute_query(cypher_query_ : str, **kwargs : Any) : Coroutine
+session(database : str | None = None) : GraphDriverSession
+close()
+delete_all_indexes() : Coroutine
+with_database(database : str) : GraphDriver
+build_fulltext_query(query : str, group_ids : list[str] | None = None, max_query_length : int = 128) : str
}
class GraphDriverSession {
<<abstract>>
+provider : GraphProvider
+__aenter__()
+__aexit__(exc_type, exc, tb)
+run(query : str, **kwargs : Any) : Any
+close()
+execute_write(func, *args, **kwargs)
}
class GraphProvider {
<<enumeration>>
+NEO4J
+FALKORDB
+KUZU
+NEPTUNE
}
GraphDriver <|-- Neo4jDriver
GraphDriver <|-- FalkorDriver
GraphDriver <|-- KuzuDriver
GraphDriver <|-- NeptuneDriver
GraphDriverSession <|-- Neo4jDriverSession
GraphDriverSession <|-- FalkorDriverSession
GraphDriverSession <|-- KuzuDriverSession
GraphDriverSession <|-- NeptuneDriverSession
GraphDriver ..> GraphProvider
GraphDriver ..> SearchInterface
GraphDriver ..> GraphOperationsInterface
```

**Diagram sources**
- [driver.py](file://graphiti_core/driver/driver.py#L42-L115)

**Section sources**
- [driver.py](file://graphiti_core/driver/driver.py#L42-L115)

## Factory Pattern Implementation
Graphiti implements a factory pattern that allows for pluggable database backends through the `Graphiti` class constructor. The factory pattern is implemented by accepting a `graph_driver` parameter that can be any implementation of the `GraphDriver` interface.

```mermaid
sequenceDiagram
participant Application
participant Graphiti
participant DriverFactory
participant Neo4jDriver
participant FalkorDriver
participant KuzuDriver
participant NeptuneDriver
Application->>Graphiti : Initialize with graph_driver parameter
alt Driver Provided
Graphiti->>Graphiti : Use provided driver instance
else Default Driver
Graphiti->>DriverFactory : Create default driver (Neo4j)
DriverFactory->>Neo4jDriver : Initialize with URI, user, password
Neo4jDriver-->>DriverFactory : Return Neo4jDriver instance
DriverFactory-->>Graphiti : Return driver instance
end
Graphiti-->>Application : Return Graphiti instance
```

**Diagram sources**
- [graphiti.py](file://graphiti_core/graphiti.py#L128-L200)

**Section sources**
- [graphiti.py](file://graphiti_core/graphiti.py#L128-L200)

## Supported Database Drivers
Graphiti supports four major graph database backends, each implemented as a concrete class extending the `GraphDriver` abstract base class. Each driver provides specific configuration options, performance characteristics, and deployment considerations.

### Neo4j Driver
The Neo4j driver provides integration with the Neo4j graph database, supporting both local and remote instances through the Bolt protocol.

```mermaid
classDiagram
class Neo4jDriver {
+provider : GraphProvider = NEO4J
+__init__(uri : str, user : str | None, password : str | None, database : str = 'neo4j')
+execute_query(cypher_query_ : LiteralString, **kwargs : Any) : EagerResult
+session(database : str | None = None) : GraphDriverSession
+close() : None
+delete_all_indexes() : Coroutine
}
Neo4jDriver --|> GraphDriver
```

**Configuration Options**
- `uri`: Connection URI (e.g., bolt://localhost:7687)
- `user`: Authentication username
- `password`: Authentication password
- `database`: Target database name (default: 'neo4j')

**Performance Characteristics**
- Optimized for complex graph traversals
- Strong ACID compliance
- Excellent for deep relationship queries

**Deployment Considerations**
- Requires Neo4j server installation
- Supports both single-instance and clustered deployments
- Enterprise edition provides advanced clustering and high availability

**Section sources**
- [neo4j_driver.py](file://graphiti_core/driver/neo4j_driver.py#L29-L75)

### FalkorDB Driver
The FalkorDB driver integrates with the Redis-based graph database, providing high-performance capabilities for real-time applications.

```mermaid
classDiagram
class FalkorDriver {
+provider : GraphProvider = FALKORDB
+fulltext_syntax : str = '@'
+aoss_client : None = None
+__init__(host : str = 'localhost', port : int = 6379, username : str | None = None, password : str | None = None, falkor_db : FalkorDB | None = None, database : str = 'default_db')
+execute_query(cypher_query_ : str, **kwargs : Any) : tuple[list[dict[str, Any]], None, None]
+session(database : str | None = None) : GraphDriverSession
+close() : None
+delete_all_indexes() : None
+clone(database : str) : GraphDriver
+sanitize(query : str) : str
+build_fulltext_query(query : str, group_ids : list[str] | None = None, max_query_length : int = 128) : str
}
FalkorDriver --|> GraphDriver
```

**Configuration Options**
- `host`: Server hostname (default: 'localhost')
- `port`: Server port (default: 6379)
- `username`: Authentication username (optional)
- `password`: Authentication password (optional)
- `database`: Database name (default: 'default_db')

**Performance Characteristics**
- In-memory performance with Redis backend
- Low latency for read operations
- High throughput for write operations

**Deployment Considerations**
- Can run as standalone server or integrated with Redis
- Supports on-premises and cloud deployments
- Multi-tenant architecture allows multiple graphs in single instance

**Section sources**
- [falkordb_driver.py](file://graphiti_core/driver/falkordb_driver.py#L112-L309)

### Kuzu Driver
The Kuzu driver provides integration with the lightweight, embeddable Kuzu graph database, designed for applications requiring a compact footprint.

```mermaid
classDiagram
class KuzuDriver {
+provider : GraphProvider = KUZU
+aoss_client : None = None
+__init__(db : str = ' : memory : ', max_concurrent_queries : int = 1)
+execute_query(cypher_query_ : str, **kwargs : Any) : tuple[list[dict[str, Any]] | list[list[dict[str, Any]]], None, None]
+session(_database : str | None = None) : GraphDriverSession
+close()
+delete_all_indexes(database_ : str)
+setup_schema()
}
KuzuDriver --|> GraphDriver
```

**Configuration Options**
- `db`: Database path (':memory:' for in-memory, file path for persistent)
- `max_concurrent_queries`: Maximum concurrent queries (default: 1)

**Performance Characteristics**
- Optimized for single-threaded performance
- Efficient memory usage
- Fast startup time

**Deployment Considerations**
- Embeddable design suitable for edge applications
- Single-file deployment
- No external dependencies

**Section sources**
- [kuzu_driver.py](file://graphiti_core/driver/kuzu_driver.py#L93-L177)

### Neptune Driver
The Neptune driver integrates with Amazon Neptune, providing cloud-native graph database capabilities with integrated OpenSearch for full-text search.

```mermaid
classDiagram
class NeptuneDriver {
+provider : GraphProvider = NEPTUNE
+__init__(host : str, aoss_host : str, port : int = 8182, aoss_port : int = 443)
+execute_query(cypher_query_ : str, **kwargs : Any) : tuple[dict[str, Any], None, None]
+session(database : str | None = None) : GraphDriverSession
+close() : None
+_delete_all_data() : Any
+delete_all_indexes() : Coroutine[Any, Any, Any]
+delete_all_indexes_impl() : Coroutine[Any, Any, Any]
+create_aoss_indices()
+delete_aoss_indices()
+run_aoss_query(name : str, query_text : str, limit : int = 10) : dict[str, Any]
+save_to_aoss(name : str, data : list[dict]) : int
}
NeptuneDriver --|> GraphDriver
```

**Configuration Options**
- `host`: Neptune endpoint (neptune-db://<endpoint> or neptune-graph://<graphid>)
- `aoss_host`: OpenSearch serverless host
- `port`: Neptune port (default: 8182)
- `aoss_port`: OpenSearch port (default: 443)

**Performance Characteristics**
- Auto-scaling cloud infrastructure
- Integrated full-text search with OpenSearch
- High availability and durability

**Deployment Considerations**
- Fully managed AWS service
- Requires IAM authentication
- Integrated with AWS security and monitoring tools

**Section sources**
- [neptune_driver.py](file://graphiti_core/driver/neptune_driver.py#L109-L300)

## Common Graph Operations Interface
Graphiti provides a common interface for graph operations through the `GraphOperationsInterface` class, enabling database-agnostic development of graph mutation behaviors.

```mermaid
classDiagram
class GraphOperationsInterface {
<<abstract>>
+node_save(node : Any, driver : Any) : None
+node_delete(node : Any, driver : Any) : None
+node_save_bulk(_cls : Any, driver : Any, transaction : Any, nodes : list[Any], batch_size : int = 100) : None
+node_delete_by_group_id(_cls : Any, driver : Any, group_id : str, batch_size : int = 100) : None
+node_delete_by_uuids(_cls : Any, driver : Any, uuids : list[str], group_id : str | None = None, batch_size : int = 100) : None
+node_load_embeddings(node : Any, driver : Any) : None
+node_load_embeddings_bulk(_cls : Any, driver : Any, transaction : Any, nodes : list[Any], batch_size : int = 100) : None
+episodic_node_save(node : Any, driver : Any) : None
+episodic_node_delete(node : Any, driver : Any) : None
+episodic_node_save_bulk(_cls : Any, driver : Any, transaction : Any, nodes : list[Any], batch_size : int = 100) : None
+episodic_edge_save_bulk(_cls : Any, driver : Any, transaction : Any, episodic_edges : list[Any], batch_size : int = 100) : None
+episodic_node_delete_by_group_id(_cls : Any, driver : Any, group_id : str, batch_size : int = 100) : None
+episodic_node_delete_by_uuids(_cls : Any, driver : Any, uuids : list[str], group_id : str | None = None, batch_size : int = 100) : None
+edge_save(edge : Any, driver : Any) : None
+edge_delete(edge : Any, driver : Any) : None
+edge_save_bulk(_cls : Any, driver : Any, transaction : Any, edges : list[Any], batch_size : int = 100) : None
+edge_delete_by_uuids(_cls : Any, driver : Any, uuids : list[str], group_id : str | None = None) : None
+edge_load_embeddings(edge : Any, driver : Any) : None
+edge_load_embeddings_bulk(_cls : Any, driver : Any, transaction : Any, edges : list[Any], batch_size : int = 100) : None
}
GraphOperationsInterface ..> GraphDriver
```

**Diagram sources**
- [graph_operations.py](file://graphiti_core/driver/graph_operations/graph_operations.py#L22-L196)

**Section sources**
- [graph_operations.py](file://graphiti_core/driver/graph_operations/graph_operations.py#L22-L196)

## Connection Pooling and Transaction Management
Graphiti's driver architecture includes comprehensive connection pooling and transaction management capabilities. Each driver implementation handles connection lifecycle management through the `session()` method, which returns a `GraphDriverSession` instance.

```mermaid
flowchart TD
Start([Application Request]) --> CreateSession["Create Session via driver.session()"]
CreateSession --> ExecuteWrite["Execute Write Operations"]
ExecuteWrite --> ExecuteWriteMethod["session.execute_write(func, *args, **kwargs)"]
ExecuteWriteMethod --> Transaction["Transaction Context"]
Transaction --> RunQueries["Run Multiple Queries"]
RunQueries --> Commit["Commit Transaction"]
Commit --> EndSession["Close Session"]
EndSession --> End([Request Complete])
ExecuteWrite --> ExecuteRead["Execute Read Operations"]
ExecuteRead --> RunQuery["session.run(query, **kwargs)"]
RunQuery --> ReturnResults["Return Results"]
ReturnResults --> EndSession
```

The `execute_write` method provides a transactional context for write operations, ensuring atomicity and consistency. Connection pooling is handled internally by each driver implementation, with connection reuse across sessions when possible.

**Section sources**
- [driver.py](file://graphiti_core/driver/driver.py#L49-L71)
- [falkordb_driver.py](file://graphiti_core/driver/falkordb_driver.py#L94-L97)
- [kuzu_driver.py](file://graphiti_core/driver/kuzu_driver.py#L166-L168)
- [neptune_driver.py](file://graphiti_core/driver/neptune_driver.py#L288-L290)

## Error Handling Strategies
Graphiti implements a comprehensive error handling strategy across all database drivers, with consistent patterns for exception management and recovery.

```mermaid
flowchart TD
StartOperation["Driver Operation"] --> TryBlock["Try Block"]
TryBlock --> ExecuteOperation["Execute Database Operation"]
ExecuteOperation --> Success["Operation Successful"]
Success --> ReturnResult["Return Result"]
ReturnResult --> End
ExecuteOperation --> Failure["Operation Failed"]
Failure --> CatchBlock["Catch Exception"]
CatchBlock --> CheckErrorType["Check Error Type"]
CheckErrorType --> IndexExists{"Index Already Exists?"}
IndexExists --> |Yes| LogInfo["Log as Info, Continue"]
IndexExists --> |No| CheckQueryError{"Query Execution Error?"}
CheckQueryError --> |Yes| LogError["Log Error with Query and Params"]
CheckQueryError --> |No| ReThrow["Re-throw Exception"]
LogInfo --> End
LogError --> ReThrow
ReThrow --> ThrowException["Throw Exception to Caller"]
ThrowException --> End
```

Each driver implementation includes specific error handling for database-specific conditions, such as the FalkorDB driver's handling of "already indexed" errors, which are treated as non-fatal conditions. All query execution errors are logged with the complete query and parameters for debugging purposes.

**Section sources**
- [falkordb_driver.py](file://graphiti_core/driver/falkordb_driver.py#L157-L163)
- [kuzu_driver.py](file://graphiti_core/driver/kuzu_driver.py#L119-L122)
- [neo4j_driver.py](file://graphiti_core/driver/neo4j_driver.py#L58-L60)
- [neptune_driver.py](file://graphiti_core/driver/neptune_driver.py#L207-L210)

## Database Selection Guidance
Choosing the right database backend for Graphiti depends on specific use case requirements, including performance needs, deployment environment, and scalability requirements.

### Comparison Table

| Database | Use Case | Performance | Deployment | Scalability | Cost |
|----------|---------|-------------|------------|-------------|------|
| Neo4j | Complex graph traversals, enterprise applications | High for deep queries | On-premises, cloud, managed | Horizontal scaling (Enterprise) | Commercial, open source available |
| FalkorDB | Real-time applications, high throughput | Very high (in-memory) | On-premises, cloud, Redis integration | Vertical scaling | Open source, commercial support |
| Kuzu | Embedded applications, edge computing | Optimized for single-threaded | Embedded, lightweight | Limited (single instance) | Open source |
| Neptune | Cloud-native applications, large-scale | Auto-scaling, managed service | AWS cloud only | Automatic horizontal scaling | Pay-per-use, AWS pricing |

### Selection Criteria

**Choose Neo4j when:**
- You need advanced graph algorithms and complex traversals
- Enterprise features like role-based access control are required
- You have existing Neo4j expertise or infrastructure
- ACID compliance is critical for your use case

**Choose FalkorDB when:**
- Low latency and high throughput are primary requirements
- You already use Redis in your technology stack
- Real-time applications require sub-millisecond response times
- You need a multi-tenant architecture

**Choose Kuzu when:**
- You need an embeddable, lightweight solution
- Your application runs on edge devices or has limited resources
- You want a simple, single-file deployment
- Your dataset size is moderate and fits in memory

**Choose Neptune when:**
- You are already invested in the AWS ecosystem
- You need automatic scaling and high availability
- Your application requires integration with other AWS services
- You want a fully managed database service

**Section sources**
- [neo4j_driver.py](file://graphiti_core/driver/neo4j_driver.py)
- [falkordb_driver.py](file://graphiti_core/driver/falkordb_driver.py)
- [kuzu_driver.py](file://graphiti_core/driver/kuzu_driver.py)
- [neptune_driver.py](file://graphiti_core/driver/neptune_driver.py)

## Migration Considerations
Migrating between different graph databases in Graphiti requires careful planning due to differences in configuration, performance characteristics, and deployment models.

### Migration Strategy
```mermaid
flowchart TD
AssessCurrent["Assess Current Database Usage"] --> IdentifyPatterns["Identify Query Patterns and Workloads"]
IdentifyPatterns --> EvaluateOptions["Evaluate Target Database Options"]
EvaluateOptions --> PlanMigration["Plan Migration Strategy"]
PlanMigration --> ChooseApproach{"Migration Approach"}
ChooseApproach --> |Parallel Run| ParallelRun["Run Both Databases in Parallel"]
ChooseApproach --> |Cutover| Cutover["Direct Cutover"]
ChooseApproach --> |Phased| Phased["Phased Migration"]
ParallelRun --> TestPerformance["Test Performance and Compatibility"]
Cutover --> BackupData["Backup Current Data"]
Phased --> IdentifyComponents["Identify Components to Migrate First"]
TestPerformance --> ValidateData["Validate Data Integrity"]
BackupData --> MigrateData["Migrate Data"]
IdentifyComponents --> MigrateComponents["Migrate Components Incrementally"]
ValidateData --> SwitchTraffic["Switch Application Traffic"]
MigrateData --> SwitchTraffic
MigrateComponents --> SwitchTraffic
SwitchTraffic --> MonitorPerformance["Monitor Performance"]
MonitorPerformance --> Optimize["Optimize Configuration"]
Optimize --> Complete["Migration Complete"]
```

### Key Migration Considerations

**Data Model Compatibility:**
- Ensure that the data model is compatible with the target database
- Verify that all required indexes and constraints can be created
- Test complex queries to ensure equivalent performance

**Configuration Changes:**
- Update connection parameters in application configuration
- Adjust batch sizes and concurrency settings based on target database capabilities
- Configure appropriate timeout values for network operations

**Performance Testing:**
- Conduct thorough performance testing with production-like workloads
- Compare query execution times for critical operations
- Monitor resource utilization (CPU, memory, I/O)

**Rollback Plan:**
- Prepare a rollback strategy in case of migration issues
- Maintain backups of the original database
- Test the rollback procedure before starting migration

**Section sources**
- [driver.py](file://graphiti_core/driver/driver.py)
- [graphiti.py](file://graphiti_core/graphiti.py)