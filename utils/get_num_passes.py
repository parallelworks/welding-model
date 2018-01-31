import sys
import data_IO

coor_pass_file = data_IO.setOptionalSysArgs(sys.argv, 'pass_coordinates.out',1)
fcp = data_IO.open_file(coor_pass_file)

# First get the number of layers:
num_layers = data_IO.read_int_from_file_line_offset(fcp,'Number-of-Layers')

# Then, read the passes in each layer
num_passes = 0
for layer in range(num_layers):
    data = data_IO.read_ints_from_file_line_offset(fcp,'Layer,Number-of-Passes',
                                                   delimiter=',', offset=layer,end_line=1)
    num_passes = num_passes + data[1]

print(num_passes)


fcp.close()