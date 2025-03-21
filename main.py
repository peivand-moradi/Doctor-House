from __future__ import annotations
from typing import Any
import csv

class _Vertex:
    """A vertex in a graph.

    Instance Attributes:
        - item: The data stored in this vertex.
        - neighbours: The vertices that are adjacent to this vertex.
    """
    item: Any
    neighbours: set[_Vertex]

    def __init__(self, item: Any, neighbours: set[_Vertex]) -> None:
        """Initialize a new vertex with the given item and neighbours."""
        self.item = item
        self.neighbours = neighbours


class Graph:

    """A graph.

    Representation Invariants:
    - all(item == self._vertices[item].item for item in self._vertices)
    """
    # Private Instance Attributes:
    #     - _vertices: A collection of the vertices contained in this graph.
    #                  Maps item to _Vertex instance.
    _vertices: dict[Any, _Vertex]

    def add_vertex(self, item: Any) -> None:
        """Add a vertex with the given item to this graph.

        The new vertex is not adjacent to any other vertices.

        Preconditions:
            - item not in self._vertices
        """
        self._vertices[item] = _Vertex(item, set())

    def add_edge(self, item1: Any, item2: Any) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            # Add the new edge
            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            # We didn't find an existing vertex for both items.
            raise ValueError
    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return any(v2.item == item2 for v2 in v1.neighbours)
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
            return {neighbour.item for neighbour in v.neighbours}
        else:
            raise ValueError
        

with open('Symptom-severity.csv', mode ='r') as file:
  symptomfile = csv.reader(file)
  next(symptomfile)
  severity_map = {line[0] : line[1] for line in symptomfile}

with open('dataset.csv', mode ='r') as file:
  diseasefile = csv.reader(file)
  next(diseasefile)
  disease_to_symptom_map = {}
  for line in diseasefile:
    symptoms = {element for element in line[1:] if element != ""}
    if line[0] in disease_to_symptom_map:
        disease_to_symptom_map[line[0]] = disease_to_symptom_map[line[0]].union(symptoms)
    else:
       disease_to_symptom_map[line[0]] = symptoms

print(disease_to_symptom_map)

diagnosis_graph = Graph()

for disease in disease_to_symptom_map:
    if disease not in diagnosis_graph._vertices:
        diagnosis_graph.add_vertex(disease)

    for symptom in disease_to_symptom_map[disease]:
        if symptom not in diagnosis_graph._vertices:
            diagnosis_graph.add_vertex(symptom)
        
        diagnosis_graph.add_edge(disease_to_symptom_map[disease], symptom)
