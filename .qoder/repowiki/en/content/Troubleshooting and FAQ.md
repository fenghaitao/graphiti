# Troubleshooting and FAQ

<cite>
**Referenced Files in This Document**   
- [README.md](file://README.md)
- [graphiti.py](file://graphiti_core/graphiti.py)
- [errors.py](file://graphiti_core/errors.py)
- [llm_client/errors.py](file://graphiti_core/llm_client/errors.py)
- [driver/driver.py](file://graphiti_core/driver/driver.py)
- [helpers.py](file://graphiti_core/helpers.py)
- [examples/quickstart/README.md](file://examples/quickstart/README.md)
- [mcp_server/README.md](file://mcp_server/README.md)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Installation Issues](#installation-issues)
3. [Database Connectivity Problems](#database-connectivity-problems)
4. [LLM API Errors](#llm-api-errors)
5. [Search Performance Bottlenecks](#search-performance-bottlenecks)
6. [Data Consistency Issues](#data-consistency-issues)
7. [Configuration Mistakes](#configuration-mistakes)
8. [Frequently Asked Questions](#frequently-asked-questions)
9. [Conclusion](#conclusion)

## Introduction
This comprehensive troubleshooting guide and FAQ addresses common issues encountered when using Graphiti, a framework for building and querying temporally-aware knowledge graphs tailored for AI agents. The guide covers installation issues, database connectivity problems, LLM API errors, search performance bottlenecks, and data consistency issues. It provides detailed error messages, root cause analysis, and step-by-step solutions for each problem, along with diagnostic commands and logging techniques to help identify issues. The document also includes performance optimization tips for slow queries and high memory usage, common configuration mistakes, and best practices.

**Section sources**
- [README.md](file://README.md#L1-L650)

## Installation Issues
### Missing Dependencies
When installing Graphiti, ensure that all required dependencies are installed. Graphiti requires Python 3.10 or higher and specific database backends such as Neo4j, FalkorDB, Kuzu, or Amazon Neptune. Additionally, an OpenAI API key is required by default for LLM inference and embedding.

To install Graphiti with support for different database backends, use the appropriate extras:
```bash
pip install graphiti-core[falkordb]
pip install graphiti-core[kuzu]
pip install graphiti-core[neptune]
```

For optional LLM providers, install the corresponding extras:
```bash
pip install graphiti-core[anthropic,groq,google-genai]
```

### Environment Variables Not Set
Ensure that required environment variables are set, especially the `OPENAI_API_KEY`. For other LLM providers, set the corresponding API keys. For database configurations, set the appropriate environment variables or pass them directly to the driver constructors.

**Section sources**
- [README.md](file://README.md#L116-L207)

## Database Connectivity Problems
### Database Not Found Error
If you encounter the error `Neo.ClientError.Database.DatabaseNotFound: Graph not found: default_db`, it indicates that the driver is trying to connect to a database that does not exist. The Neo4j driver defaults to using `neo4j` as the database name. To resolve this issue, specify the correct database name in the driver constructor:

```python
from graphiti_core.driver.neo4j_driver import Neo4jDriver

driver = Neo4jDriver(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    database="your_custom_database"
)
```

### Connection Timeout
If you experience connection timeouts, verify that the database server is running and accessible. Check the URI, port, and credentials. For Neo4j, ensure that the database is started in Neo4j Desktop. For FalkorDB, use Docker to run the server:

```bash
docker run -p 6379:6379 -p 3000:3000 -it --rm falkordb/falkordb:latest
```

**Section sources**
- [README.md](file://README.md#L119-L142)
- [examples/quickstart/README.md](file://examples/quickstart/README.md#L13-L23)

## LLM API Errors
### Rate Limit Errors
Graphiti's ingestion pipelines are designed for high concurrency, controlled by the `SEMAPHORE_LIMIT` environment variable. By default, `SEMAPHORE_LIMIT` is set to `10` concurrent operations to prevent `429` rate limit errors from your LLM provider. If you encounter rate limit errors, try lowering this value:

```bash
export SEMAPHORE_LIMIT=5
```

If your LLM provider allows higher throughput, you can increase `SEMAPHORE_LIMIT` to boost episode ingestion performance.

### Structured Output Requirement
Graphiti works best with LLM services that support Structured Output, such as OpenAI and Gemini. Using other services may result in incorrect output schemas and ingestion failures. For Azure OpenAI, ensure that the v1 API is enabled for structured outputs:

```python
from openai import AsyncAzureOpenAI
from graphiti_core import Graphiti
from graphiti_core.llm_client import LLMConfig, OpenAIClient

api_key = "<your-api-key>"
api_version = "<your-api-version>"
llm_endpoint = "<your-llm-endpoint>"
embedding_endpoint = "<your-embedding-endpoint>"

llm_client_azure = AsyncAzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=llm_endpoint
)

embedding_client_azure = AsyncAzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=embedding_endpoint
)

azure_llm_config = LLMConfig(
    small_model="gpt-4.1-nano",
    model="gpt-4.1-mini",
)

graphiti = Graphiti(
    "bolt://localhost:7687",
    "neo4j",
    "password",
    llm_client=OpenAIClient(
        config=azure_llm_config,
        client=llm_client_azure
    ),
    embedder=OpenAIEmbedder(
        config=OpenAIEmbedderConfig(
            embedding_model="text-embedding-3-small-deployment"
        ),
        client=embedding_client_azure
    ),
    cross_encoder=OpenAIRerankerClient(
        config=LLMConfig(
            model=azure_llm_config.small_model
        ),
        client=llm_client_azure
    )
)
```

**Section sources**
- [README.md](file://README.md#L209-L219)
- [mcp_server/README.md](file://mcp_server/README.md#L131-L136)

## Search Performance Bottlenecks
### Slow Queries
To optimize search performance, ensure that indices and constraints are properly built in the database. Use the `build_indices_and_constraints` method to set up the necessary indices and constraints:

```python
await graphiti.build_indices_and_constraints()
```

For hybrid search, combine semantic embeddings, keyword (BM25), and graph traversal to achieve low-latency queries. Use predefined search recipes for efficient node and edge searches:

```python
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF

results = await graphiti.search_(query='Who is Tania', search_config=NODE_HYBRID_SEARCH_RRF)
```

### High Memory Usage
Monitor memory usage during ingestion and search operations. Use the `max_coroutines` parameter to limit the number of concurrent operations:

```python
graphiti = Graphiti(
    "bolt://localhost:7687",
    "neo4j",
    "password",
    max_coroutines=5
)
```

**Section sources**
- [graphiti.py](file://graphiti_core/graphiti.py#L321-L355)
- [README.md](file://README.md#L85-L89)

## Data Consistency Issues
### Entity Type Validation
Ensure that custom entity types do not use protected attribute names. The `validate_entity_types` function checks for conflicts between custom entity type fields and `EntityNode` fields:

```python
from graphiti_core.utils.ontology_utils.entity_types_utils import validate_entity_types

entity_types = {
    'Person': Person,
    'Organization': Organization,
}

validate_entity_types(entity_types)
```

### Group ID Validation
Group IDs must contain only alphanumeric characters, dashes, or underscores. Use the `validate_group_id` function to validate group IDs:

```python
from graphiti_core.helpers import validate_group_id

try:
    validate_group_id("valid-group_id")
except GroupIdValidationError as e:
    print(e.message)
```

**Section sources**
- [errors.py](file://graphiti_core/errors.py#L78-L83)
- [helpers.py](file://graphiti_core/helpers.py#L137-L140)

## Configuration Mistakes
### Incorrect Environment Variables
Ensure that environment variables are correctly set. Common mistakes include misspelled variable names or incorrect values. Refer to the documentation for the correct variable names and formats.

### Missing Database Configuration
When using custom database names, ensure that the database name is specified in the driver constructor. For Neo4j and FalkorDB, the default database names are `neo4j` and `default_db`, respectively. To use a different database, pass the `database` parameter to the driver constructor.

**Section sources**
- [README.md](file://README.md#L272-L354)

## Frequently Asked Questions
### What is Graphiti?
Graphiti is a framework for building and querying temporally-aware knowledge graphs, specifically tailored for AI agents operating in dynamic environments. It continuously integrates user interactions, structured and unstructured enterprise data, and external information into a coherent, queryable graph.

### How does Graphiti differ from GraphRAG?
Graphiti is designed for real-time incremental updates and bi-temporal data handling, making it suitable for applications requiring real-time interaction and precise historical queries. In contrast, GraphRAG is primarily used for static document summarization and batch-oriented processing.

### Can I use Graphiti with local LLMs?
Yes, Graphiti supports Ollama for running local LLMs and embedding models via Ollama's OpenAI-compatible API. Install the required models and configure the LLM client accordingly:

```python
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig

llm_config = LLMConfig(
    api_key="ollama",
    model="deepseek-r1:7b",
    base_url="http://localhost:11434/v1",
)

llm_client = OpenAIGenericClient(config=llm_config)

graphiti = Graphiti(
    "bolt://localhost:7687",
    "neo4j",
    "password",
    llm_client=llm_client,
    embedder=OpenAIEmbedder(
        config=OpenAIEmbedderConfig(
            api_key="ollama",
            embedding_model="nomic-embed-text",
            base_url="http://localhost:11434/v1",
        )
    ),
    cross_encoder=OpenAIRerankerClient(client=llm_client, config=llm_config),
)
```

**Section sources**
- [README.md](file://README.md#L37-L114)

## Conclusion
This troubleshooting guide and FAQ provide comprehensive solutions to common issues encountered when using Graphiti. By following the steps outlined in this document, users can effectively resolve installation issues, database connectivity problems, LLM API errors, search performance bottlenecks, and data consistency issues. The guide also covers common configuration mistakes and best practices, ensuring a smooth and efficient experience with Graphiti.

**Section sources**
- [README.md](file://README.md#L1-L650)