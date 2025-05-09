from typing import Set, Dict, Tuple, List, Optional
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import os
import webbrowser


class HAG:
    """
    Hierarchical Abstraction Graph (HAG)
    ------------------------------------
    A graph model supporting:
        - Standard vertices and edges
        - Multi-level abstraction using hyper-vertices
        - Constraint registration (future logic)
        - Path traversal
        - Static and interactive visualization
    """

    def __init__(self) -> None:
        self._vertices: Set[str] = set()
        self._edges: Set[Tuple[str, str, str]] = set()  # (source, target, label)
        self._hyper_vertices: Dict[str, Set[str]] = {}  # name -> members
        self._constraints: List[str] = []

    # ----------------------------
    # Graph Construction
    # ----------------------------

    def add_vertex(self, vertex: str) -> None:
        """Add a single vertex."""
        self._vertices.add(vertex)

    def add_edge(self, source: str, target: str, label: str = "") -> None:
        """Add a directed edge with optional label."""
        self._edges.add((source, target, label))
        self._vertices.update([source, target])

    def add_hyper_vertex(self, name: str, members: Set[str]) -> None:
        """Define a hyper-vertex that groups existing vertices or hyper-vertices."""
        self._hyper_vertices[name] = members
        self._vertices.add(name)

    def add_constraint(self, constraint: str) -> None:
        """Add a constraint (stored only, not enforced)."""
        self._constraints.append(constraint)

    # ----------------------------
    # Graph Logic
    # ----------------------------

    def get_neighbors(self, vertex: str) -> List[str]:
        """Return the list of direct neighbors of a vertex."""
        return [t for (s, t, _) in self._edges if s == vertex]

    def path_exists(self, start: str, end: str, visited: Optional[Set[str]] = None) -> bool:
        """Check if a path exists between two vertices (DFS traversal)."""
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
        Collapse a hyper-vertex by replacing its members in all edges with the HV name.
        This simplifies the graph view.
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
    # Static Visualization
    # ----------------------------

    def draw(self, show_labels: bool = True, highlight_hyper: bool = True, save_as: Optional[str] = None) -> None:
        """
        Render the graph using NetworkX + Matplotlib.
        Args:
            show_labels: display node labels
            highlight_hyper: mark hyper-vertices in red
            save_as: save image (e.g., 'graph.png', 'graph.pdf')
        """
        G = nx.DiGraph()
        labels = {}

        # Add nodes and edges
        for v in self._vertices:
            G.add_node(v)
            labels[v] = v
        for u, v, lbl in self._edges:
            G.add_edge(u, v)
            if lbl:
                labels[(u, v)] = lbl

        pos = nx.spring_layout(G, seed=42)

        nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=800, alpha=0.8)
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True)

        if show_labels:
            nx.draw_networkx_labels(G, pos, font_size=10)

        edge_labels = {(u, v): l for (u, v, l) in self._edges if l}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='green')

        if highlight_hyper:
            for hv in self._hyper_vertices:
                if hv in pos:
                    x, y = pos[hv]
                    plt.text(x, y + 0.1, f"HV: {hv}", color='red', fontsize=9, fontweight='bold', ha='center')

        plt.title("Hierarchical Abstraction Graph (HAG)", fontsize=12)
        plt.axis('off')
        plt.tight_layout()

        if save_as:
            plt.savefig(save_as, format=save_as.split('.')[-1], dpi=300)
            print(f"[✔] Saved image to: {save_as}")

        plt.show()

    # ----------------------------
    # Interactive Visualization
    # ----------------------------

    def draw_interactive(self, notebook: bool = False, filename: str = "hag_graph.html") -> None:
        """
        Create an interactive, zoomable HTML visualization using PyVis.
        Args:
            notebook: render in Jupyter Notebook (True) or open in browser (False)
            filename: output HTML file
        """
        net = Network(height='600px', width='100%', directed=True, notebook=notebook)
        net.barnes_hut()

        for node in self._vertices:
            is_hyper = node in self._hyper_vertices
            net.add_node(
                node,
                label=node,
                color='red' if is_hyper else 'lightblue',
                shape='box' if is_hyper else 'ellipse',
                title=f"Hyper-Vertex: {node}" if is_hyper else f"Vertex: {node}"
            )

        for src, tgt, label in self._edges:
            net.add_edge(src, tgt, label=label)

        net.show(filename)

        full_path = os.path.abspath(filename)
        if not notebook:
            webbrowser.open(f"file://{full_path}")

        print(f"[✔] Interactive graph saved to: {filename}")

    # ----------------------------
    # Debug/Output
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

    # Define vertices and edges
    hag.add_edge("A", "B", "calls")
    hag.add_edge("B", "C", "uses")
    hag.add_edge("C", "D", "flows")

    # Define hyper-vertices
    hag.add_hyper_vertex("Module1", {"A", "B"})
    hag.add_hyper_vertex("Subsystem", {"Module1", "C"})

    # Print the structure
    print(hag)

    # Static plot
    hag.draw(save_as="hag_static.png")

    # Interactive plot
    hag.draw_interactive(filename="hag_interactive.html")
