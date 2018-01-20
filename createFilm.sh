#!/bin/bash 

./tools/unical Mesh_3D.unv Model3d_4cgx.inp
./tools/cgx_2.12 -bg write_film.fbd 
mv sFilmSurface.flm model_film.in
cat all.msh *.nam > allinone.inp 
rm *.nam 
rm all.msh
