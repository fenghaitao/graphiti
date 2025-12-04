#!/usr/bin/env python3
"""
Test cases for label propagation algorithm to verify convergence.
"""

from collections import defaultdict
from graphiti_core.utils.maintenance.community_operations import label_propagation


class Neighbor:
    """Mock Neighbor class for testing."""
    def __init__(self, node_uuid: str, edge_count: int):
        self.node_uuid = node_uuid
        self.edge_count = edge_count


def test_case(name: str, projection: dict, expected_clusters: int = None):
    """Run a test case and print results."""
    print(f"\n{'='*60}")
    print(f"Test: {name}")
    print(f"{'='*60}")
    print(f"Nodes: {len(projection)}")
    print(f"Edges: {sum(len(neighbors) for neighbors in projection.values())}")
    
    # Run label propagation (no iteration limit - testing convergence)
    clusters = label_propagation(projection)
    
    print(f"Result: {len(clusters)} clusters")
    for i, cluster in enumerate(clusters, 1):
        print(f"  Cluster {i}: {sorted(cluster)}")
    
    if expected_clusters is not None:
        status = "✓ PASS" if len(clusters) == expected_clusters else "✗ FAIL"
        print(f"Expected {expected_clusters} clusters: {status}")
    
    return clusters


# Test Case 1: Two nodes with bidirectional edge
print("\n" + "="*60)
print("TEST CASE 1: Two nodes (A ←→ B)")
print("="*60)
projection1 = {
    "A": [Neighbor("B", 2)],
    "B": [Neighbor("A", 2)],
}
test_case("Two nodes bidirectional", projection1, expected_clusters=1)


# Test Case 2: Three nodes in a line
print("\n" + "="*60)
print("TEST CASE 2: Three nodes in line (A ← B → C)")
print("="*60)
projection2 = {
    "A": [Neighbor("B", 1)],
    "B": [Neighbor("A", 1), Neighbor("C", 1)],
    "C": [Neighbor("B", 1)],
}
test_case("Three nodes line", projection2, expected_clusters=1)


# Test Case 3: Triangle (fully connected)
print("\n" + "="*60)
print("TEST CASE 3: Triangle (A ↔ B ↔ C ↔ A)")
print("="*60)
projection3 = {
    "A": [Neighbor("B", 1), Neighbor("C", 1)],
    "B": [Neighbor("A", 1), Neighbor("C", 1)],
    "C": [Neighbor("A", 1), Neighbor("B", 1)],
}
test_case("Triangle", projection3, expected_clusters=1)


# Test Case 4: Two separate pairs
print("\n" + "="*60)
print("TEST CASE 4: Two separate pairs (A-B) (C-D)")
print("="*60)
projection4 = {
    "A": [Neighbor("B", 1)],
    "B": [Neighbor("A", 1)],
    "C": [Neighbor("D", 1)],
    "D": [Neighbor("C", 1)],
}
test_case("Two separate pairs", projection4, expected_clusters=2)


# Test Case 5: Star topology (hub and spokes)
print("\n" + "="*60)
print("TEST CASE 5: Star (B,C,D,E all connect to A)")
print("="*60)
projection5 = {
    "A": [Neighbor("B", 1), Neighbor("C", 1), Neighbor("D", 1), Neighbor("E", 1)],
    "B": [Neighbor("A", 1)],
    "C": [Neighbor("A", 1)],
    "D": [Neighbor("A", 1)],
    "E": [Neighbor("A", 1)],
}
test_case("Star topology", projection5, expected_clusters=1)


# Test Case 6: Two clusters connected by weak link
print("\n" + "="*60)
print("TEST CASE 6: Two clusters with weak link")
print("  Cluster 1: A-B-C (strong)")
print("  Cluster 2: D-E-F (strong)")
print("  Weak link: C-D (1 edge)")
print("="*60)
projection6 = {
    "A": [Neighbor("B", 3)],
    "B": [Neighbor("A", 3), Neighbor("C", 3)],
    "C": [Neighbor("B", 3), Neighbor("D", 1)],
    "D": [Neighbor("C", 1), Neighbor("E", 3)],
    "E": [Neighbor("D", 3), Neighbor("F", 3)],
    "F": [Neighbor("E", 3)],
}
test_case("Two clusters weak link", projection6, expected_clusters=2)


# Test Case 7: Cycle (A → B → C → D → A)
print("\n" + "="*60)
print("TEST CASE 7: Cycle (A → B → C → D → A)")
print("="*60)
projection7 = {
    "A": [Neighbor("B", 1), Neighbor("D", 1)],
    "B": [Neighbor("A", 1), Neighbor("C", 1)],
    "C": [Neighbor("B", 1), Neighbor("D", 1)],
    "D": [Neighbor("C", 1), Neighbor("A", 1)],
}
test_case("Cycle", projection7, expected_clusters=1)


# Test Case 8: Asymmetric edges (different weights)
print("\n" + "="*60)
print("TEST CASE 8: Asymmetric edges")
print("  A → B (weight 5)")
print("  B → A (weight 1)")
print("="*60)
projection8 = {
    "A": [Neighbor("B", 5)],
    "B": [Neighbor("A", 1)],
}
test_case("Asymmetric edges", projection8, expected_clusters=1)


