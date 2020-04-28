import struct
from . import ma_util

endian='big'
float_endian = '>f'
int_endian = '>i'
short_endian = '>h'


class MeshHeader:
  def __init__(self, writer, offset):
    self.data = self.header_parse(writer, offset)

  def header_parse(self, writer, offset):
    header = {}
    writer.seek(offset)
    header['offset_to_mesh_table'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['num_fixups'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    #read padded data - 16 byte alignment
    writer.read(8)
    return header

  def print_header(self):
    print("--------------- Mesh Header ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))

  def to_bytes(self, int_endian):
    #TODO
    byteheader = struct.pack(int_endian, self.data['offset_to_mesh_table'])
    byteheader += struct.pack(int_endian, self.data['num_meshes'])
    #add 8 bytes for alignment
    for i in range(8):
      byteheader.append(0x0)
    return byteheader

class MeshObject:
  def __init__(self, writer, size):
    #parse header
    self.data = self.header_parse(writer, size)

  def read_segments(self, writer):
    writer.seek(self.data['segment_offset'])
    if self.data['num_seg_count'] == 255: 
      return []
    segments = []
    for item in range(self.data['num_seg_count']):
      bounding_sphere_radius = struct.unpack(float_endian, writer.read(4))[0]
      x = struct.unpack(float_endian, writer.read(4))[0]
      y = struct.unpack(float_endian, writer.read(4))[0]
      z = struct.unpack(float_endian, writer.read(4))[0]
      bounding_sphere_position = ma_util.Vector(3,x,y,z)
      bone_count = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
      bone_mtx_index = []
      for i in range(4):
        bone_mtx_index.append(int.from_bytes(writer.read(1), byteorder=endian, signed=False))
      segments.append(MeshSegment(bounding_sphere_radius, bounding_sphere_position, bone_count, bone_mtx_index))
    return segments
  
  def read_bone_array(self, writer):
    writer.seek(self.data['bone_offset'])
    if self.data['num_bone_count'] == 255: 
      return []
    bones = []
    for item in range(self.data['num_bone_count']):
      bones.append(MeshBone(writer))
    return bones
  
  def read_light_array(self, writer):
    writer.seek(self.data['light_offset'])
    if self.data['num_light_count'] == 255: 
      return []
    lights = []
    for item in range(self.data['num_light_count']):
      lights.append(MeshLight(writer))
    return lights
  
  #TODO not sure how many of these there are, probably one per bone
  def skeleton_index_array(self, writer, count):
    writer.seek(self.data['skeleton_index_offset'])
    if self.data['num_bone_count'] == 255: 
      return []
    indices = []
    for item in range(self.data['num_bone_count']):
      indices.append(int.from_bytes(writer.read(1), byteorder=endian, signed=False))
    return indices
  
  def read_material_array(self, writer):
    writer.seek(self.data['material_offset'])
    if self.data['num_material_count'] == 255: 
      return []
    bones = []
    for item in range(self.data['num_material_count']):
      bones.append(MeshMaterial(writer))
    return bones
  
  def read_collision_tree_array(self, writer):
    writer.seek(self.data['collision_tree_offset'])
    if self.data['num_collision_tree_count'] == 255: 
      return []
    bones = []
    for item in range(self.data['num_collision_tree_count']):
      bones.append(MeshMaterial(writer))
    return bones
  
  #TODO make sure this is right
  def read_texture_layer(self, writer):
    writer.seek(self.data['texture_layer_id_array_offset'])
    if self.data['num_tex_layer_id_count'] == 255: 
      return []
    bones = []
    for item in range(self.data['num_tex_layer_id_count']):
      bones.append(MeshMaterial(writer))
    return bones

  def header_parse(self, writer, size):
    header = {}
    header['offset'] = writer.tell()
    header['size'] = size
    header['mesh_name'] = writer.read(16)
    header['bounding_sphere_radius'] = struct.unpack(float_endian, writer.read(4))[0]
    x = struct.unpack(float_endian, writer.read(4))[0]
    y = struct.unpack(float_endian, writer.read(4))[0]
    z = struct.unpack(float_endian, writer.read(4))[0]
    header['bounding_sphere_position'] = ma_util.Vector(3,x,y,z)
    x = struct.unpack(float_endian, writer.read(4))[0]
    y = struct.unpack(float_endian, writer.read(4))[0]
    z = struct.unpack(float_endian, writer.read(4))[0]
    header['min_bounding_box'] = ma_util.Vector(3,x,y,z)
    x = struct.unpack(float_endian, writer.read(4))[0]
    y = struct.unpack(float_endian, writer.read(4))[0]
    z = struct.unpack(float_endian, writer.read(4))[0]
    header['max_bounding_box'] = ma_util.Vector(3,x,y,z)
    header['num_flags'] = int.from_bytes(writer.read(2), byteorder=endian, signed=False)
    header['num_mesh_collision_mask'] = int.from_bytes(writer.read(2), byteorder=endian, signed=False)
    header['num_used_bone_count'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    header['num_root_bone_index'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    header['num_bone_count'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    header['num_seg_count'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    header['num_tex_layer_id_count'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    header['num_tex_layer_id_count_ST'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    header['num_tex_layer_id_count_Flip'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    header['num_light_count'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    header['num_material_count'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    header['num_collision_tree_count'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    header['num_LOD_mesh_count'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    header['num_shadow_LOD_bias'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    lod_distance = []
    for i in range(8):
      lod_distance.append(struct.unpack(float_endian, writer.read(4))[0])
    header['LOD_Distance'] = lod_distance
    header['segment_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['bone_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['light_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['skeleton_index_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['material_array_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['collision_tree_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['texture_layer_id_array_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    header['mesh_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)

    return header

  def print_header(self):
    print("--------------- Mesh Object Header ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))

  def to_bytes(self, int_endian):
    #TODO
    None

class MeshSegment:
  def __init__(self, bounding_sphere_radius, bounding_sphere_position, bone_matrix_count, bone_matrix_idx_array):
    self.data = {}
    self.data['bounding_sphere_radius'] = bounding_sphere_radius
    self.data['bounding_sphere_position'] = bounding_sphere_position
    self.data['bone_matrix_count'] = bone_matrix_count
    self.data['bone_matrix_idx_array'] = bone_matrix_idx_array

  def print_header(self):
    print("--------------- Mesh Segment ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))

  def to_bytes(self):
    #TODO
    None

class MeshBone:
  def __init__(self, writer):
    self.data = {}
    self.data['offset'] = writer.tell()
    self.data['name'] = writer.read(32)
    at_rest_bone = []
    for i in range(16):
      at_rest_bone.append(struct.unpack(float_endian, writer.read(4))[0])
    self.data['bone_at_rest_bone_to_model_vertex_transformation'] = at_rest_bone
    at_rest_model = []
    for i in range(16):
      at_rest_model.append(struct.unpack(float_endian, writer.read(4))[0])
    self.data['bone_at_rest_model_to_bone_vertex_transformation'] = at_rest_model
    at_rest_parent = []
    for i in range(16):
      at_rest_parent.append(struct.unpack(float_endian, writer.read(4))[0])
    self.data['bone_at_rest_parent_to_bone_vertex_transformation'] = at_rest_parent
    at_rest_bone_parent = []
    for i in range(16):
      at_rest_bone_parent.append(struct.unpack(float_endian, writer.read(4))[0])
    self.data['bone_at_rest_bone_to_parent_vertex_transformation'] = at_rest_bone_parent
    self.data['bounding_sphere_radius'] = struct.unpack(float_endian, writer.read(4))[0]
    x = struct.unpack(float_endian, writer.read(4))[0]
    y = struct.unpack(float_endian, writer.read(4))[0]
    z = struct.unpack(float_endian, writer.read(4))[0]
    self.data['bounding_sphere_position'] = ma_util.Vector(3,x,y,z)
    self.data['skeleton_parent_bone_index'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    self.data['skeleton_child_bone_count'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    self.data['skeleton_child_array_start_index'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    self.data['flags'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    self.data['part_id'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    writer.read(3) #padding


  def print_header(self):
    print("--------------- Mesh Bone ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))

  def to_bytes(self):
    #TODO
    None

class MeshLight:
  def __init__(self, writer):
    self.data = {}
    self.data['offset'] = writer.tell()
    self.data['name'] = writer.read(16)
    self.data['per_pixel_texture_name'] = writer.read(16)
    self.data['corona_texture_name'] = writer.read(16)
    self.data['flags'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    self.data['light_id'] = int.from_bytes(writer.read(2), byteorder=endian, signed=False)
    self.data['light_type'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    self.data['parent_bone_index'] = int.from_bytes(writer.read(1), byteorder=endian, signed=False)
    self.data['intensity'] = struct.unpack(float_endian, writer.read(4))[0]
    color = {}
    color['red'] = struct.unpack(float_endian, writer.read(4))[0])
    color['blue'] = struct.unpack(float_endian, writer.read(4))[0])
    color['green'] = struct.unpack(float_endian, writer.read(4))[0])
    color['alpha'] = struct.unpack(float_endian, writer.read(4))[0])
    color['motif_index'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    self.data['color'] = color
    self.data['light_sphere_radius'] = struct.unpack(float_endian, writer.read(4))[0]
    x = struct.unpack(float_endian, writer.read(4))[0]
    y = struct.unpack(float_endian, writer.read(4))[0]
    z = struct.unpack(float_endian, writer.read(4))[0]
    self.data['light_sphere_position'] = ma_util.Vector(3,x,y,z)
    orientation = []
    for i in range(12):
      orientation.append(struct.unpack(float_endian, writer.read(4))[0])
    self.data['orientation'] = orientation
    self.data['spotlight_inner_radians'] = struct.unpack(float_endian, writer.read(4))[0]
    self.data['spotlight_outer_radians'] = struct.unpack(float_endian, writer.read(4))[0]
    self.data['corona_scale'] = struct.unpack(float_endian, writer.read(4))[0]

  def print_header(self):
    print("--------------- Mesh Bone ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))

  def to_bytes(self):
    #TODO

class MeshMaterial:
  def __init__(self, writer):
    self.data = {}
    self.data['offset'] = writer.tell()
    self.data['light_register_array_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)
    self.data['surface_register_array_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=false)
    self.data['light_shader_index'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['specular_shader_index'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['surface_shader_index'] = int.from_bytes(writer.read(2), byteorder=endian, signed=false)
    self.data['part_id_mask'] = int.from_bytes(writer.read(4), byteorder=endian, signed=false)
    self.data['platform_data_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=false)
    self.data['LOD_mask'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['depth_bias_level'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['number_of_base_st_sets'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['number_of_light_map_st_sets'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    texture_layer_id_index = []
    texture_layer_id_index.append(int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    texture_layer_id_index.append(int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    texture_layer_id_index.append(int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    texture_layer_id_index.append(int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['texture_layer_id_index'] = texture_layer_id_index
    self.data['affect_angle'] = struct.unpack(float_endian, writer.read(4))[0])
    self.data['compressed_affect_normal_1'] = int.from_bytes(writer.read(1), byteorder=endian, signed=true
    self.data['compressed_affect_normal_2'] = int.from_bytes(writer.read(1), byteorder=endian, signed=true
    self.data['compressed_affect_normal_3'] = int.from_bytes(writer.read(1), byteorder=endian, signed=true
    self.data['affect_bone_id'] = int.from_bytes(writer.read(1), byteorder=endian, signed=true
    self.data['compressed_radius'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false
    writer.read(1) #pad
    self.data['material_flags'] = int.from_bytes(writer.read(2), byteorder=endian, signed=false
    self.data['draw_key'] = int.from_bytes(writer.read(4), byteorder=endian, signed=false
    color = {}
    color['red'] = struct.unpack(float_endian, writer.read(4))[0])
    color['blue'] = struct.unpack(float_endian, writer.read(4))[0])
    color['green'] = struct.unpack(float_endian, writer.read(4))[0])
    self.data['color'] = color
    self.data['average_vert_position_x'] = struct.unpack(float_endian, writer.read(4))[0])
    self.data['average_vert_position_y'] = struct.unpack(float_endian, writer.read(4))[0])
    self.data['average_vert_position_z'] = struct.unpack(float_endian, writer.read(4))[0])
    self.data['display_list_hash_key'] = int.from_bytes(writer.read(4), byteorder=endian, signed=False)

    #now read child arrays and dont forget to reset reader!
    #TODO
    offset = writer.tell()

    writer.seek(offset)


  def print_header(self):
    print("--------------- Mesh Bone ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))

  def to_bytes(self):
    #TODO

class CollisionTree:
  def __init__(self, writer):
    self.data = {}
    self.data['offset'] = writer.tell()
    self.data['flags'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['segment_index'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['collision_mask'] = int.from_bytes(writer.read(2), byteorder=endian, signed=false)
    self.data['number_of_bits_in_fraction_component'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['tree_type'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['tree_node_count'] = int.from_bytes(writer.read(2), byteorder=endian, signed=false)
    self.data['tree_node_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=false)
    writer.read(2) # pad
    self.data['root_type'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['root_vertex_count'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['root_vert_position_x'] = struct.unpack(float_endian, writer.read(4))[0])
    self.data['root_vert_position_y'] = struct.unpack(float_endian, writer.read(4))[0])
    self.data['root_vert_position_z'] = struct.unpack(float_endian, writer.read(4))[0])
    self.data['bounding_sphere_radius'] = struct.unpack(float_endian, writer.read(4))[0]
    x = struct.unpack(float_endian, writer.read(4))[0]
    y = struct.unpack(float_endian, writer.read(4))[0]
    z = struct.unpack(float_endian, writer.read(4))[0]
    self.data['bounding_sphere_position'] = ma_util.Vector(3,x,y,z)
    self.data['bounding_capsule_start_position_x'] = struct.unpack(float_endian, writer.read(4))[0])
    self.data['bounding_capsule_start_position_y'] = struct.unpack(float_endian, writer.read(4))[0])
    self.data['bounding_capsule_start_position_z'] = struct.unpack(float_endian, writer.read(4))[0])
    self.data['bounding_capsule_end_position_x'] = struct.unpack(float_endian, writer.read(4))[0])
    self.data['bounding_capsule_end_position_y'] = struct.unpack(float_endian, writer.read(4))[0])
    self.data['bounding_capsule_end_position_z'] = struct.unpack(float_endian, writer.read(4))[0])
    self.data['bounding_capsule_radius'] = struct.unpack(float_endian, writer.read(4))[0])
    self.data['interval_array_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=false)


    #now read child arrays and dont forget to reset reader!
    #TODO
    offset = writer.tell()

    writer.seek(offset)


  def print_header(self):
    print("--------------- Mesh Bone ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))

  def to_bytes(self):
    #TODO

class TextureLayer:
  def __init__(self, writer):
    self.data = {}
    self.data['offset'] = writer.tell()
    self.data['layer_id'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['flags'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['flip_page_count'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['frames_per_flip'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['flip_array_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=false)
    self.data['scroll_rate_x'] = struct.unpack(float_endian, writer.read(4))[0])
    self.data['scroll_rate_y'] = struct.unpack(float_endian, writer.read(4))[0])
    self.data['degree_rotation_per_second'] = struct.unpack(float_endian, writer.read(4))[0])
    self.data['uv_rotate_anchor_x'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['uv_rotate_anchor_y'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    writer.read(2) #pad


    #now read child arrays and dont forget to reset reader!
    #TODO
    offset = writer.tell()

    writer.seek(offset)


  def print_header(self):
    print("--------------- Mesh Bone ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))

  def to_bytes(self):
    #TODO

class XboxMesh:
  def __init__(self, writer):
    self.data = {}
    self.data['offset'] = writer.tell()
    self.data['flags'] = int.from_bytes(writer.read(2), byteorder=endian, signed=false)
    self.data['vertex_buffer_count'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['index_buffer_count'] = int.from_bytes(writer.read(1), byteorder=endian, signed=false)
    self.data['disposable_object_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=false)
    self.data['bounding_sphere_radius'] = struct.unpack(float_endian, writer.read(4))[0]
    x = struct.unpack(float_endian, writer.read(4))[0]
    y = struct.unpack(float_endian, writer.read(4))[0]
    z = struct.unpack(float_endian, writer.read(4))[0]
    self.data['bounding_sphere_position'] = ma_util.Vector(3,x,y,z)
    self.data['platform_independent_mesh_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=false)
    self.data['vertex_buffer_array_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=false)
    self.data['collision_vertex_buffer_array_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=false)
    self.data['indices_count_array_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=false)
    self.data['index_buffer_array_offset'] = int.from_bytes(writer.read(4), byteorder=endian, signed=false)

    #now read child arrays and dont forget to reset reader!
    #TODO
    offset = writer.tell()

    writer.seek(offset)


  def print_header(self):
    print("--------------- Mesh Bone ---------------")
    for item in self.data:
      print(item + " : " + str(self.data[item]))

  def to_bytes(self):
    #TODO
