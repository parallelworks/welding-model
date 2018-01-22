#!/bin/bash 
outputDir=$1
logDir=$2
weldPassfile=$3

echo $SALOMEPATH/salome start -t -w 1 utils/Automesh_v14.py  args:--out_dir=$ouptutDir,--log_dir=$logDir,--weld_pass_coordinates_file=$weldPassfile

$SALOMEPATH/salome start -t -w 1 utils/Automesh_v14.py  args:--out_dir=$outputDir,--log_dir=$logDir,--weld_pass_coordinates_file=$weldPassfile
