Welding workflow
================

This workflow implements a case runner for the thermomechanical simulation of a V-Groove welding process based on the user specifications input files.

In this workflow, which is implemented in [Swift](http://swift-lang.org/main/):

-   The geometry and mesh is generated using [Salome platform](http://www.salome-platform.org/) (version 8.2.0)
-   The generated mesh by salome is converted to CalculiX format using [CalculiX GraphiX (cgx)](http://www.dhondt.de/) and unical.
-   The thrmomechanical simulation of the welding process is performed with the open source [CalculiX FEA solver](http://www.dhondt.de/) (version 2.12)
-   Post-processing is performed using [ParaView](https://www.paraview.org/) and a [python library](https://github.com/parallelworks/MetricExtraction) developed by Parallel Works for automated generation of output images and metrics extraction.

This repository contains the modules for automatically creating the files required for simulating a welding case by CalculiX. The workflow involves the following steps:

-   Calculate the weld pass coordinates based on user inputs (`calcArcPasses`)
-   Create geometry and mesh (unv) files using Salome. In this step the user defined file for defining the weld heat source, `dflux.f`, is also created (`runAutoMesh`)
-   Convert unv mesh files to CalculiX/Abaqus input format using cgx and unical (`runCGX`)
-   Create CalculiX analysis files and the based on user inputs (`createAnalysisFiles`)
-   Compile CalculiX with the user defined file for weld heat source, `dflux.f` (`complileCcx`)
-   Run CalculiX (`runCCX`)
-   Post-process results using ParaView and a python library (`runMex`) The steps of the workflow are detailed in `docs/Instruction_flow.pdf`.

Instructions
------------

### Running the workflow from on Parallel Works platform

To run the workflow in Parallel Works, upload/select the input files in the input form. The input files specify:

-   Geometry, materials, type, ... (e.g., `eweld.in`)
-   The power and speed of each weld pass (e.g., `eweld_weld_parameters.in`)
-   Boundary conditions, i.e., fixed points and directions (e.g., see `eweld_boundary_condition.in` file)
-   Preheat and interpass temperatures (e.g., `eweld_boundary_condition.in` file)

Sample input files under `inputs/long_run` directory (for larger jobs), and under `inputs/test_run` directory (for fast running tests).

### Running the workflow from command line:

The main swift script for the welding model workflow is `welding.swift` file.

-   Before running the workflow, start the coaster service via `pworks` command with two workers:

    ``` example
    pworks cluster 2 
    ```

-   To run the `welding.swift` workflow, run this command from the workflow directory:

    ``` example
    swift welding.swift
    ```
