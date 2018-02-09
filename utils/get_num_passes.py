import sys
import data_IO
from calculix import calculix_utils 

pass_coor_file = data_IO.setOptionalSysArgs(sys.argv, 'pass_coordinates.out', 1)

weld_passes = calculix_utils.WeldPasses(pass_coor_file)

print(weld_passes.num_passes)

