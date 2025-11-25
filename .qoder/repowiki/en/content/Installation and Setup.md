# Installation and Setup

<cite>
**Referenced Files in This Document**   
- [README.md](file://README.md)
- [pyproject.toml](file://pyproject.toml)
- [graphiti.py](file://graphiti_core/graphiti.py)
- [neo4j_driver.py](file://graphiti_core/driver/neo4j_driver.py)
- [falkordb_driver.py](file://graphiti_core/driver/falkordb_driver.py)
- [kuzu_driver.py](file://graphiti_core/driver/kuzu_driver.py)
- [neptune_driver.py](file://graphiti_core/driver/neptune_driver.py)
- [config.py](file://graphiti_core/llm_client/config.py)
- [openai_client.py](file://graphiti_core/llm_client/openai_client.py)
- [gemini_client.py](file://graphiti_core/llm_client/gemini_client.py)
- [azure_openai_client.py](file://graphiti_core/llm_client/azure_openai_client.py)
- [telemetry.py](file://graphiti_core/telemetry/telemetry.py)
- [quickstart_neo4j.py](file://examples/quickstart/quickstart_neo4j.py)
- [quickstart_falkordb.py](file://examples/quickstart/quickstart_falkordb.py)
- [quickstart_neptune.py](file://examples/quickstart/quickstart_neptune.py)
</cite>

## Table of Contents
1. [Installation](#installation)
2. [Graph Database Configuration](#graph-database-configuration)
3. [LLM Provider Configuration](#llm-provider-configuration)
4. [Telemetry Setup](#telemetry-setup)
5. [Initialization Examples](#initialization-examples)
6. [Platform-Specific Considerations](#platform-specific-considerations)
7. [Troubleshooting](#troubleshooting)

## Installation

Graphiti can be installed using either pip or uv package managers. The framework requires Python 3.10 or higher and has different installation options depending on the desired graph database backend and LLM providers.

### Basic Installation

To install the core Graphiti framework with default dependencies:

```bash
pip install graphiti-core
```

or with uv:

```bash
uv add graphiti-core
```

### Database-Specific Installation

Graphiti supports multiple graph database backends, each requiring specific installation extras:

**For Neo4j (default):**
```bash
pip install graphiti-core
```

**For FalkorDB:**
```bash
pip install graphiti-core[falkordb]
```

or with uv:
```bash
uv add graphiti-core[falkordb]
```

**For Kuzu:**
```bash
pip install graphiti-core[kuzu]
```

or with uv:
```bash
uv add graphiti-core[kuzu]
```

**For Amazon Neptune:**
```bash
pip install graphiti-core[neptune]
```

or with uv:
```bash
uv add graphiti-core[neptune]
```

### LLM Provider Installation

Graphiti supports various LLM providers as optional extras:

**For Anthropic:**
```bash
pip install graphiti-core[anthropic]
```

**For Groq:**
```bash
pip install graphiti-core[groq]
```

**For Google Gemini:**
```bash
pip install graphiti-core[google-genai]
```

**For multiple providers:**
```bash
pip install graphiti-core[anthropic,groq,google-genai]
```

**For combined database and LLM providers:**
```bash
pip install graphiti-core[falkordb,anthropic,google-genai]
```

**Section sources**
- [README.md](file://README.md#L116-L207)
- [pyproject.toml](file://pyproject.toml#L28-L37)

## Graph Database Configuration

Graphiti supports multiple graph database backends, each with specific configuration requirements.

### Neo4j Configuration

Neo4j is the default database backend. To connect to Neo4j:

```python
from graphiti_core import Graphiti

# Basic connection
graphiti = Graphiti(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="your_password"
)
```

For custom database names:
```python
from graphiti_core.driver.neo4j_driver import Neo4jDriver

driver = Neo4jDriver(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="your_password",
    database="my_custom_database"
)

graphiti = Graphiti(graph_driver=driver)
```

**Section sources**
- [README.md](file://README.md#L272-L297)
- [neo4j_driver.py](file://graphiti_core/driver/neo4j_driver.py#L32-L44)

### FalkorDB Configuration

To use FalkorDB as the backend:

```python
from graphiti_core import Graphiti
from graphiti_core.driver.falkordb_driver import FalkorDriver

driver = FalkorDriver(
    host="localhost",
    port=6379,
    username="falkor_user",
    password="falkor_password",
    database="my_custom_graph"
)

graphiti = Graphiti(graph_driver=driver)
```

To run FalkorDB locally with Docker:
```bash
docker run -p 6379:6379 -p 3000:3000 -it --rm falkordb/falkordb:latest
```

**Section sources**
- [README.md](file://README.md#L300-L317)
- [falkordb_driver.py](file://graphiti_core/driver/falkordb_driver.py#L116-L124)

### Kuzu Configuration

To use Kuzu as the backend:

```python
from graphiti_core import Graphiti
from graphiti_core.driver.kuzu_driver import KuzuDriver

driver = KuzuDriver(db="/tmp/graphiti.kuzu")
graphiti = Graphiti(graph_driver=driver)
```

**Section sources**
- [README.md](file://README.md#L319-L330)
- [kuzu_driver.py](file://graphiti_core/driver/kuzu_driver.py#L97-L101)

### Amazon Neptune Configuration

To use Amazon Neptune as the backend:

```python
from graphiti_core import Graphiti
from graphiti_core.driver.neptune_driver import NeptuneDriver

driver = NeptuneDriver(
    host="neptune-db://your-endpoint",
    aoss_host="your-aoss-host",
    port=8182,
    aoss_port=443
)

graphiti = Graphiti(graph_driver=driver)
```

**Section sources**
- [README.md](file://README.md#L332-L354)
- [neptune_driver.py](file://graphiti_core/driver/neptune_driver.py#L112-L137)

## LLM Provider Configuration

Graphiti supports multiple LLM providers with specific configuration requirements.

### OpenAI Configuration

OpenAI is the default LLM provider. Ensure your API key is set in the environment:

```bash
export OPENAI_API_KEY=your_api_key
```

Basic initialization:
```python
from graphiti_core import Graphiti

graphiti = Graphiti(
    "bolt://localhost:7687",
    "neo4j",
    "password"
)
```

**Section sources**
- [README.md](file://README.md#L123-L124)
- [openai_client.py](file://graphiti_core/llm_client/openai_client.py#L38-L64)

### Azure OpenAI Configuration

For Azure OpenAI, configure separate endpoints for LLM and embedding services:

```python
from openai import AsyncAzureOpenAI
from graphiti_core import Graphiti
from graphiti_core.llm_client import LLMConfig, OpenAIClient
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig

# Azure configuration
api_key = "your-api-key"
api_version = "your-api-version"
llm_endpoint = "https://your-llm-resource.openai.azure.com/"
embedding_endpoint = "https://your-embedding-resource.openai.azure.com/"

# Create Azure clients
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

# Initialize Graphiti with Azure
graphiti = Graphiti(
    "bolt://localhost:7687",
    "neo4j",
    "password",
    llm_client=OpenAIClient(
        config=LLMConfig(
            small_model="gpt-4.1-nano",
            model="gpt-4.1-mini"
        ),
        client=llm_client_azure
    ),
    embedder=OpenAIEmbedder(
        config=OpenAIEmbedderConfig(
            embedding_model="text-embedding-3-small-deployment"
        ),
        client=embedding_client_azure
    )
)
```

**Section sources**
- [README.md](file://README.md#L356-L427)
- [azure_openai_client.py](file://graphiti_core/llm_client/azure_openai_client.py#L36-L43)

### Google Gemini Configuration

To use Google Gemini as the LLM provider:

```python
from graphiti_core import Graphiti
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig

# Initialize with Gemini
graphiti = Graphiti(
    "bolt://localhost:7687",
    "neo4j",
    "password",
    llm_client=GeminiClient(
        config=LLMConfig(
            api_key="your-google-api-key",
            model="gemini-2.0-flash"
        )
    ),
    embedder=GeminiEmbedder(
        config=GeminiEmbedderConfig(
            api_key="your-google-api-key",
            embedding_model="embedding-001"
        )
    )
)
```

**Section sources**
- [README.md](file://README.md#L432-L482)
- [gemini_client.py](file://graphiti_core/llm_client/gemini_client.py#L93-L122)

### Ollama (Local LLM) Configuration

To use Ollama for running local LLMs:

```python
from graphiti_core import Graphiti
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig

# Configure Ollama
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
    )
)
```

Ensure Ollama is running and models are pulled:
```bash
ollama serve
ollama pull deepseek-r1:7b
ollama pull nomic-embed-text
```

**Section sources**
- [README.md](file://README.md#L488-L535)

## Telemetry Setup

Graphiti collects anonymous usage statistics by default to help improve the framework.

### What Data is Collected

When you initialize a Graphiti instance, the following anonymous data is collected:

- **Anonymous identifier**: A randomly generated UUID stored locally
- **System information**: Operating system, Python version, and system architecture
- **Graphiti version**: The version you're using
- **Configuration choices**:
  - LLM provider type (OpenAI, Azure, Anthropic, etc.)
  - Database backend (Neo4j, FalkorDB, Kuzu, Amazon Neptune)
  - Embedder provider (OpenAI, Azure, Voyage, etc.)

### What Data is NOT Collected

Graphiti does not collect:
- Personal information or identifiers
- API keys or credentials
- Your actual data, queries, or graph content
- IP addresses or hostnames
- File paths or system-specific information
- Any content from your episodes, nodes, or edges

### Disabling Telemetry

Telemetry is opt-out and can be disabled in several ways:

**Option 1: Environment Variable**
```bash
export GRAPHITI_TELEMETRY_ENABLED=false
```

**Option 2: Shell Profile**
```bash
# For bash users
echo 'export GRAPHITI_TELEMETRY_ENABLED=false' >> ~/.bashrc

# For zsh users
echo 'export GRAPHITI_TELEMETRY_ENABLED=false' >> ~/.zshrc
```

**Option 3: Python Session**
```python
import os
os.environ['GRAPHITI_TELEMETRY_ENABLED'] = 'false'

from graphiti_core import Graphiti
graphiti = Graphiti(...)
```

**Section sources**
- [README.md](file://README.md#L545-L619)
- [telemetry.py](file://graphiti_core/telemetry/telemetry.py#L29-L37)

## Initialization Examples

### Basic Neo4j Initialization

```python
from graphiti_core import Graphiti

# Initialize with Neo4j
graphiti = Graphiti(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

# Build indices and constraints (one-time setup)
await graphiti.build_indices_and_constraints()
```

**Section sources**
- [quickstart_neo4j.py](file://examples/quickstart/quickstart_neo4j.py#L67-L71)

### FalkorDB Initialization with Custom Driver

```python
from graphiti_core import Graphiti
from graphiti_core.driver.falkordb_driver import FalkorDriver

# Create custom driver
driver = FalkorDriver(
    host="localhost",
    port=6379,
    username="falkor_user",
    password="falkor_password"
)

# Initialize Graphiti
graphiti = Graphiti(graph_driver=driver)
await graphiti.build_indices_and_constraints()
```

**Section sources**
- [quickstart_falkordb.py](file://examples/quickstart/quickstart_falkordb.py#L75-L78)

### Neptune Initialization

```python
from graphiti_core import Graphiti
from graphiti_core.driver.neptune_driver import NeptuneDriver

# Initialize Neptune driver
driver = NeptuneDriver(
    host="neptune-db://your-endpoint",
    aoss_host="your-aoss-host"
)

# Initialize Graphiti
graphiti = Graphiti(graph_driver=driver)
await graphiti.build_indices_and_constraints()
```

**Section sources**
- [quickstart_neptune.py](file://examples/quickstart/quickstart_neptune.py#L71-L73)

## Platform-Specific Considerations

### Docker Environment

When running in Docker, ensure proper network configuration for database connections. For local development with FalkorDB:

```dockerfile
# Example Docker setup
docker run -p 6379:6379 -p 3000:3000 -it --rm falkordb/falkordb:latest
```

Ensure your application container can reach the database container on the appropriate ports.

### Local Development Environment

For local development, consider the following:

1. **Environment Variables**: Use .env files to manage credentials
2. **Database Setup**: Use Neo4j Desktop for easy Neo4j management
3. **Resource Limits**: Adjust SEMAPHORE_LIMIT for LLM rate limiting

```bash
# Control concurrency to avoid LLM rate limits
export SEMAPHORE_LIMIT=10
```

**Section sources**
- [README.md](file://README.md#L135-L138)
- [README.md](file://README.md#L209-L219)

## Troubleshooting

### Missing Dependencies

If you encounter import errors for specific database drivers:

```bash
# For FalkorDB
pip install graphiti-core[falkordb]

# For Kuzu
pip install graphiti-core[kuzu]

# For Neptune
pip install graphiti-core[neptune]
```

The framework will raise specific import errors indicating which package is missing.

### Database Connectivity Problems

**For Neo4j:**
- Ensure Neo4j server is running
- Verify credentials and URI format
- Check that the database is accessible on port 7687

**For FalkorDB:**
- Ensure FalkorDB container is running
- Verify host and port configuration
- Check that Redis port 6379 is exposed

**For Neptune:**
- Verify AWS credentials and permissions
- Ensure VPC and security group configurations allow access
- Confirm AOSS (OpenSearch) endpoint is correctly configured

### LLM API Authentication Failures

**Common Issues:**
- Invalid API keys
- Incorrect endpoint URLs
- Missing environment variables

**Solutions:**
```bash
# Verify environment variables
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
echo $GOOGLE_API_KEY

# Test API connectivity
curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Rate Limiting:**
- Reduce SEMAPHORE_LIMIT value
- Implement retry logic
- Upgrade to higher-tier API plans

**Section sources**
- [README.md](file://README.md#L209-L219)
- [README.md](file://README.md#L123-L124)