from abc import ABC, abstractmethod


class Node():

  def __init__(self, graph_coordinates):
    self.graph_coordinates = graph_coordinates
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
    self._init_units(length, width, path_thickness, mesh_width)
    self._init_nodes_and_edges()

  def _init_units(self, path_thickness, mesh_width):
    self.unit_width = path_thickness + mesh_width

  def _create_wall_point(self, coordinates):
    wall_coordinates = self._calc_map_coordinates(coordinates)
    return WallPoint(wall_coordinates)

  @abstractmethod
  def _init_nodes_and_edges(self):
    pass

  @abstractmethod
  def _calc_map_coordinates(self, coordinates):
    pass
