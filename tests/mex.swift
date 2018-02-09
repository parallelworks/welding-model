import "stdlib.v2";

type file;

// Only for testing 
string maxPasses2Run = "3";

string inputDir           = "inputs/";
string outDir             = "results/";
string modelsDir          = "utils/";
string settingsDir        = "setting/";
string caseDirRoot        = strcat(outDir, "case_"); 
string errorsDir          = strcat(outDir, "errorFiles/");
string logsDir            = strcat(outDir, "logFiles/");


//file mex_utils[]          <filesys_mapper;location=strcat(modelsDir, "mexdex"), pattern="?*.*">;
file mex_utils[]          <filesys_mapper;location="utils/mexdex", pattern="?*.*">;
file ccx_utils[]          <filesys_mapper;location="utils/calculix", pattern="?*.*">;

// ------ App Definitions --------------------

app (file fmexCsv, file[] fmexpngs, file ferr, file fout) runMex (file fsteps, file fccxResults, file fmex_kpi, string mexOutputDir, file fpassCoords, string maxPasses2Run, file[] mex_utils, file[] ccx_utils){
	bash "./utils/mexdex/extract.sh" filename(fsteps) filename(fccxResults) filename(fmex_kpi) mexOutputDir filename(fmexCsv) filename(fpassCoords) maxPasses2Run stderr=filename(ferr) stdout=filename(fout);
}

//----------------Workflow-------------------

int i=1;
file[] passCoords_files;
string[] caseOutDirs;

caseOutDirs[i]            = strcat(caseDirRoot, i,"/");
file[] mexCsvFiles;

string mexInputDir        = strcat(inputDir, "mex/");
string mexOutputDir       = strcat(caseOutDirs[i], "mex/");
string mexSettings        = strcat(settingsDir, "mex/");
string mexErrorsDir       = strcat(errorsDir, "mex/");
string mexLogsDir         = strcat(logsDir, "mex/");

file fsteps               <strcat(mexInputDir, "/model_step.tar")>;
file fccxResults          <strcat(mexInputDir, "/ccx-results.tar")>; 
file fpassCoords 	      <strcat(mexInputDir, "/pass_coordinates.out")>;

file fmex_kpi             <strcat(mexSettings, "/welding_anim.json")>;

file fmexPngs[]           <filesys_mapper;location=mexOutputDir>;
file mexCsvOut            <strcat(mexOutputDir, "metrics.csv")>;
file fmexErr              <strcat(mexErrorsDir, "mex", i ,".err")>;
file fmexLog              <strcat(mexLogsDir, "mex", i, ".out")>;
(mexCsvOut, fmexPngs, fmexErr, fmexLog) = runMex(fsteps, fccxResults, fmex_kpi, mexOutputDir, fpassCoords, maxPasses2Run, mex_utils, ccx_utils);
mexCsvFiles[i] = mexCsvOut;
