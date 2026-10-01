"""Funcoes puras sobre grafos dirigidos (pre-requisitos, hierarquia de unidades)."""

from uuid import UUID
from collections import defaultdict
from collections.abc import Iterable


def reaches(edges: Iterable[tuple[int, int]], start: int, target: int) -> bool:
    """Existe caminho ``start -> ... -> target`` seguindo as arestas ``(origem, destino)``?"""
    adjacency: dict[UUID, list[UUID]] = defaultdict(list)
    for origin, destination in edges:
        adjacency[origin].append(destination)
    pending, seen = [start], {start}
    while pending:
        node = pending.pop()
        if node == target:
            return True
        for neighbor in adjacency[node]:
            if neighbor not in seen:
                seen.add(neighbor)
                pending.append(neighbor)
    return False