# Test Case 9: Isolated node
print("\n" + "="*60)
print("TEST CASE 9: Isolated node")
print("  A-B connected, C isolated")
print("="*60)
projection9 = {
    "A": [Neighbor("B", 1)],
    "B": [Neighbor("A", 1)],
    "C": [],
}
test_case("Isolated node", projection9, expected_clusters=2)


# Test Case 10: Complex graph (potential oscillation)
print("\n" + "="*60)
print("TEST CASE 10: Complex graph")
print("  Multiple interconnections")
print("="*60)
projection10 = {
    "A": [Neighbor("B", 2), Neighbor("C", 1)],
    "B": [Neighbor("A", 2), Neighbor("C", 2), Neighbor("D", 1)],
    "C": [Neighbor("A", 1), Neighbor("B", 2), Neighbor("D", 2)],
    "D": [Neighbor("B", 1), Neighbor("C", 2)],
}
test_case("Complex graph", projection10, expected_clusters=1)


# Test Case 11: Complete graph (everyone connected to everyone)
print("\n" + "="*60)
print("TEST CASE 11: Complete graph (K5)")
print("  All nodes connected to all others")
print("="*60)
projection11 = {
    "A": [Neighbor("B", 1), Neighbor("C", 1), Neighbor("D", 1), Neighbor("E", 1)],
    "B": [Neighbor("A", 1), Neighbor("C", 1), Neighbor("D", 1), Neighbor("E", 1)],
    "C": [Neighbor("A", 1), Neighbor("B", 1), Neighbor("D", 1), Neighbor("E", 1)],
    "D": [Neighbor("A", 1), Neighbor("B", 1), Neighbor("C", 1), Neighbor("E", 1)],
    "E": [Neighbor("A", 1), Neighbor("B", 1), Neighbor("C", 1), Neighbor("D", 1)],
}
test_case("Complete graph K5", projection11, expected_clusters=1)


# Test Case 12: Barbell (two complete graphs connected by single edge)
print("\n" + "="*60)
print("TEST CASE 12: Barbell graph")
print("  Two triangles connected by one edge")
print("="*60)
projection12 = {
    "A": [Neighbor("B", 3), Neighbor("C", 3), Neighbor("D", 1)],  # Bridge node
    "B": [Neighbor("A", 3), Neighbor("C", 3)],
    "C": [Neighbor("A", 3), Neighbor("B", 3)],
    "D": [Neighbor("A", 1), Neighbor("E", 3), Neighbor("F", 3)],  # Bridge node
    "E": [Neighbor("D", 3), Neighbor("F", 3)],
    "F": [Neighbor("D", 3), Neighbor("E", 3)],
}
test_case("Barbell graph", projection12, expected_clusters=2)


# Test Case 13: Grid (2x3)
print("\n" + "="*60)
print("TEST CASE 13: Grid 2x3")
print("  A-B-C")
print("  D-E-F")
print("="*60)
projection13 = {
    "A": [Neighbor("B", 1), Neighbor("D", 1)],
    "B": [Neighbor("A", 1), Neighbor("C", 1), Neighbor("E", 1)],
    "C": [Neighbor("B", 1), Neighbor("F", 1)],
    "D": [Neighbor("A", 1), Neighbor("E", 1)],
    "E": [Neighbor("B", 1), Neighbor("D", 1), Neighbor("F", 1)],
    "F": [Neighbor("C", 1), Neighbor("E", 1)],
}
test_case("Grid 2x3", projection13, expected_clusters=1)


# Test Case 14: Bipartite graph
print("\n" + "="*60)
print("TEST CASE 14: Bipartite graph")
print("  Group 1: A, B, C")
print("  Group 2: X, Y")
print("  All cross-connections")
print("="*60)
projection14 = {
    "A": [Neighbor("X", 1), Neighbor("Y", 1)],
    "B": [Neighbor("X", 1), Neighbor("Y", 1)],
    "C": [Neighbor("X", 1), Neighbor("Y", 1)],
    "X": [Neighbor("A", 1), Neighbor("B", 1), Neighbor("C", 1)],
    "Y": [Neighbor("A", 1), Neighbor("B", 1), Neighbor("C", 1)],
}
test_case("Bipartite graph", projection14, expected_clusters=1)


# Test Case 15: Long chain
print("\n" + "="*60)
print("TEST CASE 15: Long chain")
print("  A-B-C-D-E-F-G-H-I-J")
print("="*60)
projection15 = {
    "A": [Neighbor("B", 1)],
    "B": [Neighbor("A", 1), Neighbor("C", 1)],
    "C": [Neighbor("B", 1), Neighbor("D", 1)],
    "D": [Neighbor("C", 1), Neighbor("E", 1)],
    "E": [Neighbor("D", 1), Neighbor("F", 1)],
    "F": [Neighbor("E", 1), Neighbor("G", 1)],
    "G": [Neighbor("F", 1), Neighbor("H", 1)],
    "H": [Neighbor("G", 1), Neighbor("I", 1)],
    "I": [Neighbor("H", 1), Neighbor("J", 1)],
    "J": [Neighbor("I", 1)],
}
test_case("Long chain", projection15, expected_clusters=1)


print("\n" + "="*60)
print("ALL TESTS COMPLETED")
print("="*60)
