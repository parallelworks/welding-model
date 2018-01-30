#!/bin/bash 
# Example:
# ./utils/createFilm.sh results/case_1/Mesh_3D.unv ./utils/write_film.fbd   results/case_1/model_film.in  results/case_1/allinone.inp 

unvFile=$1
fbdFile=$2


if [[ $# -lt 3 ]]; then
 	filmFile=model_film.in 
else
	filmFile=$3 
fi


if [[ $# -lt 4 ]]; then
 	nodesElemsFile=nodesElems.inp 
else
	nodesElemsFile=$4
fi
echo "nodesElemsFile: " 
echo $nodesElemsFile

chmod +x ./tools/unical
chmod +x ./tools/cgx_2.12
./tools/unical $unvFile Model3d_4cgx.inp
./tools/cgx_2.12 -bg $fbdFile
mv sFilmSurface.flm $filmFile 
cat all.msh *.nam > $nodesElemsFile
rm *.nam 
rm all.msh
