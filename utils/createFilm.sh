#!/bin/bash 
# Example:
# ./utils/createFilm.sh results/case_1/Mesh_3D.unv ./utils/write_film.fbd   results/case_1/model_film.in  results/case_1/allinone.inp 

unvFile=$1
fbdFile=$2
filmFile=$3
echo "Number of arguments: " 
echo $#

if [[ $# -ne 4 ]]; then
 	allinoneFile=allinone.inp 
else
	allinoneFile=$4
fi
echo "allinoneFile: " 
echo $allinoneFile

chmod +x ./tools/unical
chmod +x ./tools/cgx_2.12
./tools/unical $unvFile Model3d_4cgx.inp
./tools/cgx_2.12 -bg $fbdFile
mv sFilmSurface.flm $filmFile 
cat all.msh *.nam > $allinoneFile
rm *.nam 
rm all.msh
