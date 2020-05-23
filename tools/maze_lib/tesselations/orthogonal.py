from tesselations import Shape


class Orthogonal(Shape):

  def __init__(self, x_units, z_units):
    self.x_units = x_units
    self.z_units = z_units
    self._init_nodes_and_edges()

  def _add_path_node(self, path_node):
    self.path_nodes[path_node.coordinates] = path_node

  def _add_wall_node(self, wall_node):
    self.wall_nodes[wall_node.coordinates] = wall_node

  def _add_wall_nodes(self, wall_nodes):
    for wall_node in wall_nodes:
      self._add_wall_node(wall_node)

  def _add_inner_edge(self, inner_edge):
    self.inner_edges[frozenset(inner_edge.path_nodes)] = inner_edge

  def _init_nodes_and_edges(self):
    self.path_nodes = {}
    self.wall_nodes = {}
    self.outer_edges = set()
    self.inner_edges = {}

    last_wall_col = []
    last_wall_row = []
    
    # first cell
    if self.x_units >= 1 and self.z_units >= 1:
      # first path node
      start_path_node = PathNode((0,0))
      self._add_path_node(start_path_node)
      # first border corner
      start_nw_wall_node = WallNode((0,0))
      start_sw_wall_node = WallNode((0,1))
      start_ne_wall_node = WallNode((1,0))
      self._add_wall_nodes((
          start_nw_wall_node, start_sw_wall_node, start_ne_wall_node))
      self.outer_edges.update([
          OuterEdge(start_nw_wall_node, start_sw_wall_node),
          OuterEdge(start_nw_wall_node, start_ne_wall_node)])

    # first column
    prev_path_col = []
    prev_path_node = start_path_node
    prev_wall_col = []
    prev_wall_node = start_sw_wall_node
    for z in range(1, self.z_units):
      # path node
      new_path_node = PathNode((0,z))
      self._add_path_node(new_path_node)
      # left corner
      sw_wall_node = WallNode((0,z+1))
      ne_wall_node = WallNode((1,z))
      self._add_wall_nodes((sw_wall_node, ne_wall_node))
      self.outer_edges.add(OuterEdge(prev_wall_node, sw_wall_node))
      self._add_inner_edge(InnerEdge(
          prev_wall_node, ne_wall_node, prev_path_node, new_path_node))
      # next
      prev_path_col.append(new_path_node)
      prev_path_node = new_path_node
      prev_wall_col.append(ne_wall_node)
      prev_wall_node = sw_wall_node
      # last
      if z == self.z_units-1:
        last_wall_row.append(sw_wall_node)

    # first row
    start_path_row = []
    prev_path_node = start_path_node
    start_wall_row = []
    prev_wall_node = start_ne_wall_node
    for x in range(1, self.x_units):
      # path node
      new_path_node = PathNode((x,0))
      self._add_path_node(new_path_node)
      # top corner
      sw_wall_node = WallNode((x,1)) if x>1 else prev_wall_col[0]
      ne_wall_node = WallNode((x+1,0))
      self._add_wall_nodes((sw_wall_node, ne_wall_node))
      self._add_inner_edge(InnerEdge(
          prev_wall_node, sw_wall_node, prev_path_node, new_path_node))
      self.outer_edges.add(OuterEdge(prev_wall_node, ne_wall_node))
      # next
      start_path_row.append(new_path_node)
      prev_path_node = new_path_node
      start_wall_row.append(sw_wall_node)
      prev_wall_node = ne_wall_node
      # last
      if x == self.x_units-1:
        last_wall_col.append(ne_wall_node)

    # remaining grid
    prev_path_x = start_path_row[0] if len(start_path_row)>0 else None
    for x in range(1, self.x_units):
      new_path_col = []
      prev_path_z = prev_path_col[0] if len(prev_path_col)>0 else None
      new_wall_col = []
      prev_wall_sw = start_wall_row[x-1]
      for z in range(1, self.z_units):
        # path node
        new_path_node = PathNode((x,z))
        self._add_path_node(new_path_node)
        # wall corner
        nw_wall_node = prev_wall_sw
        sw_wall_node = prev_wall_col[z] \
            if z<self.z_units-1 else WallNode((x,z+1))
        ne_wall_node = WallNode((x+1,z)) \
            if z>1 or x==self.x_units-1 else start_wall_row[x]
        self._add_wall_nodes((sw_wall_node, ne_wall_node))
        self._add_inner_edge(InnerEdge(
            nw_wall_node, sw_wall_node, prev_path_z, new_path_node))
        self._add_inner_edge(InnerEdge(
            nw_wall_node, ne_wall_node, prev_path_x, new_path_node))
        # next z
        new_path_col.append(new_path_node)
        if z < self.z_units-1:
          prev_path_z = prev_path_col[z]
        prev_path_x = new_path_node
        new_wall_col.append(ne_wall_node)
        prev_wall_sw = sw_wall_node
        # last z
        if z == self.z_units-1:
          last_wall_row.append(sw_wall_node)
      # next x
      prev_path_col = new_path_col
      if x < self.x_units-1:
        prev_path_x = start_path_row[x] 
      prev_wall_col = new_wall_col
      # last x
      if x == self.x_units-1:
        last_wall_col.extend(new_wall_col)

    # last wall node
    last_wall_node = WallNode((self.x_units, self.z_units))
    self._add_wall_node(last_wall_node)

    # last border column
    n_wall_node = last_wall_col[0] if len(last_wall_col)>0 else None
    for s_wall_node in last_wall_col[1:]:
      self.outer_edges.add(OuterEdge(n_wall_node, s_wall_node))
      n_wall_node = s_wall_node
    if n_wall_node:
      self.outer_edges.add(OuterEdge(n_wall_node, last_wall_node))

    # last border row
    w_wall_node = last_wall_row[0] if len(last_wall_row)>0 else None
    for e_wall_node in last_wall_row[1:]:
      self.outer_edges.add(OuterEdge(w_wall_node, e_wall_node))
      w_wall_node = e_wall_node
    if w_wall_node:
      self.outer_edges.add(OuterEdge(w_wall_node, last_wall_node))

  def _calc_point(self, node, width, height):
    x, z = node.coordinates
    center_x = width//2
    center_z = height//2
    unit_length = min(width//(self.x_units+1), height//(self.z_units+1))
    start_x = center_x - ((self.x_units) * unit_length)//2
    start_z = center_z - ((self.z_units) * unit_length)//2
    return (start_x + x*unit_length, start_z + z*unit_length)
