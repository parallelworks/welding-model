#!/bin/bash 
outputDir=$1
logDir=$2
weldPassfile=$3

export PATH=$SALOMEPATH:$PATH						 
salome start -t -w 1 utils/Automesh_v14.py  args:--out_dir=$outputDir,--log_dir=$logDir,--weld_pass_coordinates_file=$weldPassfile,--write_separate_step_files

cd $outputDir
tar -cf model_step.tar  model_step?*.inp
