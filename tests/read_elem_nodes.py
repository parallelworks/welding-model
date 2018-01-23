from utils import data_IO
from utils import calculix_utils as cu

input_file = '../Model3d.inp'

model3d_mesh = cu.Mesh()
model3d_mesh.read_mesh_from_inp(input_file)
print(model3d_mesh.node_set_names())
print(model3d_mesh.element_set_names())

print(model3d_mesh.num_all_elements())
print(model3d_mesh.num_elements_in_sets())
print(model3d_mesh.num_nodes_in_sets())

elem_set_names = model3d_mesh.element_set_names()
iFS = data_IO.get_index_in_str_list(elem_set_names,'FilmSurface')
print (iFS)