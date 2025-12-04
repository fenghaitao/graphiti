# Community Summarization

## Overview

This document describes the hierarchical summarization approach used to generate community summaries from entity nodes in detected communities.

## Problem Statement

When a community contains multiple entities, we need to generate a single coherent summary that captures the essence of the entire community. Simply concatenating all entity summaries would be too long and lose important context. We need a hierarchical approach that:

1. Preserves important details from peripheral entities
2. Emphasizes central themes from hub entities
3. Creates a natural information flow from context to main ideas
4. Scales efficiently to communities of any size

## Solution: Degree-Based Tournament Summarization

### Step 1: Sort by Node Degree

Entities are sorted by their degree (number of connections) in ascending order:

```python
community_cluster_sorted = sorted(
    community_cluster, 
    key=lambda e: node_degrees.get(e.uuid, 0)
)
```

**Why ascending order?**
- Peripheral nodes (low degree) come first
- Hub nodes (high degree) come last
- Creates a natural progression: supporting details → main themes

**Example:**
```
Original: [Hub(deg=5), Leaf1(deg=1), Leaf2(deg=1), Bridge(deg=3)]
Sorted:   [Leaf1(deg=1), Leaf2(deg=1), Bridge(deg=3), Hub(deg=5)]
```

### Step 2: Tournament-Style Pairing

Summaries are combined in pairs using adjacent pairing:

```python
while length > 1:
    pairs = []
    for i in range(0, length - 1, 2):
        pairs.append((summaries[i], summaries[i + 1]))
    
    new_summaries = await process_pairs_in_parallel(pairs)
    
    if length % 2 == 1:
        new_summaries.append(summaries[-1])
    
    summaries = new_summaries
    length = len(summaries)
```

**Why adjacent pairing?**
- Pairs nodes with similar degrees
- Peripheral details combine first
- Central themes emerge at higher levels
- Creates balanced tree structure

### Step 3: Hierarchical Combination

**Example with 4 entities:**

```
Initial (sorted by degree):
  A (deg=1): "Handles DMA transfers"
  B (deg=1): "Manages interrupts"  
  C (deg=3): "Controls PCIe bus"
  D (deg=4): "Main system controller"

Round 1: Pair adjacent
  (A, B) → AB: "Handles DMA transfers and manages interrupts"
  (C, D) → CD: "Controls PCIe bus as main system controller"

Round 2: Pair adjacent
  (AB, CD) → ABCD: "System controller managing PCIe bus, DMA, and interrupts"

Final: ABCD summary
```

**Information flow:**
1. Peripheral details (A, B) combine into supporting context
2. Central concepts (C, D) combine into main theme
3. Supporting context merges with main theme
4. Result: Hierarchical summary with proper emphasis

## Implementation Details

### Degree Calculation

Node degrees are computed from the projection (adjacency list) during community detection:

```python
node_degrees = {uuid: len(neighbors) for uuid, neighbors in projection.items()}
```

This information is passed through the call chain:
- `get_community_clusters()` → returns `(cluster, node_degrees)` tuples
- `build_communities()` → passes degrees to `build_community()`
- `build_community()` → uses degrees for sorting

### LLM Integration

Each pair of summaries is combined using an LLM call:

```python
llm_response = await llm_client.generate_response(
    prompt_library.summarize_nodes.summarize_pair(context),
    response_model=Summary,
)
```

**Parallelization:**
- All pairs in a round are processed in parallel
- Reduces total LLM calls from O(N) sequential to O(log N) rounds
- Each round processes multiple pairs concurrently

### Odd Number Handling

When there's an odd number of summaries, the last one is carried forward:

```python
if length % 2 == 1:
    new_summaries.append(summaries[-1])
```

This ensures all information is preserved through the tournament.

## Benefits

### 1. Natural Hierarchy

Peripheral nodes provide context, hub nodes provide main themes:

```
Peripheral: "Handles specific DMA channel 0"
           + "Handles specific DMA channel 1"
           = "Handles DMA channels"

Hub:        "Main PCIe controller"
           + "Handles DMA channels"
           = "PCIe controller with DMA support"
```

