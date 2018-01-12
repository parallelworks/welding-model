# To convert to md use this command (org export doesn't work with nested lists:)
# pandoc --from org --to markdown_github  README_json0.org  -s -o README_json0.md
#+OPTIONS: toc:nil
#+OPTIONS: ^:nil

* Welding workflow modules
  This repository contains the modules for automatically creating the  files required for 
  simulating a welding case by CalculiX based on the user specifications/output files from a web interface. 
  The modules create mesh files, convert them to CalculiX input format, create CalculiX input files, and 
  CalculiX user defined heat source file, =dflux.f= for defining the heat source for welding steps.

** Required software
   - The geometry and mesh is generated using [[http://www.salome-platform.org/][Salome platform]]
   - The thrmomechanical simulation of the welding process is performed with the open source [[http://www.dhondt.de/][CalculiX FEA solver]]
** Instructions
   Instructions for running the files are in =docs/Instruction_flow.pdf= 
