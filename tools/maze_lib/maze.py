from maze_lib import tesselations
import random

class Maze():

    #     params:  length, width, path_thickness, mesh_width, tesselation,
    #              routing
  def __init__(self, length, width, path_thickness, mesh_width, tesselation_name, routing):
    self._init_tesselation(tesselation_name.title(), length, width, path_thickness, mesh_width)
    self.routing = routing.lower()
    self.maze_walls = self._init_maze_walls(self.routing)

  def _init_tesselation(self, tesselation_name, length, width, path_thickness, mesh_width):
    try:
      TesselationClass = getattr(tesselations, tesselation_name)
    except AttributeError:
      error_msg = '{} is not a valid tesselation.'.format(tesselation_name)
      raise ValueError(error_msg)
    self.tesselation = TesselationClass(length, width, path_thickness, mesh_width)
    self.border_walls = self.tesselation.outer_edges

  def _init_maze_walls(self, routing):
    if routing == "perfect":
      return self._init_perfect_maze_walls()
    else:
      error_msg = '{} is not a valid routing.'.format(routing)
      raise ValueError(error_msg)

  def _init_perfect_maze_walls(self):

    def _is_maze_wall(edge):
      node1, node2 = edge.nodes
      node1_parent = node1.find_parent()
      node2_parent = node2.find_parent()
      if node1_parent == node2_parent:
        return True
      else:
        # join sets
        if node1.rank < node2.rank:
          node1_parent.parent = node2_parent
        elif node1.rank > node2.rank:
          node2_parent.parent = node1_parent
        else:
          node1_parent.parent = node2_parent
          node2_parent.rank += 1
        return False

    self.maze_walls = set()
    for edge in random.sample(list(self.tesselation.inner_edges.values()), len(self.tesselation.inner_edges)):
      if _is_maze_wall(edge):
        self.maze_walls.add(edge)
