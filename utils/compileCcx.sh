#!/bin/bash -e
dfluxFile=$1
ccxDirTar=$2
ccxBin=$3

workDir=$(pwd)

# Get ccxDir name from $ccxDirTAr
filename=$(basename "$ccxDirTar")
ccxDir0="${filename%.*}"
ccxDir="${ccxDir0%.*}"

# Decompress CalculiX files and copy the dflux.f file into CalculiX src directory
tar -zxf $ccxDirTar 
cp $dfluxFile $ccxDir/src/dflux.f

cd $ccxDir/src
make 

cd $workDir
cp $ccxDir/src/ccx_2.12_MT $ccxBin
chmod +x $ccxBin

