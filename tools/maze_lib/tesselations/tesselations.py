from abc import ABC, abstractmethod


class Node(ABC):

  def __init__(self, coordinates):
    self.coordinates = coordinates

  def __repr__(self):
    return str(self.coordinates)


class PathNode(Node):

  def __init__(self, coordinates):
    super().__init__(coordinates)
    self.parent = self
    self.rank = 0

  def find_parent(self):
    while self.parent != self.parent.parent:
      self.parent = self.parent.parent
    return self.parent


class WallNode(Node):
  pass


class Edge(ABC):

  def __init__(self, wall_node_1, wall_node_2):
    self.wall_nodes = [wall_node_1, wall_node_2]

  def __repr__(self):
    return "{wall_node_0}-{wall_node_1}".format(
      wall_node_0=self.wall_nodes[0],
      wall_node_1=self.wall_nodes[1])


class InnerEdge(Edge):

  def __init__(self, wall_node_1, wall_node_2, path_node_1, path_node_2):
    super().__init__(wall_node_1, wall_node_2)
    self.path_nodes = [path_node_1, path_node_2]

  def __repr__(self):
    return "{path_node_0}-{path_node_1}".format(
      path_node_0=self.path_nodes[0].__repr__(),
      path_node_1=self.path_nodes[1].__repr__())


class OuterEdge(Edge):
  pass


class Tesselation(ABC):

  @abstractmethod
  def _init_nodes_and_edges(self):
    pass

  @abstractmethod
  def _calc_point(self, node):
    pass
