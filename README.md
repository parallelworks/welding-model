Welding workflow modules
========================

This repository contains the modules for automatically creating the files required for simulating a welding case by CalculiX based on the user specifications/output files from a web interface. The modules create mesh files, convert them to CalculiX input format, create CalculiX input files, and CalculiX user defined heat source file, `dflux.f` for defining the heat source for welding steps.

Required software
-----------------

-   The geometry and mesh is generated using [Salome platform](http://www.salome-platform.org/)
-   The thrmomechanical simulation of the welding process is performed with the open source [CalculiX FEA solver](http://www.dhondt.de/)

Instructions
------------

Instructions for running the files are in `docs/Instruction_flow.pdf`
