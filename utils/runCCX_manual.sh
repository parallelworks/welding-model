#!/bin/bash

if [[ $# -lt 1 ]]; then
 	np=1
else
	np=$1
fi

if [[ $# -lt 2 ]]; then
 	maxPasses2Run=1000
else
	maxPasses2Run=$2
fi 

ccx_MT=./ccx_2.12_MT

# Get number of weld passes
numPasses="$(python utils/get_num_passes.py inputs/pass_coordinates.out )" 
# Make sure number of passes is less than the maximum number of passes 
numPasses=$(($numPasses<$maxPasses2Run?$numPasses:$maxPasses2Run))
echo "Running $numPasses passes"

# Setup variables for running CalculiX with muliple threads

export OMP_NUM_THREADS=$np
export CCX_NPROC_RESULTS=$np # for subroutine calcs
export CCX_NPROC_EQUATION_SOLVER=$np
export NUMBER_OF_CPUS=$np
echo "###########################################"
echo "Using $np processor(s)"
echo "###########################################"

ccxInputRoot=model_step
Counter=1
RunningOK=true

# First input file is named analysis.inp

echo "###########################################"
echo "Solving step $Counter"
echo "###########################################"

# Run CalculiX and export to EXODUSII for Paraview  
$ccx_MT analysis  -o exo  

if [ ! -f analysis.rout ]; then
	echo "Calculix Step $Counter: $? was Unsuccessful" 
	RunningOK=false
else
	cp analysis.rout  ${ccxInputRoot}$((Counter+1)).rin
	let Counter=Counter+1 
fi

# Continue with the following steps
while [  $Counter -le $numPasses ] && [ "$RunningOK" = true ]; do

	echo "###########################################"
    echo "Solving step $Counter"
	echo "###########################################"

	# Run CalculiX and export to EXODUSII for Paraview  
	$ccx_MT $ccxInputRoot$Counter  -o exo  

	if [ ! -f $ccxInputRoot$Counter.rout ]; then
		echo "Calculix Step $Counter: $? was Unsuccessful" 
		RunningOK=false
	else
		cp $ccxInputRoot$Counter.rout $ccxInputRoot$((Counter+1)).rin 
		let Counter=Counter+1 
	fi
done

echo Simulation Complete.
echo ""

# Compress exo files
tar -cf ccx-results.tar   *.exo *.sta *.cvg

