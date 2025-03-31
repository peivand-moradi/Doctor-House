"""Doctor House Backend Module"""

from __future__ import annotations
from typing import Any, Optional
import csv


class Disease:
    """A disease object.

    Instance Attributes:
        - symptoms: Symptoms related to this disease.
        - advice: Precautions that can be taken against this disease.
        - description: A brief description of the disease.
    """
    name: str
    symptoms: Optional[set]
    advice: list
    description: Optional[str]

    def __init__(self, name: str, advice: list = None,
                 symptoms: set = None, description: str = None) -> None:
        """Initialize a new Disease object.

        >>> d = Disease('Flu')
        >>> d.name
        'Flu'
        >>> d.advice
        []
        """
        self.name = name
        self.symptoms = symptoms if symptoms is not None else set()
        self.advice = advice if advice is not None else []
        self.description = description


class _Vertex:
    """A vertex in a graph.

    Instance Attributes:
        - item: The data stored in this vertex.
        - neighbours: The vertices that are adjacent to this vertex.
        - kind: The type of this vertex: 'symptom' or 'disease'.
    """
    item: Any
    neighbours: set[tuple[_Vertex, float]]
    kind: str

    def __init__(self, item: Any, neighbours: set[tuple[_Vertex, float]],
                 kind: str) -> None:
        """Initialize a new vertex."""
        self.item = item
        self.neighbours = neighbours
        self.kind = kind


