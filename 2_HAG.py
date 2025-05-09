import networkx as nx
import matplotlib.pyplot as plt
from typing import Set, Dict, Tuple, List, Optional


class HAG:
    """
    HAG (Hierarchical Abstraction Graph) is a graph structure supporting:
    - Multi-level abstraction through hyper-vertices
    - Directed labeled edges
    - Path finding
    - Visualization using NetworkX and Matplotlib
    """

    def __init__(self) -> None:
        self._vertices: Set[str] = set()
        self._edges: Set[Tuple[str, str, str]] = set()  # Each edge: (source, target, label)
        self._hyper_vertices: Dict[str, Set[str]] = {}  # Hyper-vertex name → set of members
        self._constraints: List[str] = []  # Placeholder for future constraint logic

    # ----------------------------
    # Vertex, Edge, HV Management
    # ----------------------------
    
    def add_vertex(self, vertex: str) -> None:
        """Add a vertex to the graph."""
        self._vertices.add(vertex)

    def add_edge(self, source: str, target: str, label: str = "") -> None:
        """Add a directed edge from source to target, with optional label."""
        self._edges.add((source, target, label))
        self._vertices.update([source, target])  # Ensure both vertices are registered

    def add_hyper_vertex(self, name: str, members: Set[str]) -> None:
        """
        Define a hyper-vertex, which groups a set of vertices (or other hyper-vertices).
        """
        self._hyper_vertices[name] = members
        self._vertices.add(name)

    def add_constraint(self, constraint: str) -> None:
        """Add a logical or structural constraint (not enforced yet)."""
        self._constraints.append(constraint)

    # ----------------------------
    # Graph Logic
    # ----------------------------

    def get_neighbors(self, vertex: str) -> List[str]:
        """Return all directly connected target vertices from a given source vertex."""
        return [t for (s, t, _) in self._edges if s == vertex]

    def path_exists(self, start: str, end: str, visited: Optional[Set[str]] = None) -> bool:
        """Check if a path exists from start to end vertex using DFS."""
        if visited is None:
            visited = set()
        if start == end:
            return True
        visited.add(start)
        for neighbor in self.get_neighbors(start):
            if neighbor not in visited and self.path_exists(neighbor, end, visited):
                return True
        return False

    def collapse_hyper_vertex(self, name: str) -> None:
        """
        Replace all members of a hyper-vertex in the graph with the hyper-vertex name itself.
        This simplifies the graph view while maintaining structure.
        """
        if name not in self._hyper_vertices:
            return
        members = self._hyper_vertices[name]
        new_edges = set()
        for v1, v2, label in self._edges:
            nv1 = name if v1 in members else v1
            nv2 = name if v2 in members else v2
            new_edges.add((nv1, nv2, label))
        self._edges = new_edges
        self._vertices.difference_update(members)
        self._vertices.add(name)

    # ----------------------------
    # Graph Visualization
    # ----------------------------

    def draw(self, show_labels: bool = True, highlight_hyper: bool = True) -> None:
        """
        Visualize the graph using NetworkX and Matplotlib.
        Args:
            show_labels: whether to show node labels
            highlight_hyper: whether to highlight hyper-vertices
        """
        G = nx.DiGraph()
        labels = {}

        # Add all vertices
        for v in self._vertices:
            G.add_node(v)
            labels[v] = v

        # Add all edges
        for u, v, lbl in self._edges:
            G.add_edge(u, v)
            if lbl:
                labels[(u, v)] = lbl

        # Compute layout
        pos = nx.spring_layout(G, seed=42)

        # Draw nodes and edges
        nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=800, alpha=0.8)
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True)

        # Node labels
        if show_labels:
            nx.draw_networkx_labels(G, pos, font_size=10)

        # Edge labels (if present)
        edge_labels = {(u, v): l for (u, v, l) in self._edges if l}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='green')

        # Highlight hyper-vertices
        if highlight_hyper:
            for hv, members in self._hyper_vertices.items():
                if hv in pos:
                    x, y = pos[hv]
                    plt.text(x, y + 0.1, f"HV: {hv}", color='red', fontsize=9, fontweight='bold', ha='center')

        plt.title("Hierarchical Abstraction Graph (HAG)", fontsize=12)
        plt.axis('off')
        plt.tight_layout()
        plt.show()

    # ----------------------------
    # String Representation
    # ----------------------------

    def __str__(self) -> str:
        return (
            f"HAG Model\n"
            f"Vertices: {sorted(self._vertices)}\n"
            f"Edges: {sorted(self._edges)}\n"
            f"Hyper-Vertices: {self._hyper_vertices}\n"
            f"Constraints: {self._constraints}"
        )
if __name__ == "__main__":
    hag = HAG()

    # Define edges and structure
    hag.add_edge("A", "B", "calls")
    hag.add_edge("B", "C", "uses")
    hag.add_edge("C", "D", "flows")

    # Define hyper-vertices
    hag.add_hyper_vertex("Module1", {"A", "B"})
    hag.add_hyper_vertex("Subsystem", {"Module1", "C"})

    # Display graph structure
    print(hag)

    # Show graphical representation
    hag.draw()
