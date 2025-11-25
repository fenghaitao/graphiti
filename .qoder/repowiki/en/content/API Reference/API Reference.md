# API Reference

<cite>
**Referenced Files in This Document**   
- [graphiti.py](file://graphiti_core/graphiti.py)
- [driver.py](file://graphiti_core/driver/driver.py)
- [neo4j_driver.py](file://graphiti_core/driver/neo4j_driver.py)
- [falkordb_driver.py](file://graphiti_core/driver/falkordb_driver.py)
- [kuzu_driver.py](file://graphiti_core/driver/kuzu_driver.py)
- [neptune_driver.py](file://graphiti_core/driver/neptune_driver.py)
- [client.py](file://graphiti_core/llm_client/client.py)
- [openai_client.py](file://graphiti_core/llm_client/openai_client.py)
- [anthropic_client.py](file://graphiti_core/llm_client/anthropic_client.py)
- [gemini_client.py](file://graphiti_core/llm_client/gemini_client.py)
- [groq_client.py](file://graphiti_core/llm_client/groq_client.py)
- [client.py](file://graphiti_core/embedder/client.py)
- [openai.py](file://graphiti_core/embedder/openai.py)
- [azure_openai.py](file://graphiti_core/embedder/azure_openai.py)
- [gemini.py](file://graphiti_core/embedder/gemini.py)
- [voyage.py](file://graphiti_core/embedder/voyage.py)
- [client.py](file://graphiti_core/cross_encoder/client.py)
- [openai_reranker_client.py](file://graphiti_core/cross_encoder/openai_reranker_client.py)
- [bge_reranker_client.py](file://graphiti_core/cross_encoder/bge_reranker_client.py)
- [gemini_reranker_client.py](file://graphiti_core/cross_encoder/gemini_reranker_client.py)
- [search.py](file://graphiti_core/search/search.py)
- [search_config.py](file://graphiti_core/search/search_config.py)
</cite>

## Table of Contents
1. [Graphiti Class Initialization](#graphiti-class-initialization)
2. [Core Methods](#core-methods)
3. [Driver Interface and Implementations](#driver-interface-and-implementations)
4. [LLM Client Abstraction](#llm-client-abstraction)
5. [Embedder Interface](#embedder-interface)
6. [Cross-Encoder Interface](#cross-encoder-interface)
7. [Search Configuration](#search-configuration)
8. [Usage Examples](#usage-examples)
9. [Error Handling](#error-handling)

## Graphiti Class Initialization

The `Graphiti` class serves as the main entry point for interacting with the Graphiti framework. It manages connections to the graph database, LLM services, embedding models, and search configurations.

```python
class Graphiti:
    def __init__(
        self,
        uri: str | None = None,
        user: str | None = None,
        password: str | None = None,
        llm_client: LLMClient | None = None,
        embedder: EmbedderClient | None = None,
        cross_encoder: CrossEncoderClient | None = None,
        store_raw_episode_content: bool = True,
        graph_driver: GraphDriver | None = None,
        max_coroutines: int | None = None,
        tracer: Tracer | None = None,
        trace_span_prefix: str = 'graphiti',
    ):
```

**Parameters:**
- `uri`: Database connection URI (required when not providing a custom driver)
- `user`: Database authentication username
- `password`: Database authentication password
- `llm_client`: LLM client instance for natural language processing tasks. If not provided, defaults to `OpenAIClient`.
- `embedder`: Embedding client instance for vector operations. If not provided, defaults to `OpenAIEmbedder`.
- `cross_encoder`: Cross-encoder client for reranking search results. If not provided, defaults to `OpenAIRerankerClient`.
- `store_raw_episode_content`: Whether to store raw episode content in the database (default: True)
- `graph_driver`: Custom graph driver implementation. If not provided, defaults to `Neo4jDriver`.
- `max_coroutines`: Maximum number of concurrent operations allowed
- `tracer`: OpenTelemetry tracer instance for distributed tracing
- `trace_span_prefix`: Prefix for tracing span names (default: 'graphiti')

The constructor establishes connections to the specified graph database and initializes the various AI service clients. When no custom clients are provided, it automatically initializes default implementations based on environment variables.

**Section sources**
- [graphiti.py](file://graphiti_core/graphiti.py#L128-L236)

## Core Methods

### add_episode Method

The `add_episode` method processes textual or structured content and extracts entities and relationships to build the knowledge graph.

```python
async def add_episode(
    self,
    name: str,
    episode_body: str,
    source_description: str,
    reference_time: datetime,
    source: EpisodeType = EpisodeType.message,
    group_id: str | None = None,
    uuid: str | None = None,
    update_communities: bool = False,
    entity_types: dict[str, type[BaseModel]] | None = None,
    excluded_entity_types: list[str] | None = None,
    previous_episode_uuids: list[str] | None = None,
    edge_types: dict[str, type[BaseModel]] | None = None,
    edge_type_map: dict[tuple[str, str], list[str]] | None = None,
) -> AddEpisodeResults:
```

**Parameters:**
- `name`: Name identifier for the episode
- `episode_body`: Content to be processed (text or JSON)
- `source_description`: Description of the content source
- `reference_time`: Timestamp for temporal context
- `source`: Type of episode (e.g., message, text, JSON)
- `group_id`: Optional partition identifier for multi-tenant scenarios
- `uuid`: Optional custom UUID for the episode
- `update_communities`: Whether to update community detection with new information
- `entity_types`: Custom entity type definitions using Pydantic models
- `excluded_entity_types`: Entity types to exclude from graph creation
- `previous_episode_uuids`: Explicit list of prior episodes for context
- `edge_types`: Custom relationship type definitions
- `edge_type_map`: Mapping of source-target entity types to relationship types

The method returns an `AddEpisodeResults` object containing the created episode, nodes, edges, and community information.

**Section sources**
- [graphiti.py](file://graphiti_core/graphiti.py#L611-L800)

### search Method

The `search` method performs hybrid searches across the knowledge graph using multiple retrieval strategies and reranking techniques.

```python
async def search(
    self,
    query: str,
    group_ids: list[str] | None = None,
    config: SearchConfig | None = None,
    search_filter: SearchFilters | None = None,
    center_node_uuid: str | None = None,
    bfs_origin_node_uuids: list[str] | None = None,
    query_vector: list[float] | None = None,
) -> SearchResults:
```

**Parameters:**
- `query`: Search query string
- `group_ids`: Optional list of group IDs to restrict search scope
- `config`: Search configuration object defining search strategies
- `search_filter`: Filters to apply to search results
- `center_node_uuid`: Reference node for distance-based reranking
- `bfs_origin_node_uuids`: Starting nodes for breadth-first search expansion
- `query_vector`: Pre-computed embedding vector for the query

The method orchestrates multiple search strategies including full-text search, semantic similarity search, and graph traversal, then applies reranking to produce a unified result set.

**Section sources**
- [search.py](file://graphiti_core/search/search.py#L68-L519)

### close Method

The `close` method safely terminates the connection to the graph database.

```python
async def close(self):
    """
    Close the connection to the Neo4j database.
    
    This method safely closes the driver connection to the Neo4j database.
    It should be called when the Graphiti instance is no longer needed or
    when the application is shutting down.
    """
```

This method should be called as part of application cleanup to ensure proper resource release and transaction completion.

**Section sources**
- [graphiti.py](file://graphiti_core/graphiti.py#L289-L319)

## Driver Interface and Implementations

### GraphDriver Interface

The `GraphDriver` abstract base class defines the interface for database connectivity and operations.

```python
class GraphDriver(ABC):
    provider: GraphProvider
    fulltext_syntax: str = ''
    _database: str
    search_interface: SearchInterface | None = None
    graph_operations_interface: GraphOperationsInterface | None = None

    @abstractmethod
    def execute_query(self, cypher_query_: str, **kwargs: Any) -> Coroutine:
        raise NotImplementedError()

    @abstractmethod
    def session(self, database: str | None = None) -> GraphDriverSession:
        raise NotImplementedError()

    @abstractmethod
    def close(self):
        raise NotImplementedError()

    @abstractmethod
    def delete_all_indexes(self) -> Coroutine:
        raise NotImplementedError()
```

The interface supports multiple query execution modes, session management, and database-specific full-text search syntax handling.

**Section sources**
- [driver.py](file://graphiti_core/driver/driver.py#L73-L116)

### Neo4j Driver

The `Neo4jDriver` provides connectivity to Neo4j graph databases using the official Neo4j Python driver.

```python
class Neo4jDriver(GraphDriver):
    provider = GraphProvider.NEO4J

    def __init__(
        self,
        uri: str,
        user: str | None,
        password: str | None,
        database: str = 'neo4j',
    ):
```

**Connection Parameters:**
- `uri`: Neo4j database URI (e.g., bolt://localhost:7687)
- `user`: Authentication username
- `password`: Authentication password
- `database`: Target database name (default: 'neo4j')

The driver uses Neo4j's native Cypher query language and supports both direct query execution and session-based transactions.

**Section sources**
- [neo4j_driver.py](file://graphiti_core/driver/neo4j_driver.py#L29-L75)

### FalkorDB Driver

The `FalkorDriver` enables connectivity to FalkorDB, a Redis-based graph database.

```python
class FalkorDriver(GraphDriver):
    provider = GraphProvider.FALKORDB

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        username: str | None = None,
        password: str | None = None,
        falkor_db: FalkorDB | None = None,
        database: str = 'default_db',
    ):
```

**Connection Parameters:**
- `host`: FalkorDB server hostname (default: 'localhost')
- `port`: Server port (default: 6379)
- `username`: Optional authentication username
- `password`: Optional authentication password
- `falkor_db`: Existing FalkorDB client instance (for connection reuse)
- `database`: Database name (multi-tenant graphs)

The driver implements RedisSearch-like syntax for full-text queries and includes text sanitization to handle special characters.

**Section sources**
- [falkordb_driver.py](file://graphiti_core/driver/falkordb_driver.py#L112-L309)

### Kuzu Driver

The `KuzuDriver` provides integration with Kuzu, an embedded analytical graph database.

```python
class KuzuDriver(GraphDriver):
    provider: GraphProvider = GraphProvider.KUZU

    def __init__(
        self,
        db: str = ':memory:',
        max_concurrent_queries: int = 1,
    ):
```

**Connection Parameters:**
- `db`: Database path ('memory' for in-memory database)
- `max_concurrent_queries`: Maximum concurrent query limit

Kuzu requires an explicit schema definition, which the driver automatically creates with predefined node and relationship tables optimized for the Graphiti data model.

**Section sources**
- [kuzu_driver.py](file://graphiti_core/driver/kuzu_driver.py#L93-L177)

### Neptune Driver

The `NeptuneDriver` connects to Amazon Neptune graph databases with integrated OpenSearch for hybrid search capabilities.

```python
class NeptuneDriver(GraphDriver):
    provider: GraphProvider = GraphProvider.NEPTUNE

    def __init__(self, host: str, aoss_host: str, port: int = 8182, aoss_port: int = 443):
```

**Connection Parameters:**
- `host`: Neptune endpoint (neptune-db:// or neptune-graph://)
- `aoss_host`: Amazon OpenSearch Service endpoint
- `port`: Neptune port (default: 8182)
- `aoss_port`: OpenSearch port (default: 443)

The driver integrates AWS authentication via boto3 and manages separate indices for nodes, edges, episodes, and communities in OpenSearch to enable efficient hybrid search operations.

**Section sources**
- [neptune_driver.py](file://graphiti_core/driver/neptune_driver.py#L109-L300)

## LLM Client Abstraction

### LLMClient Interface

The `LLMClient` abstract base class defines the interface for large language model interactions.

```python
class LLMClient(ABC):
    def __init__(self, config: LLMConfig | None, cache: bool = False):
        self.config = config
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        self.cache_enabled = cache
        self.tracer: Tracer = NoOpTracer()
```

The interface supports response caching, distributed tracing, and retry logic for robust LLM interactions.

**Section sources**
- [client.py](file://graphiti_core/llm_client/client.py#L66-L243)

### OpenAI Client

The `OpenAIClient` provides integration with OpenAI's language models.

```python
class OpenAIClient(BaseOpenAIClient):
    def __init__(
        self,
        config: LLMConfig | None = None,
        cache: bool = False,
        client: typing.Any = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        reasoning: str = DEFAULT_REASONING,
        verbosity: str = DEFAULT_VERBOSITY,
    ):
```

Supports both regular completions and structured output via OpenAI's beta parsing API. The client handles API key management, request formatting, and response parsing.

**Section sources**
- [openai_client.py](file://graphiti_core/llm_client/openai_client.py#L27-L106)

### Anthropic Client

The `AnthropicClient` integrates with Anthropic's Claude models.

```python
class AnthropicClient(LLMClient):
    def __init__(
        self,
        config: LLMConfig | None = None,
        cache: bool = False,
        client: typing.Any = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ):
```

Implements Anthropic-specific request formatting and handles the differences in API structure compared to other providers.

**Section sources**
- [anthropic_client.py](file://graphiti_core/llm_client/anthropic_client.py)

### Gemini Client

The `GeminiClient` provides connectivity to Google's Gemini models.

```python
class GeminiClient(LLMClient):
    def __init__(
        self,
        config: LLMConfig | None = None,
        cache: bool = False,
        client: typing.Any = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ):
```

Handles Google Cloud authentication and adapts the Gemini API's request/response format to the unified LLMClient interface.

**Section sources**
- [gemini_client.py](file://graphiti_core/llm_client/gemini_client.py)

### Groq Client

The `GroqClient` integrates with Groq's high-performance LLM inference service.

```python
class GroqClient(LLMClient):
    def __init__(
        self,
        config: LLMConfig | None = None,
        cache: bool = False,
        client: typing.Any = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ):
```

Optimized for Groq's ultra-fast inference capabilities, with appropriate request batching and rate limiting.

**Section sources**
- [groq_client.py](file://graphiti_core/llm_client/groq_client.py)

## Embedder Interface

### EmbedderClient Interface

The `EmbedderClient` abstract base class defines the interface for embedding generation.

```python
class EmbedderClient(ABC):
    @abstractmethod
    async def create(
        self, input_data: str | list[str] | Iterable[int] | Iterable[Iterable[int]]
    ) -> list[float]:
        pass

    async def create_batch(self, input_data_list: list[str]) -> list[list[float]]:
        raise NotImplementedError()
```

The interface supports both single and batch embedding generation, with consistent vector dimensionality across implementations.

**Section sources**
- [client.py](file://graphiti_core/embedder/client.py#L30-L39)

### OpenAI Embedder

The `OpenAIEmbedder` generates embeddings using OpenAI's embedding models.

```python
class OpenAIEmbedder(EmbedderClient):
    def __init__(self, config: EmbedderConfig | None = None):
        if config is None:
            config = OpenAIEmbedderConfig()
        self.config = config
        self.client = AsyncOpenAI(api_key=config.api_key, base_url=config.base_url)
```

Supports configurable embedding dimensions and model selection through the configuration object.

**Section sources**
- [openai.py](file://graphiti_core/embedder/openai.py)

### Azure OpenAI Embedder

The `AzureOpenAIEmbedderClient` provides embedding generation through Azure's OpenAI service.

```python
class AzureOpenAIEmbedderClient(EmbedderClient):
    def __init__(self, config: AzureOpenAIEmbedderConfig | None = None):
        if config is None:
            config = AzureOpenAIEmbedderConfig()
        self.config = config
        self.client = AsyncAzureOpenAI(
            api_key=config.api_key,
            azure_endpoint=config.azure_endpoint,
            api_version=config.api_version,
        )
```

Handles Azure-specific authentication and endpoint configuration for enterprise deployments.

**Section sources**
- [azure_openai.py](file://graphiti_core/embedder/azure_openai.py)

### Gemini Embedder

The `GeminiEmbedder` generates embeddings using Google's Gemini embedding models.

```python
class GeminiEmbedder(EmbedderClient):
    def __init__(self, config: EmbedderConfig | None = None):
        if config is None:
            config = EmbedderConfig()
        self.config = config
        self.client = genai.GenerativeModel(config.model)
```

Integrates with Google's Generative AI SDK for embedding generation with proper error handling and retry logic.

**Section sources**
- [gemini.py](file://graphiti_core/embedder/gemini.py)

### Voyage AI Embedder

The `VoyageAIEmbedder` provides access to Voyage AI's specialized embedding models.

```python
class VoyageAIEmbedder(EmbedderClient):
    def __init__(self, config: VoyageAIEmbedderConfig | None = None):
        if config is None:
            config = VoyageAIEmbedderConfig()
        self.config = config
        self.client = voyageai.Client(api_key=config.api_key)
```

Optimized for Voyage AI's high-performance embedding models with support for their unique API features.

**Section sources**
- [voyage.py](file://graphiti_core/embedder/voyage.py)

## Cross-Encoder Interface

### CrossEncoderClient Interface

The `CrossEncoderClient` abstract base class defines the interface for reranking models.

```python
class CrossEncoderClient(ABC):
    @abstractmethod
    async def rank(self, query: str, passages: list[str]) -> list[tuple[str, float]]:
        """
        Rank the given passages based on their relevance to the query.
        
        Args:
            query: The query string
            passages: A list of passages to rank
            
        Returns:
            List of tuples containing (passage, score) sorted by relevance
        """
        pass
```

The interface enables reranking of search results to improve relevance through cross-attention mechanisms.

**Section sources**
- [client.py](file://graphiti_core/cross_encoder/client.py#L20-L41)

### OpenAI Reranker

The `OpenAIRerankerClient` uses OpenAI's models for reranking search results.

```python
class OpenAIRerankerClient(CrossEncoderClient):
    def __init__(self, config: LLMConfig | None = None):
        if config is None:
            config = LLMConfig()
        self.config = config
        self.client = AsyncOpenAI(api_key=config.api_key, base_url=config.base_url)
```

Implements prompt engineering techniques to leverage general-purpose LLMs for reranking tasks.

**Section sources**
- [openai_reranker_client.py](file://graphiti_core/cross_encoder/openai_reranker_client.py)

### BGE Reranker

The `BGERerankerClient` uses specialized BGE (Bidirectional Guided Encoder) models for efficient reranking.

```python
class BGERerankerClient(CrossEncoderClient):
    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        self.model_name = model_name
        self.model = FlagReranker(model_name, use_fp16=True)
```

Provides high-performance local reranking with pre-trained models optimized for retrieval tasks.

**Section sources**
- [bge_reranker_client.py](file://graphiti_core/cross_encoder/bge_reranker_client.py)

### Gemini Reranker

The `GeminiRerankerClient` leverages Google's Gemini models for reranking operations.

```python
class GeminiRerankerClient(CrossEncoderClient):
    def __init__(self, config: LLMConfig | None = None):
        if config is None:
            config = LLMConfig()
        self.config = config
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel('models/gemini-pro')
```

Integrates with Google's ecosystem for reranking with appropriate authentication and rate limiting.

**Section sources**
- [gemini_reranker_client.py](file://graphiti_core/cross_encoder/gemini_reranker_client.py)

## Search Configuration

### SearchConfig Model

The `SearchConfig` class defines comprehensive search parameters for hybrid retrieval.

```python
class SearchConfig(BaseModel):
    node_config: NodeSearchConfig | None = None
    edge_config: EdgeSearchConfig | None = None
    episode_config: EpisodeSearchConfig | None = None
    community_config: CommunitySearchConfig | None = None
    limit: int = DEFAULT_SEARCH_LIMIT
    reranker_min_score: float = 0.0
```

The configuration supports independent settings for nodes, edges, episodes, and communities, enabling fine-grained control over search behavior.

**Section sources**
- [search_config.py](file://graphiti_core/search/search_config.py)

### Search Methods

The framework supports multiple search methods that can be combined for hybrid retrieval:

**Node Search Methods:**
- `bm25`: Full-text search using BM25 ranking
- `cosine_similarity`: Semantic similarity search via vector embeddings
- `bfs`: Graph traversal via breadth-first search

**Edge Search Methods:**
- `bm25`: Full-text search on edge properties
- `cosine_similarity`: Semantic similarity on edge embeddings
- `bfs`: Relationship expansion from source nodes

**Reranking Strategies:**
- `rrf`: Reciprocal Rank Fusion for combining multiple result sets
- `cross_encoder`: Relevance scoring using cross-attention models
- `mmr`: Maximal Marginal Relevance for diversity optimization
- `episode_mentions`: Popularity based on episode references
- `node_distance`: Proximity to a center node in the graph

These methods can be combined in the search configuration to create sophisticated retrieval pipelines tailored to specific use cases.

**Section sources**
- [search_config.py](file://graphiti_core/search/search_config.py)
- [search.py](file://graphiti_core/search/search.py)

## Usage Examples

### Basic Initialization

```python
# Initialize with Neo4j connection
graphiti = Graphiti(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

# Initialize with custom FalkorDB driver
falkor_driver = FalkorDriver(
    host="localhost",
    port=6379,
    database="my_graph"
)
graphiti = Graphiti(graph_driver=falkor_driver)
```

### Custom Client Injection

```python
# Create custom LLM client
llm_client = OpenAIClient(
    config=LLMConfig(
        api_key="your-api-key",
        model="gpt-4-turbo",
        temperature=0.7
    ),
    cache=True
)

# Create custom embedder
embedder = OpenAIEmbedder(
    config=OpenAIEmbedderConfig(
        api_key="your-api-key",
        model="text-embedding-3-large"
    )
)

# Initialize Graphiti with custom clients
graphiti = Graphiti(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    llm_client=llm_client,
    embedder=embedder
)
```

### Adding Content

```python
# Add a text episode
await graphiti.add_episode(
    name="Conversation",
    episode_body="Alice is the CEO of TechCorp. Bob is the CTO.",
    source_description="chat transcript",
    reference_time=datetime.now(timezone.utc),
    group_id="company_x"
)

# Add structured JSON episode
await graphiti.add_episode(
    name="User Profile",
    episode_body=json.dumps({
        "name": "Charlie",
        "role": "Engineer",
        "skills": ["Python", "JavaScript"]
    }),
    source=EpisodeType.json,
    source_description="user data",
    reference_time=datetime.now(timezone.utc)
)
```

### Advanced Search

```python
# Perform hybrid search with custom configuration
from graphiti_core.search.search_config_recipes import COMBINED_HYBRID_SEARCH_CROSS_ENCODER

results = await graphiti.search(
    query="Who are the key leaders at TechCorp?",
    config=COMBINED_HYBRID_SEARCH_CROSS_ENCODER,
    group_ids=["company_x"],
    center_node_uuid="alice-node-uuid"
)

# Access different result types
print(f"Found {len(results.nodes)} nodes")
print(f"Found {len(results.edges)} relationships")
print(f"Found {len(results.episodes)} relevant episodes")
```

**Section sources**
- [quickstart_neo4j.py](file://examples/quickstart/quickstart_neo4j.py)
- [quickstart_falkordb.py](file://examples/quickstart/quickstart_falkordb.py)
- [quickstart_neptune.py](file://examples/quickstart/quickstart_neptune.py)

## Error Handling

The Graphiti framework implements comprehensive error handling across all components:

### Connection Errors
- Database connection failures raise appropriate exceptions with diagnostic information
- LLM provider connectivity issues are handled with retry logic
- Network timeouts are managed with configurable retry policies

### Validation Errors
- Input validation is performed for all public methods
- Configuration validation ensures proper setup before operations
- Type checking prevents invalid data from entering the graph

### Rate Limiting
- LLM client includes automatic rate limit detection and backoff
- Database operations include circuit breaker patterns for high load
- Concurrent operation limits prevent resource exhaustion

### Recovery Strategies
- Failed operations provide sufficient context for debugging
- Partial success scenarios are handled gracefully
- Transactional integrity is maintained across distributed operations

The framework uses Python's exception hierarchy with custom exception types defined in the `errors.py` module to provide clear error semantics for different failure modes.

**Section sources**
- [errors.py](file://graphiti_core/errors.py)
- [client.py](file://graphiti_core/llm_client/client.py#L31)
- [graphiti.py](file://graphiti_core/graphiti.py)