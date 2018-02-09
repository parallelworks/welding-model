# This workflow is a tester/runner for the mex app (in lib/mex.swift app).
# Run this workflow from the root directory of the repository

import "stdlib.v2";
import "lib/mex";

type file;

// For faster testing:
string maxPasses2Run = "3";

// workflow structure definitions:
string inputDir           = "inputs/";
string outDir             = "results/";
string modelsDir          = "utils/";
string settingsDir        = "setting/";
string caseDirRoot        = strcat(outDir, "case_"); 
string errorsDir          = strcat(outDir, "errorFiles/");
string logsDir            = strcat(outDir, "logFiles/");

//----------------Workflow-------------------

int i=1;

string[] caseOutDirs;
caseOutDirs[i]            = strcat(caseDirRoot, i,"/");
file[] mexCsvFiles;

// set input and output directories
string mexInputDir        = strcat(inputDir, "mex/");
string mexOutputDir       = strcat(caseOutDirs[i], "mex/");

file fmex_kpi             <strcat(mexSettings, "/welding_anim.json")>;

file fsteps               <strcat(mexInputDir, "/model_step.tar")>;
file fccxResults          <strcat(mexInputDir, "/ccx-results.tar")>; 
file fpassCoords 	      <strcat(mexInputDir, "/pass_coordinates.out")>; 

file mexCsvOut            <strcat(mexOutputDir, "metrics.csv")>;
file fmexPngs[]           <filesys_mapper;location=mexOutputDir>;
(mexCsvOut, fmexPngs, fmexErr, fmexLog) = runMex(fsteps, fccxResults, fmex_kpi, mexOutputDir, fpassCoords, maxPasses2Run, mex_utils, ccx_utils);
mexCsvFiles[i] = mexCsvOut;