class Graph:
    """A graph.

    Representation Invariants:
    - all(item == self._vertices[item].item for item in self._vertices)
    """
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph.

        >>> g = Graph()
        >>> g._vertices
        {}
        """
        self._vertices = {}

    def add_vertex(self, item: Any, item_kind: str) -> None:
        """Add a vertex with the given item to this graph.

        >>> g = Graph()
        >>> g.add_vertex('Flu', 'disease')
        >>> 'Flu' in g._vertices
        True
        """
        self._vertices[item] = _Vertex(item, set(), item_kind)

    def add_edge(self, item1: Any, item2: Any, edge_value: int) -> None:
        """Add an edge between two vertices.

        >>> g = Graph()
        >>> g.add_vertex('A', 'symptom')
        >>> g.add_vertex('B', 'disease')
        >>> g.add_edge('A', 'B', 2)
        >>> g.adjacent('A', 'B')
        True
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]
            v1.neighbours.add((v2, 1 / edge_value))
            v2.neighbours.add((v1, 1 / edge_value))
        else:
            raise ValueError

    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent.

        >>> g = Graph()
        >>> g.add_vertex('A', 'symptom')
        >>> g.add_vertex('B', 'disease')
        >>> g.add_edge('A', 'B', 2)
        >>> g.adjacent('A', 'B')
        True
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return any(v2[0].item == item2 for v2 in v1.neighbours)
        return False

    def get_neighbours(self, item: Any) -> set:
        """Return the neighbours of the given item.

        >>> g = Graph()
        >>> g.add_vertex('A', 'symptom')
        >>> g.add_vertex('B', 'disease')
        >>> g.add_edge('A', 'B', 2)
        >>> g.get_neighbours('A')
        {'B'}
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour[0].item for neighbour in v.neighbours}
        raise ValueError

    def shortest_path(self, start: Any, end: Any) -> list[Any]:
        """Find the shortest path between two vertices.

        >>> g = Graph()
        >>> g.add_vertex('A', 'symptom')
        >>> g.add_vertex('B', 'disease')
        >>> g.add_edge('A', 'B', 2)
        >>> g.shortest_path('A', 'B')
        ['A', 'B']
        """
        queue = [[start]]
        visited = set()

        if start not in self._vertices or end not in self._vertices:
            return []

        while queue:
            path = queue.pop(0)
            node = path[-1]

            if node == end:
                return path

            if node not in visited:
                visited.add(node)
                for neighbor in self.get_neighbours(node):
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)

        return []

    def get_vertex_kind(self, item: Any) -> str:
        """Return the type of vertex.

        >>> g = Graph()
        >>> g.add_vertex('A', 'symptom')
        >>> g.get_vertex_kind('A')
        'symptom'
        """
        return self._vertices[item].kind

    def get_weight_of_edge(self, item_1: Any, item_2: Any) -> float:
        """Return the weight of the edge between two vertices.

        >>> g = Graph()
        >>> g.add_vertex('A', 'symptom')
        >>> g.add_vertex('B', 'disease')
        >>> g.add_edge('A', 'B', 2)
        >>> g.get_weight_of_edge('A', 'B')
        0.5
        """
        for neighbour in self._vertices[item_1].neighbours:
            if neighbour[0].item == item_2:
                return neighbour[1]
        return 0.0

    def calculate_path_score(self, path: list) -> float:
        """Return the total weight of the given path.

        >>> g = Graph()
        >>> g.add_vertex('A', 'symptom')
        >>> g.add_vertex('B', 'disease')
        >>> g.add_edge('A', 'B', 2)
        >>> g.calculate_path_score(['A', 'B'])
        0.5
        """
        score = 0.0
        for i in range(len(path) - 1):
            score += self.get_weight_of_edge(path[i], path[i + 1])
        return score

    def get_list_of_vertices(self) -> list:
        """Return a list of all vertices.

        >>> g = Graph()
        >>> g.add_vertex('A', 'symptom')
        >>> g.get_list_of_vertices()
        ['A']
        """
        return list(self._vertices.keys())


def generate_combinations(lst: list[Any]) -> list[tuple[Any, Any]]:
    """Return all unique pairs from lst.

    >>> generate_combinations(['a', 'b', 'c'])
    [('a', 'b'), ('a', 'c'), ('b', 'c')]
    """
    result: list[tuple[Any, Any]] = []
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            result.append((lst[i], lst[j]))
    return result


def load_diagnosis_graph(symptom_file: str, dataset_file: str,
                          description_file: str, precaution_file: str) -> tuple[Graph, list, dict]:
    """Load the diagnosis graph and related data."""
    with open(symptom_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        severity_map = {row[0].strip(): row[1].strip() for row in reader}

    name_to_disease_map = {}
    with open(dataset_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            symptoms = {element.strip() for element in row[1:] if element != ""}
            if row[0].strip() in name_to_disease_map:
                name_to_disease_map[row[0].strip()].symptoms.update(symptoms)
            else:
                name_to_disease_map[row[0].strip()] = Disease(name=row[0].strip(), symptoms=symptoms)

    with open(description_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            name_to_disease_map[row[0].strip()].description = row[1].strip()

    with open(precaution_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            for i in range(1, len(row)):
                name_to_disease_map[row[0].strip()].advice.append(row[i].strip())

    symptoms_list = list(severity_map)
    diagnosis_graph = Graph()

    for disease in name_to_disease_map:
        if disease not in diagnosis_graph.get_list_of_vertices():
            diagnosis_graph.add_vertex(disease, 'disease')

        for symptom in name_to_disease_map[disease].symptoms:
            if symptom not in diagnosis_graph.get_list_of_vertices():
                diagnosis_graph.add_vertex(symptom, 'symptom')

            diagnosis_graph.add_edge(disease, symptom, int(severity_map[symptom]))

    return diagnosis_graph, symptoms_list, name_to_disease_map


def calculate_potential_disease(diagnosis_graph: Graph, symptoms: list) -> dict[str, float]:
    """Return the likelihood of each disease based on the provided symptoms.

    >>> g = Graph()
    >>> g.add_vertex('Headache', 'symptom')
    >>> g.add_vertex('Flu', 'disease')
    >>> g.add_edge('Headache', 'Flu', 2)
    >>> calculate_potential_disease(g, ['Headache'])
    {'Flu': 100.0}
    """
    scores = {}

    if len(symptoms) == 1:
        neighbours = diagnosis_graph.get_neighbours(symptoms[0])
        for neighbour in neighbours:
            scores[neighbour] = diagnosis_graph.get_weight_of_edge(neighbour, symptoms[0])
    else:
        for symptom_1, symptom_2 in generate_combinations(symptoms):
            path = diagnosis_graph.shortest_path(symptom_1, symptom_2)
            for vertex in path:
                if diagnosis_graph.get_vertex_kind(vertex) == "disease":
                    scores[vertex] = scores.get(vertex, 0) + diagnosis_graph.calculate_path_score(path)

    scores = {disease: 1 / score for disease, score in scores.items() if score != 0}
    sum_scores = sum(scores.values())
    scores = {disease: (score / sum_scores) * 100 for disease, score in scores.items()}

    return scores

# diagnosis_graph, symptoms_list, name_to_disease_map = load_diagnosis_graph('Symptom-severity.csv', 'dataset.csv',
# 'symptom_Description.csv', 'symptom_precaution.csv')


if __name__ == '__main__':

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['csv', 'matplotlib', 'tkinter', 'backend', 'matplotlib.pyplot', 'matplotlib.figure',
                          'matplotlib.backends.backend_tkagg'],
        'allowed-io': ['print'],
        'max-line-length': 120
    })
