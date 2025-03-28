from __future__ import annotations
from typing import Any
import csv
from collections import deque
from itertools import combinations


class _Vertex:
    """A vertex in a graph.

    Instance Attributes:
        - item: The data stored in this vertex.
        - neighbours: The vertices that are adjacent to this vertex.
        - kind: The type of this vertex: 'symptom' or 'disease'.
    """
    item: Any
    neighbours: set[(_Vertex, int)]
    kind: str

    def __init__(self, item: Any, neighbours: set[(_Vertex, int)], kind: str) -> None:
        """Initialize a new vertex with the given item and neighbours."""
        self.item = item
        self.neighbours = neighbours
        self.kind = kind


class Graph:

    """A graph.

    Representation Invariants:
    - all(item == self._vertices[item].item for item in self._vertices)
    """
    # Private Instance Attributes:
    #     - _vertices: A collection of the vertices contained in this graph.
    #                  Maps item to _Vertex instance.
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any, item_kind: str) -> None:
        """Add a vertex with the given item to this graph.

        The new vertex is not adjacent to any other vertices.

        Preconditions:
            - item not in self._vertices
        """
        self._vertices[item] = _Vertex(item, set(), item_kind)

    def add_edge(self, item1: Any, item2: Any, edge_value: int) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            # Add the new edge
            v1.neighbours.add((v2, 1 / edge_value))
            v2.neighbours.add((v1, 1 / edge_value))
        else:
            # We didn't find an existing vertex for both items.
            raise ValueError
    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return any(v2[0].item == item2 for v2 in v1.neighbours)
        else:
            # We didn't find an existing vertex for both items.
            return False

    def get_neighbours(self, item: Any) -> set:
        """Return a set of the neighbours of the given item.

        Note that the *items* are returned, not the _Vertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour[0].item for neighbour in v.neighbours}
        else:
            raise ValueError

    def shortest_path(self, start: Any, end: Any) -> list[Any]:
        """Find the shortest path between two vertices using BFS.

        Returns a list of items representing the shortest path from start to end.
        If no path exists, returns an empty list.
        """
        if start not in self._vertices or end not in self._vertices:
            return []

        queue = deque([[start]])  # Queue stores paths, starting with the start vertex
        visited = set()

        while queue:
            path = queue.popleft()
            node = path[-1]

            if node == end:
                return path  # Found the shortest path

            if node not in visited:
                visited.add(node)
                for neighbor in self.get_neighbours(node):
                    new_path = list(path)  # Copy the current path
                    new_path.append(neighbor)
                    queue.append(new_path)

        return []  # No path found

    def get_vertex_kind(self, item: Any) -> str:
        """
        Return the type of vertex (that is disease or symptom) with the given item
        """
        return self._vertices[item].kind

    def get_weight_of_edge(self, item_1: Any, item_2: Any) -> float:
        """
        Returns the weight of the edge between two vertices with given item_1 and item_2.
        Preconditions:
            - item_1 and item_2 are neighbours
        """
        for neighbour in self._vertices[item_1].neighbours:
            if neighbour[0].item == item_2:
                return neighbour[1]

    def calculate_path_score(self, path: list) -> float:
        """
        return the total weight of the given path.
        """
        score = 0
        for i in range(len(path) - 1):
            score += self.get_weight_of_edge(path[i], path[i + 1])
        return score


with open('Symptom-severity.csv', mode='r') as file:
  symptomfile = csv.reader(file)
  next(symptomfile)
  severity_map = {line[0].strip() : line[1].strip() for line in symptomfile}

with open('dataset.csv', mode ='r') as file:
  diseasefile = csv.reader(file)
  next(diseasefile)
  disease_to_symptom_map = {}
  for line in diseasefile:
    symptoms = {element.strip() for element in line[1:] if element != ""}
    if line[0].strip() in disease_to_symptom_map:
        disease_to_symptom_map[line[0].strip()] = disease_to_symptom_map[line[0].strip()].union(symptoms)
    else:
       disease_to_symptom_map[line[0].strip()] = symptoms

print(disease_to_symptom_map)

symptoms_list = [item for item in severity_map]

diagnosis_graph = Graph()

for disease in disease_to_symptom_map:
    if disease not in diagnosis_graph._vertices:
        diagnosis_graph.add_vertex(disease, 'disease')

    for symptom in disease_to_symptom_map[disease]:
        if symptom not in diagnosis_graph._vertices:
            diagnosis_graph.add_vertex(symptom, 'symptom')

        diagnosis_graph.add_edge(disease, symptom, int(severity_map[symptom]))


print(diagnosis_graph.shortest_path("skin_rash","bruising"))


def calculate_potential_disease(diagnosis_graph: Graph, symptoms: list) -> dict[str, float]:
    """
    Return the likelihood of each disease based on the provided symptoms by analyzing the shortest paths
    between symptom nodes in a diagnosis graph.
    This function checks all pairs of symptoms, finds the shortest path between them, and adds up scores for
    each disease along the path. It then calculates a percentage chance for each disease based on those scores.
    """
    scores = {}
    for symptom_1, symptom_2 in combinations(symptoms, 2):
        path = diagnosis_graph.shortest_path(symptom_1, symptom_2)
        for vertex in path:
            if diagnosis_graph.get_vertex_kind(vertex) == "disease":
                if vertex not in scores:
                    scores[vertex] = diagnosis_graph.calculate_path_score(path)
                else:
                    scores[vertex] += diagnosis_graph.calculate_path_score(path)


    scores = {disease: 1 / scores[disease] for disease in scores}
    sum_scores = sum([scores[disease] for disease in scores])
    scores = {disease: (scores[disease] / sum_scores) * 100 for disease in scores}

    return scores




print(calculate_potential_disease(diagnosis_graph, ["congestion", "knee_pain", "depression", "polyuria"]))


print(calculate_potential_disease(diagnosis_graph, ["continuous_feel_of_urine", "abdominal_pain"]))

