import "stdlib.v2";

type file;

string mex_utilsDir       = strcat(modelsDir, "mexdex");
string ccx_utilsDir       = strcat(modelsDir, "calculix");
file mex_utils[]          <filesys_mapper;location=mex_utilsDir, pattern="?*.*">;
file ccx_utils[]          <filesys_mapper;location=ccx_utilsDir, pattern="?*.*">;

string mexSettings        = strcat(settingsDir, "mex/");
string mexErrorsDir       = strcat(errorsDir, "mex/");
string mexLogsDir         = strcat(logsDir, "mex/");

file fmexErr              <strcat(mexErrorsDir, "mex", i ,".err")>;
file fmexLog              <strcat(mexLogsDir, "mex", i, ".out")>;

// ------ App Definitions --------------------

app (file fmexCsv, file fpostOut, file[] fmexpngs, file ferr, file fout) runMex (file fsteps, file fccxResults, file fmex_kpi, string mexOutputDir, file fpassCoords, string maxPasses2Run, file[] mex_utils, file[] ccx_utils){
	bashMex "./utils/mexdex/extract.sh" filename(fsteps) filename(fccxResults) filename(fmex_kpi) mexOutputDir filename(fmexCsv) filename(fpassCoords) filename(fpostOut) maxPasses2Run stderr=filename(ferr) stdout=filename(fout);
}