### 2. Scalability

Tournament structure scales logarithmically:
- 4 entities: 2 rounds (4→2→1)
- 8 entities: 3 rounds (8→4→2→1)
- 16 entities: 4 rounds (16→8→4→2→1)

### 3. Parallelization

Each round processes pairs in parallel:
- Round 1: Process N/2 pairs concurrently
- Round 2: Process N/4 pairs concurrently
- Total time: O(log N) rounds × LLM latency

### 4. Deterministic Results

Sorting by degree ensures consistent results:
- Same community always produces same summary
- No randomness in pairing order
- Reproducible for testing and debugging

## Comparison with Alternatives

### Random Pairing
❌ No semantic structure
❌ Hub nodes might be paired early
❌ Non-deterministic results

### Sequential Combination
❌ O(N) LLM calls (no parallelization)
❌ Later entities have less influence
❌ Summary grows too long

### Degree-Based Tournament (Current)
✅ Semantic structure (periphery → center)
✅ O(log N) rounds with parallelization
✅ Balanced influence from all entities
✅ Deterministic and testable

## Limitations and Future Work

### Current Limitation: No Edge Awareness

The current approach sorts by degree but doesn't follow actual graph edges:

```
Graph:     A---B---C
           |   |   |
           D---E---F

Sorted:    [A, C, D, F, B, E]  (by degree)
Paired:    (A,C) (D,F) (B,E)   (not necessarily connected!)
```

Nodes paired together might not be directly connected in the graph.

### Future Enhancement: Graph-Aware Traversal

True hierarchical summarization would:

1. Start from peripheral nodes (degree 1)
2. Follow edges inward toward the center
3. Combine summaries along paths
4. Ensure paired nodes are actually connected

**Example:**
```
Graph:     A---B---C
               |
               D

Traversal: A→B, C→B, D→B (all paths lead to hub B)
Pairing:   (A,B), (C,B), (D,B) (all connected!)
```

This would require:
- Passing adjacency information to `build_community()`
- Implementing graph traversal algorithm
- Handling multiple paths and cycles

**Deferred because:**
- Current approach works well in practice
- Degree is a good proxy for centrality
- Graph-aware approach adds complexity
- Would need careful handling of cycles and multiple paths

## Testing

The summarization logic is tested indirectly through:
- Community detection tests (verify correct clustering)
- Integration tests (verify summaries are generated)
- Manual inspection of generated summaries

Future work could add:
- Unit tests for pairing logic
- Tests for odd/even number of entities
- Validation of summary quality

## Configuration

### Concurrency Limit

Maximum concurrent LLM calls for summarization:

```python
MAX_COMMUNITY_BUILD_CONCURRENCY = 10
```

This prevents overwhelming the LLM API while still allowing parallelization.

### Summary Generation

After combining all entity summaries, a final step generates a community name:

```python
name = await generate_summary_description(llm_client, summary)
```

This creates a short, descriptive name for the community node.

## Example End-to-End

**Input Community:**
```
Entities (sorted by degree):
1. DMA_CH0 (deg=1): "DMA channel 0 for memory transfers"
2. DMA_CH1 (deg=1): "DMA channel 1 for memory transfers"  
3. PCIe_BUS (deg=3): "PCIe bus controller for device communication"
4. SYS_CTRL (deg=5): "Main system controller managing all components"
```

**Round 1:**
```
Pair (DMA_CH0, DMA_CH1):
  → "DMA channels for memory transfers"

Pair (PCIe_BUS, SYS_CTRL):
  → "System controller managing PCIe bus and devices"
```

**Round 2:**
```
Pair (DMA_summary, PCIe_summary):
  → "System controller managing PCIe devices and DMA memory transfers"
```

**Final:**
```
Community Name: "System Controller with PCIe and DMA"
Community Summary: "System controller managing PCIe devices and DMA memory transfers"
```

The final summary emphasizes the main controller role while preserving details about PCIe and DMA functionality.
