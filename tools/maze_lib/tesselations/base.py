from abc import ABC, abstractmethod


class Node():

  def __init__(self, id, graph_coordinates, map_coordinates):
    self.id = id
    self.graph_coordinates = graph_coordinates
    self.map_coordinates = map_coordinates
    self.parent = self
    self.rank = 0

  def find_parent(self):
    while self.parent != self.parent.parent:
      self.parent = self.parent.parent
    return self.parent


class WallPoint():

  def __init__(self, map_coordinates):
    self.map_coordinates = map_coordinates


class Edge(ABC):

  def __init__(self, wall_point_1, wall_point_2):
    self.wall_points = [wall_point_1, wall_point_2]


class InnerEdge(Edge):

  def __init__(self, wall_point_1, wall_point_2, node_1, node_2):
    super().__init__(wall_point_1, wall_point_2)
    self.nodes = [node_1, node_2]


class OuterEdge(Edge):
  pass


class Tesselation(ABC):

  def __init__(self, length, width, path_thickness, mesh_width):
    self.node_id_sequence = 0
    self._init_units(length, width, path_thickness, mesh_width)
    self._init_nodes_and_edges()

  def _init_units(self, path_thickness, mesh_width):
    self.unit_width = path_thickness + mesh_width

  def _create_node(self, graph_coordinates):
    self.node_id_sequence += 1
    map_coordinates = self._calc_node_map_coordinates(graph_coordinates)
    return Node(self.node_id_sequence, graph_coordinates, map_coordinates)

  def _create_wall_point(self, graph_coordinates):
    map_coordinates = self._calc_wall_map_coordinates(graph_coordinates)
    return WallPoint(map_coordinates)

  @abstractmethod
  def _init_nodes_and_edges(self):
    pass

  @abstractmethod
  def _calc_node_map_coordinates(self, graph_coordinates):
    pass

  @abstractmethod
  def _calc_wall_map_coordinates(self, graph_coordinates):
    pass
