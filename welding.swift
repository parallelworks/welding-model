import "stdlib.v2";

type file;

// ------ Input / Output Definitions -------

file feweldIn            <"inputs/eweld.in">;
file feweldParams        <"inputs/eweld_weld_parameters.in">	;
file feweldBC 		     <"inputs/eweld_boundary_condition.in">;
file feweldPreHeat 	     <"inputs/eweld_preheat_interpass_temperature.in">;
file feweldTempMonitor 	 <"inputs/eweld_temperature_monitor.in">;
file farcEffcSetting      <"setting/Setting_arc_efficiency_dfault.in">;

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

app (file fMeshUnv, file dfluxfile, file fsteps, file ferr, file fout) runAutoMesh (file feweldIn, file feweldParams, file farcEffcSetting, file fpassCoords, file[] utils){
	bash "./utils/runSalome.sh" dirname(fMeshUnv) dirname(fout) filename(fpassCoords) stderr=filename(ferr) stdout=filename(fout);
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
file fsteps            <strcat(caseOutDirs[i], "/model_step.in")>;
file autoMeshErr       <strcat(errorsDir, "autoMesh", i, ".err")>;                          
file autoMeshOut       <strcat(logsDir, "autoMesh", i, ".out")>;                          
(fMeshUnv, fdflux, fsteps, autoMeshErr, autoMeshOut) = runAutoMesh(feweldIn, feweldParams, farcEffcSetting, passCoords_files[i], utils);
meshUnv_files[i] = fMeshUnv;
dflux_files[i] = fdflux;
step_files[i] = fsteps;
