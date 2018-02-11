#!/bin/bash 

# Run a single case

export SALOMEPATH=/home/marmar/programs-local/SALOME-8.2.0-UB14.04/
export PARAVIEWPATH=/home/marmar/programs-local/ParaView-5.3.0-Qt5-OpenGL2-MPI-Linux-64bit/bin

mkdir -p results/case_1/
mkdir -p results/logFiles/

# Create the pass_coordinates.out file:
./utils/determine_passes_arc_v4.out  results/case_1/ 

# Run Salome to creat the mesh (unv file):
./utils/runSalome.sh results/case_1/ results/logFiles results/case_1/pass_coordinates.out

# Convert the unv files to CaluculiX/Abaqus format 
./utils/runCGX.sh results/case_1/Mesh_3D.unv utils/write_film.fbd results/case_1/model_film.in results/case_1/nodesElems.inp


# Create CalculiX analysis files and archive them
python2 utils/Analysis_file_create.py --model_inp_file=results/case_1/nodesElems.inp \
	--log_dir=results/logFiles --out_dir=results/case_1/ 
tar -cf results/case_1/analFiles.tar -C results/case_1/ model_bc.in model_ini_temperature.in model_material.in 

# Compile CalculiX
./utils/compileCcx.sh results/case_1/model_dflux.for tools/CalculiX-PW.tar results/case_1/ccx_2.12_MT

# Run CacluliX
./utils/runCCX.sh results/case_1/model_step.tar results/case_1/analFiles.tar results/case_1/ccx_2.12_MT results/case_1/pass_coordinates.out results/case_1/model_film.in results/case_1/nodesElems.inp results/case_1/ccx-results.tar 4 

# Run post-processing
./utils/mexdex/extract.sh results/case_1/model_step.tar results/case_1/ccx-results.tar setting/mex/welding_anim.json results/case_1/mex/ results/case_1/mex/metrics.csv results/case_1/pass_coordinates.out 
