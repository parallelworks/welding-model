#!/bin/bash 
eweldinFile=$1
weldParamsFile=$2
outputDir=$3
logDir=$4
weldPassfile=$5

export PATH=$SALOMEPATH:$PATH						 
salome start -t -w 1 utils/Automesh_v14.py  args:--eweld_file=$eweldinFile,--weld_parameters_file=$weldParamsFile,--out_dir=$outputDir,--log_dir=$logDir,--weld_pass_coordinates_file=$weldPassfile,--write_separate_step_files

cd $outputDir
tar -cf model_step.tar  model_step?*.inp
