import "stdlib.v2";
import "lib/strFunctions";
import "lib/mex";

type file;

// ------ Input / Output Definitions -------

string numProcs = arg("ProcessorsPerRun", "4");

// Only for testing
string maxPasses2Run = arg("maxPasses2Run","3");

// Pick input files depending on this is a test run or not:
boolean testRun = str2bool(arg("test_run","true"));
string inputDir;
if (testRun) {
	inputDir           = "inputs/test_run/";
}
else{
	 inputDir           = "inputs/long_run/";
}

string outDir             = "results/";
string modelsDir          = "utils/";
string settingsDir        = "setting/";
string caseDirRoot        = strcat(outDir, "case_");
string errorsDir          = strcat(outDir, "errorFiles/");
string logsDir            = strcat(outDir, "logFiles/");

file feweldIn             <arg("feweldIn",			strcat(inputDir, "eweld.in"))>;
file feweldParams         <arg("feweldParams",		strcat(inputDir, "eweld_weld_parameters.in"))>;
file feweldBC 		      <arg("feweldBC",			strcat(inputDir, "eweld_boundary_condition.in"))>;
file feweldPreHeat 	      <arg("feweldPreHeat",		strcat(inputDir, "eweld_preheat_interpass_temperature.in"))>;
// file feweldTempMonitor 	  <arg("feweldTempMonitor",	strcat(inputDir, "eweld_temperature_monitor.in"))>;

file mexCsvOut <arg("mexCsvOut","results/output.csv")>;
file mexPngsOut <arg("mexPngsOut","results/mex.tar")>;

// -------- Settings ----------------------

file farcEffcSetting      <strcat(settingsDir, "Setting_arc_efficiency_dfault.in")>;

file fmex_kpi             <strcat(mexSettings, "/welding.json")>;

file analysisFile           <"analysis.inp">;
file ffilmFbd               <"utils/write_film.fbd">;
file materials[] 		    <filesys_mapper;location="material", pattern="?*.in">;

file utils[] 		        <filesys_mapper;location=modelsDir, pattern="?*.*">;
file tools[] 		        <filesys_mapper;location="tools", pattern="?*">;

file CalculiX               <"tools/CalculiX-PW.tgz">;

// ------ App Definitions --------------------

app (file fpassCoords, file ferr, file fout) calcArcPasses (file feweldIn, file[] utils) {
	chmod "+x" "./utils/determine_passes_arc_v4.out";
	determine_arc_passes filename(feweldIn) strcat(dirname(fpassCoords),"/") stderr=filename(ferr) stdout=filename(fout);
}

app (file fMeshUnv, file dfluxfile, file fsteps, file ferr, file fout) runAutoMesh (file feweldIn, file feweldParams, file farcEffcSetting, file fpassCoords, file[] utils){
	bashSalome "./utils/runSalome.sh" filename(feweldIn) filename(feweldParams) dirname(fMeshUnv) dirname(fout) filename(fpassCoords) stderr=filename(ferr) stdout=filename(fout);
}

app (file ffilm, file fMeshInp, file ferr, file fout) runCGX (file fMeshUnv, file fflimFbd, file[] utils, file[] tools){
	bashCGX "./utils/runCGX.sh" filename(fMeshUnv) filename(fflimFbd) filename(ffilm) filename(fMeshInp) stderr=filename(ferr) stdout=filename(fout);
}

app (file analysis_files, file ferr, file fout) createAnalysisFiles (file feweldIn, file feweldBC, file feweldPreHeat, file fMeshInp, file[] utils, file[] ccx_utils){
	python2 "utils/Analysis_file_create.py" strcat("--eweld_file=",filename(feweldIn)) strcat("--eweld_BC_file=",filename(feweldBC)) strcat("--eweld_preheat_temp_file=",filename(feweldPreHeat)) strcat("--model_inp_file=",filename(fMeshInp))  strcat("--log_dir=",dirname(fout)) strcat("--out_dir=",dirname(analysis_files)) stderr=filename(ferr) stdout=filename(fout);
	tar "-cf"  filename(analysis_files) "-C" dirname(analysis_files) "model_bc.in" "model_ini_temperature.in" "model_material.in";
}

app (file ccxBin, file ferr, file fout) compileCcx (file fdflux, file CalculiX, file utils[]){
	bashCompileCcx "./utils/compileCcx.sh" filename(fdflux) filename(CalculiX) filename(ccxBin) stderr=filename(ferr) stdout=filename(fout);
}

