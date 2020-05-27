from maze_lib.tesselations.base import Tesselation, Node, OuterEdge, InnerEdge


class Orthogonal(Tesselation):

  def _init_units(self, length, width, path_thickness, mesh_width):
    super()._init_units(length, width, path_thickness, mesh_width)
    # TODO: account for too small of x_units and z_units
    self.x_units = int(self.width // self.unit_width)
    self.z_units = int(self.length // self.unit_width)

  def _add_node(self, node):
    self.nodes[node.graph_coordinates] = node

  def _add_wall_point(self, wall_point):
    self.wall_points[wall_point.map_coordinates] = wall_point

  def _add_wall_points(self, wall_points):
    for wall_point in wall_points:
      self._add_wall_point(wall_point)

  def _add_inner_edge(self, inner_edge):
    self.inner_edges[frozenset(inner_edge.nodes)] = inner_edge

  def _init_nodes_and_edges(self):
    self.nodes = {}
    self.wall_points = {}
    self.outer_edges = set()
    self.inner_edges = {}

    last_wall_col = []
    last_wall_row = []
    
    # first cell
    if self.x_units >= 1 and self.z_units >= 1:
      # first node
      start_node = Node((0,0))
      self._add_node(start_node)
      # first border corner
      start_nw_wall_point = self._create_wall_point((0,0))
      start_sw_wall_point = self._create_wall_point((0,1))
      start_ne_wall_point = self._create_wall_point((1,0))
      self._add_wall_points((
          start_nw_wall_point, start_sw_wall_point, start_ne_wall_point))
      self.outer_edges.update([
          OuterEdge(start_nw_wall_point, start_sw_wall_point),
          OuterEdge(start_nw_wall_point, start_ne_wall_point)])

    # first column
    prev_path_col = []
    prev_node = start_node
    prev_wall_col = []
    prev_wall_point = start_sw_wall_point
    for z in range(1, self.z_units):
      # node
      new_node = Node((0,z))
      self._add_node(new_node)
      # left corner
      sw_wall_point = self._create_wall_point((0,z+1))
      ne_wall_point = self._create_wall_point((1,z))
      self._add_wall_points((sw_wall_point, ne_wall_point))
      self.outer_edges.add(OuterEdge(prev_wall_point, sw_wall_point))
      self._add_inner_edge(InnerEdge(
          prev_wall_point, ne_wall_point, prev_node, new_node))
      # next
      prev_path_col.append(new_node)
      prev_node = new_node
      prev_wall_col.append(ne_wall_point)
      prev_wall_point = sw_wall_point
      # last
      if z == self.z_units-1:
        last_wall_row.append(sw_wall_point)

    # first row
    start_path_row = []
    prev_node = start_node
    start_wall_row = []
    prev_wall_point = start_ne_wall_point
    for x in range(1, self.x_units):
      # node
      new_node = Node((x,0))
      self._add_node(new_node)
      # top corner
      sw_wall_point = self._create_wall_point((x,1)) if x>1 else prev_wall_col[0]
      ne_wall_point = self._create_wall_point((x+1,0))
      self._add_wall_points((sw_wall_point, ne_wall_point))
      self._add_inner_edge(InnerEdge(
          prev_wall_point, sw_wall_point, prev_node, new_node))
      self.outer_edges.add(OuterEdge(prev_wall_point, ne_wall_point))
      # next
      start_path_row.append(new_node)
      prev_node = new_node
      start_wall_row.append(sw_wall_point)
      prev_wall_point = ne_wall_point
      # last
      if x == self.x_units-1:
        last_wall_col.append(ne_wall_point)

    # remaining grid
    prev_path_x = start_path_row[0] if len(start_path_row)>0 else None
    for x in range(1, self.x_units):
      new_path_col = []
      prev_path_z = prev_path_col[0] if len(prev_path_col)>0 else None
      new_wall_col = []
      prev_wall_sw = start_wall_row[x-1]
      for z in range(1, self.z_units):
        # node
        new_node = Node((x,z))
        self._add_node(new_node)
        # wall corner
        nw_wall_point = prev_wall_sw
        sw_wall_point = prev_wall_col[z] \
            if z<self.z_units-1 else self._create_wall_point((x,z+1))
        ne_wall_point = self._create_wall_point((x+1,z)) \
            if z>1 or x==self.x_units-1 else start_wall_row[x]
        self._add_wall_points((sw_wall_point, ne_wall_point))
        self._add_inner_edge(InnerEdge(
            nw_wall_point, sw_wall_point, prev_path_z, new_node))
        self._add_inner_edge(InnerEdge(
            nw_wall_point, ne_wall_point, prev_path_x, new_node))
        # next z
        new_path_col.append(new_node)
        if z < self.z_units-1:
          prev_path_z = prev_path_col[z]
        prev_path_x = new_node
        new_wall_col.append(ne_wall_point)
        prev_wall_sw = sw_wall_point
        # last z
        if z == self.z_units-1:
          last_wall_row.append(sw_wall_point)
      # next x
      prev_path_col = new_path_col
      if x < self.x_units-1:
        prev_path_x = start_path_row[x] 
      prev_wall_col = new_wall_col
      # last x
      if x == self.x_units-1:
        last_wall_col.extend(new_wall_col)

    # last wall point
    last_wall_point = self._create_wall_point((self.x_units, self.z_units))
    self._add_wall_point(last_wall_point)

    # last border column
    n_wall_point = last_wall_col[0] if len(last_wall_col)>0 else None
    for s_wall_point in last_wall_col[1:]:
      self.outer_edges.add(OuterEdge(n_wall_point, s_wall_point))
      n_wall_point = s_wall_point
    if n_wall_point:
      self.outer_edges.add(OuterEdge(n_wall_point, last_wall_point))

    # last border row
    w_wall_point = last_wall_row[0] if len(last_wall_row)>0 else None
    for e_wall_point in last_wall_row[1:]:
      self.outer_edges.add(OuterEdge(w_wall_point, e_wall_point))
      w_wall_point = e_wall_point
    if w_wall_point:
      self.outer_edges.add(OuterEdge(w_wall_point, last_wall_point))

  def _calc_map_coordinates(self, coordinates):
    x, z = coordinates
    # TODO: translate coordinates to map coordinates
    return (0.0, 0.0)
