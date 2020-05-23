import maze_lib.tesselations
import random

class Maze():

    #     params:  length, width, path_thickness, mesh_width, tesselation,
    #              routing
  def __init__(self, length, width, path_thickness, mesh_width, tesselation_name, routing):
    # TODO: calculate x_units and z_units
    self.tesselation = set_tesselation(tesselation_name)
    self.routing = routing
    self.outer_edges = None
    self.inner_edges = None
    self.border_walls = None
    self.maze_walls = None

  def set_tesselation(self, tesselation, *args):
    try:
      self.tesselation = getattr(tesselations, tesselation)(*args)
    except AttributeError:
      error_msg = '{} is not a valid tesselation.'.format(tesselation)
      raise ValueError(error_msg)
    self.inner_edges = list(self.tesselation.inner_edges.values())
    self.outer_edges = list(self.tesselation.outer_edges)

  def randomize_maze_walls(self):
    if self.tesselation is None:
      error_msg = 'tesselation has not been set. Call set_tesselation() to set tesselation.'
      raise AttributeError(error_msg)

    def _is_maze_wall(edge):
      node1, node2 = edge.path_nodes
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

    # reset maze
    for node in self.tesselation.path_nodes.values():
      node.parent = node
    random.shuffle(self.inner_edges)
    self.maze_walls = set()

    for edge in self.inner_edges:
      if _is_maze_wall(edge):
        self.maze_walls.add(edge)
