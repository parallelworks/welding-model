Welding workflow
================

This workflow implements a case runner for the thermomechanical simulation of a V-Groove welding process based on the user specifications input files.

In this workflow, which is implemented in [Swift](http://swift-lang.org/main/):

-   The geometry and mesh is generated using [Salome platform](http://www.salome-platform.org/) (version 8.2.0)
-   The generated mesh by salome is converted to CalculiX format using [CalculiX GraphiX (cgx)](http://www.dhondt.de/) and unical.
-   The thrmomechanical simulation of the welding process is performed with the open source [CalculiX FEA solver](http://www.dhondt.de/) (version 2.12)
-   Post-processing is performed using [ParaView](https://www.paraview.org/) and a [python library](https://github.com/parallelworks/MetricExtraction) developed by Parallel Works for automated generation of output images and metrics extraction.

This repository contains the modules for automatically creating the files required for simulating a welding case by CalculiX. The modules create geometry, mesh files, convert them to CalculiX input format, create CalculiX input files, and CalculiX user defined heat source file, `dflux.f` for defining the heat source for welding steps, compile and run multi-threaded CalculiX, and post-process the results using ParaView and a python library. The steps of the workflow are detailed in `docs/Instruction_flow.pdf`.

Instructions
------------

To run the workflow, upload/select the input files in the input form. The input files specify:

-   Geometry, materials, type, ... (e.g., `eweld.in`)
-   The power and speed of each weld pass (e.g., `eweld_weld_parameters.in`)
-   Boundary conditions, i.e., fixed points and directions (e.g., see `eweld_boundary_condition.in` file)
-   Preheat and interpass temperatures (e.g., `eweld_boundary_condition.in` file)

Sample input files are uploaded in the workspace and can also be found in `inputs/` directory (for larger jobs), and under `tests/inputs/weld/` directory (for fast running tests).