app (file ccxResults, file ferr, file fout) runCCX (file fsteps, file analysis_files, file ccxBin, file pass_coordinates, file ffilm, file fMeshInp, string numProcs, string maxPasses2Run, file analysisFile, file[] materials, file[] utils, file[] ccx_utils){
	bashRunCcx "./utils/runCCX.sh" filename(fsteps) filename(analysis_files) filename(ccxBin) filename(pass_coordinates) filename(ffilm) filename(fMeshInp) filename(ccxResults) numProcs maxPasses2Run stderr=filename(ferr) stdout=filename(fout);
}

// Add a dummy application function for the application bashMex to get detected/define resource on Parallel Works platform
app (file fout) dummyMex (file fin){
	bashMex filename(fout);
}


//----------------Workflow-------------------

// Create the weld pass coordinates
int i=1;
file[] passCoords_files;
string[] caseOutDirs;
caseOutDirs[i]         = strcat(caseDirRoot, i,"/");
file fpassCoords 	   <strcat(caseOutDirs[i], "/pass_coordinates.out")>;
file arcPassErr        <strcat(errorsDir, "arcPass", i, ".err")>;
file arcPassOut        <strcat(logsDir, "arcPass", i, ".out")>;
(fpassCoords, arcPassErr, arcPassOut) = calcArcPasses(feweldIn, utils);
passCoords_files[i] = fpassCoords;

file[] meshUnv_files;
file[] dflux_files;
file[] step_files;
file fMeshUnv          <strcat(caseOutDirs[i], "/Mesh_3D.unv")>;
file fdflux            <strcat(caseOutDirs[i], "/model_dflux.for")>;
file fsteps            <strcat(caseOutDirs[i], "/model_step.tar")>;
file autoMeshErr       <strcat(errorsDir, "autoMesh", i, ".err")>;
file autoMeshOut       <strcat(logsDir, "autoMesh", i, ".out")>;
(fMeshUnv, fdflux, fsteps, autoMeshErr, autoMeshOut) = runAutoMesh(feweldIn, feweldParams, farcEffcSetting, passCoords_files[i], utils);
meshUnv_files[i] = fMeshUnv;
dflux_files[i] = fdflux;
step_files[i] = fsteps;

file[] meshInp_files;
file[] film_files;
file fMeshInp          <strcat(caseOutDirs[i], "/nodesElems.inp")>;
file ffilm                 <strcat(caseOutDirs[i], "/model_film.in")>;
file runCGXErr         <strcat(errorsDir, "runCGX", i, ".err")>;
file runCGXOut         <strcat(logsDir, "runCGX", i, ".out")>;
(ffilm, fMeshInp, runCGXErr, runCGXOut) = runCGX(meshUnv_files[i], ffilmFbd, utils, tools);
film_files[i] = ffilm;
meshInp_files[i] = fMeshInp;

file analysis_files[];
file fAnal                   <strcat(caseOutDirs[i], "/analFiles.tar")>;
file createAnalFilesErr         <strcat(errorsDir, "createAnalFiles", i, ".err")>;
file createAnalFilesOut         <strcat(logsDir, "createAnalFiles", i, ".out")>;
(fAnal,createAnalFilesErr, createAnalFilesOut) = createAnalysisFiles(feweldIn, feweldBC, feweldPreHeat, meshInp_files[i], utils, ccx_utils);
analysis_files[i] = fAnal;

file ccxExec_files[];
file fccxExec                    <strcat(caseOutDirs[i], "/ccx_2.12_MT")>;
file compileCCXErr               <strcat(errorsDir, "compileCCX", i, ".err")>;
file compileCCXOut               <strcat(logsDir, "compileCCX", i, ".out")>;
(fccxExec, compileCCXErr, compileCCXOut) = compileCcx(dflux_files[i], CalculiX, utils);
ccxExec_files[i] = fccxExec;


file ccxResult_files[];
file fccxResult        <strcat(caseOutDirs[i], "/ccx-results.tar")>;
file runCCXErr         <strcat(errorsDir, "runCCX", i, ".err")>;
file runCCXOut         <strcat(logsDir, "runCCX", i, ".out")>;
(fccxResult, runCCXErr, runCCXOut) = runCCX (step_files[i], analysis_files[i], ccxExec_files[i], passCoords_files[i], film_files[i], meshInp_files[i], numProcs, maxPasses2Run, analysisFile, materials, utils, ccx_utils);
ccxResult_files[i] = fccxResult;

string mexOutputDir       = strcat(caseOutDirs[i], "mex/");
file fmexPngs[]           <filesys_mapper;location=mexOutputDir>;
(mexCsvOut, mexPngsOut, fmexPngs, fmexErr, fmexLog) = runMex(step_files[i], ccxResult_files[i], fmex_kpi, mexOutputDir, passCoords_files[i], maxPasses2Run, mex_utils, ccx_utils);
