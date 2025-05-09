from typing import Set, Dict, Tuple, List, Optional, Union


class HAG:
    """
    Hierarchical Abstraction Graph (HAG): 
    A structured, multi-level graph model with support for hyper-vertices, constraints, and abstraction operations.
    """

    def __init__(self) -> None:
        self._vertices: Set[str] = set()
        self._edges: Set[Tuple[str, str, str]] = set()  # (source, target, label)
        self._hyper_vertices: Dict[str, Set[str]] = {}
        self._constraints: List[str] = []

    # --- Properties ---
    @property
    def vertices(self) -> Set[str]:
        return self._vertices

    @property
    def edges(self) -> Set[Tuple[str, str, str]]:
        return self._edges

    @property
    def hyper_vertices(self) -> Dict[str, Set[str]]:
        return self._hyper_vertices

    @property
    def constraints(self) -> List[str]:
        return self._constraints

    # --- Add Methods ---
    def add_vertex(self, vertex: str) -> None:
        self._vertices.add(vertex)

    def add_edge(self, source: str, target: str, label: str = "") -> None:
        self._edges.add((source, target, label))

    def add_hyper_vertex(self, name: str, members: Set[str]) -> None:
        self._hyper_vertices[name] = members

    def add_constraint(self, constraint: str) -> None:
        self._constraints.append(constraint)

    # --- Graph Logic ---
    def get_neighbors(self, vertex: str) -> List[str]:
        return [target for (source, target, _) in self._edges if source == vertex]

    def path_exists(self, start: str, end: str, visited: Optional[Set[str]] = None) -> bool:
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
        """Replaces all members of a hyper vertex with the hyper vertex name in edges."""
        if name not in self._hyper_vertices:
            return
        members = self._hyper_vertices[name]
        new_edges = set()
        for (v1, v2, label) in self._edges:
            new_v1 = name if v1 in members else v1
            new_v2 = name if v2 in members else v2
            new_edges.add((new_v1, new_v2, label))
        self._edges = new_edges
        self._vertices -= members
        self._vertices.add(name)

    # --- Graph Operations ---
    def union(self, other: 'HAG') -> 'HAG':
        result = HAG()
        result._vertices = self._vertices | other._vertices
        result._edges = self._edges | other._edges
        result._hyper_vertices = {**self._hyper_vertices, **other._hyper_vertices}
        result._constraints = list(set(self._constraints + other._constraints))
        return result

    def intersection(self, other: 'HAG') -> 'HAG':
        result = HAG()
        result._vertices = self._vertices & other._vertices
        result._edges = self._edges & other._edges
        result._hyper_vertices = {
            k: v for k, v in self._hyper_vertices.items()
            if k in other._hyper_vertices and v == other._hyper_vertices[k]
        }
        result._constraints = list(set(self._constraints) & set(other._constraints))
        return result

    def subtract(self, other: 'HAG') -> 'HAG':
        result = HAG()
        result._vertices = self._vertices - other._vertices
        result._edges = self._edges - other._edges
        result._hyper_vertices = {
            k: v for k, v in self._hyper_vertices.items()
            if k not in other._hyper_vertices
        }
        result._constraints = [c for c in self._constraints if c not in other._constraints]
        return result

    # --- Display ---
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
    hag.add_vertex("v1")
    hag.add_vertex("v2")
    hag.add_vertex("v3")
    hag.add_edge("v1", "v2", "depends")
    hag.add_edge("v2", "v3", "calls")
    hag.add_hyper_vertex("HV1", {"v1", "v2"})

    print(hag)
    print("Path v1 to v3:", hag.path_exists("v1", "v3"))
    hag.collapse_hyper_vertex("HV1")
    print("After collapse:")
    print(hag)
