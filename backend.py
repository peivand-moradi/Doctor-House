"""Doctor House Backed Module

Handles graph creation and disease detection.
"""

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

    def __init__(self, name: str, advice: list = None, symptoms: list = None, description: str = None) -> None:
        """Initialize a new vertex with the given item and neighbours."""
        self.name = name
        self.symptoms = symptoms if symptoms is not none else set()
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

    def __init__(self, item: Any, neighbours: set[tuple[_Vertex, float]], kind: str) -> None:
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
        """Initialize an empty graph (no vertices or edges).
        
        >>> g = Graph()
        >>> g._vertices
        {}
        """
        self._vertices = {}

    def add_vertex(self, item: Any, item_kind: str) -> None:
        """Add a vertex with the given item to this graph.

        The new vertex is not adjacent to any other vertices.

        Preconditions:
            - item not in self._vertices
        
        >>> g = Graph()
        >>> g.add_vertex('Flu', 'disease')
        >>> 'Flu' in g._vertices
        True
        """
        self._vertices[item] = _Vertex(item, set(), item_kind)

    def add_edge(self, item1: Any, item2: Any, edge_value: int) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
            
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

            # Add the new edge
            v1.neighbours.add((v2, 1 / edge_value))
            v2.neighbours.add((v1, 1 / edge_value))
        else:
            # We didn't find an existing vertex for both items.
            raise ValueError
    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.

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
        """Return a set of the neighbours of the given item.

        Note that the *items* are returned, not the _Vertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.

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
        """Find the shortest path between two vertices using BFS.

        Returns a list of items representing the shortest path from start to end.
        If no path exists, returns an empty list.

        >>> g = Graph()
        >>> g.add_vertex('A', 'symptom')
        >>> g.add_vertex('B', 'disease')
        >>> g.add_edge('A', 'B', 2)
        >>> g.shortest_path('A', 'B')
        ['A', 'B']
        """
        if start not in self._vertices or end not in self._vertices:
            return []

        queue = [[start]]  # Queue stores paths, starting with the start vertex
        visited = set()

        while queue:
            path = queue.pop(0)
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
        Return the type of vertex (that is disease or symptom) with the given item.

        >>> g = Graph()
        >>> g.add_vertex('A', 'symptom')
        >>> g.get_vertex_kind('A')
        'symptom'
        """
        return self._vertices[item].kind

    def get_weight_of_edge(self, item_1: Any, item_2: Any) -> float:
        """
        Returns the weight of the edge between two vertices with given item_1 and item_2.
        Preconditions:
            - item_1 and item_2 are neighbours
         
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
        """ Return the total weight of the given path.
        
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
        """ Returns a list of all vertices (could be disease or symptom) present in this graph

        >>> g = Graph()
        >>> g.add_vertex('A', 'symptom')
        >>> g.get_list_of_vertices()
        ['A']
        """
        return list(self._vertices.keys())

def generate_combinations(lst: list[Any]) -> list[tuple[Any, Any]]:
    """Return all unique pairs (combinations) from lst.

    >>> generate_combinations(['a', 'b', 'c'])
    [('a', 'b'), ('a', 'c'), ('b', 'c')]
    """
    result = []
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            result.append((lst[i], lst[j]))
    return result


def load_diagnosis_graph(symptom_file: str, dataset_file: str, 
                         description_file: str, precaution_file: str) -> Graph:
        """Load the diagnosis graph and related data from CSV file

    Returns the graph, list of symptoms, and a mapping of diseases.
    """
    with open(symptom_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        severity_map = {line[0].strip() : line[1].strip() for line in reader}

    name_to_disease_map = {}
    with open(dataset_file, mode ='r') as file:
        diseasefile = csv.reader(file)
        next(diseasefile)
        name_to_disease_map = {}
        for line in diseasefile:
            symptoms = {element.strip() for element in line[1:] if element != ""}
            if line[0].strip() in name_to_disease_map:
                name_to_disease_map[line[0].strip()].symptoms = name_to_disease_map[
                    line[0].strip()].symptoms.union(symptoms)
            else:
                name_to_disease_map[line[0].strip()] = Disease(name=line[0].strip(), symptoms=symptoms)

    with open(description_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            name_to_disease_map[row[0].strip()].advice.append(row[1].strip()

    with open('symptom_precaution.csv', mode='r') as file:
        precaution_file = csv.reader(file)
        next(precaution_file)
        for line in precaution_file:
            for i in range(1, len(line)):
                name_to_disease_map[line[0].strip()].advice.append(line[i].strip())
    
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
    """
    Return the likelihood of each disease based on the provided symptoms by analyzing the shortest paths
    between symptom nodes in a diagnosis graph.
    This function checks all pairs of symptoms, finds the shortest path between them, and adds up scores for
    each disease along the path. It then calculates a percentage chance for each disease based on those scores.

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
