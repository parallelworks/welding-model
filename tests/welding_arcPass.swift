import "stdlib.v2";

type file;

// ------ Input / Output Definitions -------

file feweldIn            <"inputs/eweld.in">;
file feweldParams        <"inputs/eweld_weld_parameters.in">	;
file feweldBC 		     <"inputs/eweld_boundary_condition.in">;
file feweldPreHeat 	     <"inputs/eweld_preheat_interpass_temperature.in">;
file feweldTempMonitor 	 <"inputs/eweld_temperature_monitor.in">;

string outDir               = "results/";
string errorsDir            = strcat(outDir, "errorFiles/");
string logsDir              = strcat(outDir, "logFiles/");
string caseDirRoot          = strcat(outDir, "case_"); 

file utils[] 		        <filesys_mapper;location="utils", pattern="?*.*">;

// ------ App Definitions --------------------

app (file fpassCoords, file ferr, file fout) calcArcPasses (file feweldIn, file[] utils) {
	chmod "+x" "./utils/determine_passes_arc_v4.out";
	"./utils/determine_passes_arc_v4.out"  strcat(dirname(fpassCoords),"/") stderr=filename(ferr) stdout=filename(fout);
}


//----------------Workflow-------------------

// Create the weld pass coordinates
int i=1;
file[] passCoords_files;
string[] caseOutDirs;

caseOutDirs[i]      = strcat(caseDirRoot, i,"/");
file fpassCoords 	  <strcat(caseOutDirs[i], "/pass_coordinates.out")>;
file arcPassErr       <strcat(errorsDir, "arcPass", i, ".err")>;                          
file arcPassOut       <strcat(logsDir, "arcPass", i, ".out")>;                          
(fpassCoords, arcPassErr, arcPassOut) = calcArcPasses(feweldIn, utils);
passCoords_files[i] = fpassCoords;

