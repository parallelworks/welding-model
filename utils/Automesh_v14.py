##################################################################
#
#   AutoMesh, Version 1.000 
#   technical contact: yyang@ewi.org;yupyang@gmail.com 
#
##################################################################
#
# -*- coding: utf-8 -*-
#
#-- SYSTEM IMPORTS ---##
import os
import os, fnmatch 
import os.path
import shutil
import sys
import glob
import math
from math import *
import argparse

import data_IO

parser = argparse.ArgumentParser(
    description='Run under Salome to create the mesh, step file and dflux.f files for a welding case')

parser.add_argument("--weld_pass_coordinates_file", default= "inputs/pass_coordinates.out",
                    help='The file that has the weld pass coordinates'
                         '(default:"inputs/pass_coordinates.out")')

parser.add_argument("--out_dir", default= "./",
                    help='The output directory (default:"./")')


parser.add_argument("--log_dir", default= "./",
                    help='The log directory (default:"./")')

parser.add_argument("--write_seperate_step_files", dest='write_separate_step_files',
                    action='store_true',
                    help='If set, the step for each welding pass (depositing, heating '
                         'and cooling steps) will be written into a separate '
                         'file (e.g, model_step1.inp, model_step2.inp,...) - the default '
                         'is to write all the steps into a single file (model_step1.inp)')

parser.add_argument("--write_single_step_file", dest='write_separate_step_files',
                    action='store_false',
                    help='If set, a single file  (model_step1.inp) will be writen for all '
                         'the simulation steps (also see --write_seperate_step_files). '
                         'This is the default ')

parser.set_defaults(write_separate_step_files=False)

args = parser.parse_args()
write_separate_step_files = args.write_separate_step_files
out_dir = args.out_dir
log_dir = args.log_dir

logfile = open(os.path.join(log_dir, "AutoMesh.log"), "w" )

cwd=os.getcwd() 
logfile.write("Work directory = " + os.path.dirname(logfile.name) +'\n')
#
#------------------- Input Parameters -----------------------
#
#length = 200
hazSize = 10
hazExt = 20
sv=0.01
#reinf=1.5
lwt=6.35
gelemaxsize = 25.0
geleminsize = 4.0
nelethick = 3
weldelesize = 1.0
hazelesize = 2.0
extelesize = 3.0
distmerge = 0.001
#------------------------------------------------------------
#--arc efficiency
#------------------------------------------------------------
logfile.write("Read heat source efficiency" +'\n')

eff_file = os.path.join(cwd,"setting/Setting_arc_efficiency_dfault.in")

eff=[ [],]*7        
filein = open(eff_file, "r" )
lines = filein.readlines()
#--- GMAW
eff[0]=float(lines[1])
logfile.write("*GMAW =     " + str(eff[0]) +'\n' )
#--- P-GMAW	
eff[1]=float(lines[3])
logfile.write("*P-GMAW =   " + str(eff[1]) +'\n' )
#--- W-P-GMAW
eff[2]=float(lines[5]) 
logfile.write("*W-P-GMAW = " + str(eff[2]) +'\n' )
#--- GTAW
eff[3]=float(lines[7])
logfile.write("*GTAW =     " + str(eff[3]) +'\n' )
#--- SAW	
eff[4]=float(lines[9])
logfile.write("*SAW =      " + str(eff[4]) +'\n' )
#--- SMAW	
eff[5]=float(lines[11])
logfile.write("*GMAW =     " + str(eff[5]) +'\n' )
#--- Other
eff[6]=float(lines[13])
logfile.write("*GMAW =     " + str(eff[6]) +'\n' )
filein.close() 
#------------------------------------------------------------
#-- Determine heat source efficiency
#------------------------------------------------------------
def arc_efficiency(weld_type,vol):
    arc_eff="Yes"
    if weld_type=='GMAW':
      if(arc_eff=="Yes"):
        eff_cal=eff[0]
      else:
        if(vol >= 26.9):
              eff_cal=0.5
        elif(vol <= 22.8):          
              eff_cal=0.87       
        elif(vol > 22.8 and vol < 26.9):
              eff_cal=0.87+(vol-22.80)*(0.5-0.87)/(26.9-22.8)
        else:
              eff_cal=0.5
    elif weld_type=='P-GMAW':
       eff_cal=eff[1]
    elif weld_type=='W-P-GMAW':
       eff_cal=eff[2]
    elif weld_type=='GTAW':
       eff_cal=eff[3]
    elif weld_type=='SAW':
       eff_cal=eff[4]    
    elif weld_type=='SMAW':
       eff_cal=eff[5]   
    else:
       eff_cal=eff[6]
    so="Efficiency=" + str(eff_cal)
    logfile.write(so +'\n')
    return eff_cal
#-------------------------------------------------------------
#--------------- Read eweld.in ------------------------------
#-------------------------------------------------------------
eweld_file = os.path.join(cwd,"inputs/eweld.in")
filein = open(eweld_file, "r" )
lines = filein.readlines()

textLine = lines[1]
length = 25.4*float(lines[1])
logfile.write("Plate length = " + str(length) +'\n')  

textLine = lines[3]
dataline = textLine.split( ',' )  
if(len(dataline)==1):
  thick = 25.4*float(lines[3])
  logfile.write("Thickness = " + str(thick) +'\n')  
elif(len(dataline)==2):
  (thk1,thk2)=map(float,dataline)
  thick1 = 25.4*thk1
  thick2 = 25.4*thk2  
  logfile.write("Thickness = " + str(thick1) + "," + str(thick2) +'\n')
else:
  logfile.write("***ERROR***, wrong data format in eweld.in" +'\n')

textLine = lines[5]
widthline = textLine.split( ',' )  
if(len(widthline)==1):
  width1 = 25.4*float(lines[5])/2.0
  width2 = 25.4*float(lines[5])/2.0  
  logfile.write("Width = " + str(width1) + "," + str(width2) +'\n')
elif(len(widthline)==2):
  (wth1,wth2)=map(float,widthline)
  width1 = 25.4*wth1
  width2 = 25.4*wth2  
  logfile.write("Width = " + str(width1) + "," + str(width2) +'\n')
elif(len(widthline)==3):
  (wth1,wth2,wth3)=map(float,widthline)
  width1 = 25.4*wth1
  width2 = 25.4*wth2 
  width3 = 25.4*wth3 
  logfile.write("Width = " + str(width1) + "," + str(width2) + "," + str (width3) +'\n')
else:
  logfile.write("***ERROR***, wrong data format in eweld.in" +'\n')

textLine = lines[7].strip()
matline = textLine.split( ',' )  
if(len(matline)==1):
  myMaterial=lines[7]
  logfile.write("Materil = " + myMaterial +'\n')
elif(len(matline)==2):
  (myMaterial1,myMaterial2)=(matline[0],matline[1])
  logfile.write("Materil = " + myMaterial1 + "," + myMaterial2 +'\n')
else:
  logfile.write("***ERROR***, wrong data format in eweld.in" +'\n')

FillerMaterial=lines[9]
FillerMaterial = FillerMaterial.strip()
logfile.write("FillerMateril = " + FillerMaterial +'\n')

weld_type = lines[11].strip()
logfile.write("Weld process = " + weld_type +'\n')

reinforcement = float(lines[13].strip())
reinf = 25.4*reinforcement
logfile.write("Weld reinforcement = " + str(reinf) +'\n')

penetration = float(lines[15].strip())
pene = 25.4*penetration
logfile.write("Weld penetration = " + str(pene) +'\n')

rootgap = float(lines[17].strip())
hgsize = 25.4*rootgap/2.0
TeeGap = 25.4*rootgap
logfile.write("Weld root gap = " + str(hgsize) +'\n')

xmesh = float(lines[21].strip())
wmesh = 25.4*xmesh
logfile.write("Weld mesh size = " + str(wmesh) +'\n')

layer_text = lines[23].strip()
logfile.write("Weld layer total = " + layer_text +'\n')
layer = int(layer_text)

nweld=0
for k in range(layer):
    textLine = lines[25+k].strip()
    data = textLine.split( ',' )  
    (nlayer,npass)=(data[0],data[1])
    nweld = nweld + int(npass)
    logfile.write("Layer, Pass = " + str(nlayer) + "," + str(npass) +'\n')
#end for
logfile.write("Number of weld passes = " + str(nweld) +'\n')

# Joint type (plate or pipe joint)
joint_type=lines[26+layer]
joint_type=joint_type.strip()
logfile.write("joint_type = " + joint_type +'\n')
startline=26+layer

TeeType=lines[26+layer]
TeeType = TeeType.strip()
logfile.write("TeeType = " + TeeType +'\n')

jshape=1
pipe_D=0.0

# Pipe Outer Diameter
if (joint_type=='Pipe') or (joint_type=='T-Pipe') or (joint_type=='User-Pipe'):
    joint_type='Pipe welding'
    jshape=2
    pipe_D=25.4*float(lines[27+layer])
    length=pi*pipe_D
    startline=27+layer
#endif

myGrooveType=lines[startline+2]
logfile.write("myGrooveType = " + myGrooveType +'\n')

if myGrooveType.find('V-groove') != -1 :
    root_high = float(lines[startline+3])*25.4
    g_angle = float(lines[startline+4])
    logfile.write("Land, angle = " + str(root_high) + "," + str(g_angle) +'\n')
    
    p1angle = g_angle/2.0
    p2angle = g_angle/2.0
    p1x=(thick-root_high)*tan(p1angle/180*pi)
    p2x=(thick-root_high)*tan(p2angle/180*pi)
    pax=(p1x+p2x)/2.0
    pay=0
    grid=1
elif myGrooveType.find('Compound-bevel') != -1 :  
    root_high = float(lines[startline+3])*25.4
    hot_width = float(lines[startline+4])*25.4/2.0
    alpha = float(lines[startline+5])
    beta = float(lines[startline+6])

    hot_high=hot_width*tan(alpha*pi/180)
    p1x=(thick-root_high-hot_high)*tan(beta/180*pi)+hot_width
    p2x=p1x
    pax=(p1x+p2x)/2.0
    pay=0
    grid=2
elif myGrooveType.find('U-groove') != -1 :
    root_high = float(lines[startline+3])*25.4
    hot_width = float(lines[startline+4])*25.4
    radius=float(lines[startline+5])*25.4
    beta = float(lines[startline+6])

    pay=0 
    grid=3   
    
    xuc = hgsize+hot_width
    yuc = root_high+radius    
    x6 = hgsize
    y6 = root_high    
    x5 = hot_width+hgsize
    y5 = root_high    
    x4 = radius*cos(beta*pi/180)+hot_width+hgsize
    y4 = radius-radius*sin(beta*pi/180)+root_high    
    x3 = (thick-y4)*tan(beta*pi/180)+x4
    y3 = thick
    
    p1x=x3-hgsize
    p2x=p1x
    pax=(p1x+p2x)/2.0
elif myGrooveType.find('J-groove') != -1 :
    root_high = float(lines[startline+3])*25.4
    hot_width = float(lines[startline+4])*25.4
    radius=float(lines[startline+5])*25.4
    beta = float(lines[startline+6])

    pay=0     
    grid=4   

    xuc = hgsize+hot_width
    yuc = root_high+radius    
    x6 = hgsize
    y6 = root_high    
    x5 = hot_width+hgsize
    y5 = root_high    
    x4 = radius*cos(beta*pi/180)+hot_width+hgsize
    y4 = radius-radius*sin(beta*pi/180)+root_high    
    x3 = (thick-y4)*tan(beta*pi/180)+x4
    y3 = thick
    p2x=x3-hgsize
    p1x=0
#    pax=(p1x+p2x)/2.0
    pax=p2x
elif myGrooveType.find('Bevel-groove') != -1 :
    g_angle = float(lines[startline+3])
    root_high = float(lines[startline+4])*25.4
    
    if(root_high > thick):   
       logfile.write("thick,root_high" + str(thick) + str(root_high))
       logfile.write("***ERROR***, TC lower than the bottom")
       sys.exit()   
    p1angle = 0.0
    p2angle = g_angle 
    p1x=thick*tan(p1angle/180*pi)
    p2x=(thick-root_high)*tan(p2angle/180*pi)
    pax=p2x
    pay=0 
    grid=5
elif myGrooveType.find('Bevel-left') != -1 :
    g_angle = float(lines[startline+3])

    root_high = 0.0
    p1angle = g_angle
    p2angle = 0.0
    p1x=thick*tan(p1angle/180*pi)
    p2x=thick*tan(p2angle/180*pi)
    pax=p1x
    pay=0    
    grid=5
elif myGrooveType.find('Bead-on-plate') != -1 :
    root_high = 0.0
    hgsize=0.0
    bwidth= 0.0
    bthick = 0
    bgap = 0
    p2x=0
    p1x=0
    pax=(p1x+p2x)/2.0
    pay=0
    grid=6
elif myGrooveType.find('Butt-joint') != -1 :
    root_high = 0.0
    g_a1 = float(lines[startline+3])*25.4
    g_a2 = float(lines[startline+4])*25.4
    g_a3 = float(lines[startline+5])*25.4
    g_a4 = float(lines[startline+6])*25.4
    g_a5 = float(lines[startline+7])*25.4
    g_a6 = float(lines[startline+8])*25.4
    g_a7 = float(lines[startline+9])*25.4
    g_a8 = float(lines[startline+10])*25.4
    g_b1 = float(lines[startline+11])*25.4
    g_b2 = float(lines[startline+12])*25.4
    g_b3 = float(lines[startline+13])*25.4
    g_b4 = float(lines[startline+14])*25.4
    g_b5 = float(lines[startline+15])*25.4
    g_b6 = float(lines[startline+16])*25.4
    g_b7 = float(lines[startline+17])*25.4
    g_b8 = float(lines[startline+18])*25.4  
    pay=0
    grid=7
    g_a=g_a1
elif myGrooveType.find('T-Bevel') != -1 :
    right_angle = float(lines[startline+3])
    right_cut = 25.4*float(lines[startline+4])
    left_angle = float(lines[startline+5])
    left_cut = 25.4*float(lines[startline+6])

    grid=8
       
    if(right_cut < thick2/2.0):
       tee_x1=(thick2/2.0 - right_cut)
       tee_y2=TeeGap+right_cut*tan(right_angle/180*pi)
    elif(right_cut == thick2/2.0):
       tee_x1=0.0
       tee_y2=TeeGap+right_cut*tan(right_angle/180*pi)      
    elif(right_cut > thick2/2.0) and (right_cut <= thick2):
       tee_x1= -(right_cut-thick2/2.0)
       tee_y2= TeeGap+right_cut*tan(right_angle/180*pi)
    elif(right_cut > thick2):
       logfile.write("***ERROR***, right_cut too big" +'\n')
    #endif
    
    if(tee_y2 > width3) : tee_y2 = width3*1
           
    if(left_cut < thick2/2.0):
       tee_x6=-(thick2/2.0 - left_cut)
       tee_y5=TeeGap+left_cut*tan(left_angle/180*pi)
    elif(left_cut == thick2/2.0):
       tee_x6=0.0
       tee_y5=TeeGap+left_cut*tan(left_angle/180*pi)      
    elif(left_cut > thick2/2.0) and (left_cut <= thick2):
       tee_x6= (left_cut-thick2/2.0)
       tee_y5= TeeGap+left_cut*tan(left_angle/180*pi)
    elif(left_cut > thick2):
       logfile.write("***ERROR***, left_cut too big" +'\n')
    #endif 
       
    if(tee_y5 > width3) : tee_y5 = width3*1
        
    pax=thick2/2.0
    pay=max(tee_y5,tee_y2)     
elif myGrooveType.find('T-J') != -1 :
    g_angle = float(lines[startline+3])
    root_high = float(lines[startline+4])*25.4
    
    p1angle = 0.0
    p2angle = g_angle 
    p1x=thick*tan(p1angle/180*pi)
    p2x=(thick-root_high)*tan(p2angle/180*pi)
    pax=p2x
    pay=0
    grid=9
#endif
logfile.write("eweld.inp has been successfully read " +'\n' +'\n')
filein.close()
#-------------------------------------------------------------
#--------------- weld_parameters.dat -------------------------
#-------------------------------------------------------------
wp_P=[[],]*nweld
wp_TS = [[],]*nweld
wp_eff=[[],]*nweld

logfile.write('Read Weld Parameters ' +'\n')

wp_file = os.path.join(cwd,"inputs/eweld_weld_parameters.in")

wp_data = open(wp_file, 'r')
textLine = wp_data.readline()
textLine = wp_data.readline()
for k in range(nweld):
    kk=str(k+1) 
    textLine = wp_data.readline()
    dataline = textLine.split( ',' )  
    (np,power,trav)=map(float,dataline)    
    so=('  ' + str(np) + ',' + str(power) + ',' + str(trav))
    logfile.write(so +'\n')
    vol=20.0
    wp_eff[k]=arc_efficiency(weld_type,vol)
    wp_P[k]=power
    wp_TS[k]=25.4/60*trav
    so=('  ' + str(np) + ',' + str(wp_P[k]) + ',' + str(wp_TS[k]) + ',' + str(wp_eff[k]))    
    logfile.write(so +'\n')
#end for
wp_data.close()
logfile.write(' ' +'\n')
##-----------------------------------------------

def area2p(start, stop):
    area2p=start[0]*stop[1]-start[1]*stop[0]
    return area2p 

def dist2p(start, stop):
    a=stop[0]-start[0]
    b=stop[1]-start[1]
    dist2p=sqrt(a*a+b*b)
    return dist2p

def dist3D(st, sp):
    a=sp[0]-st[0]
    b=sp[1]-st[1]
    c=sp[2]-st[2]
    dist3D=sqrt(a*a+b*b+c*c)
    return dist3D
    
def tra_area(aedge, bedge, cedge):
    a=aedge
    b=bedge
    c=cedge
    p=(a+b+c)/2.0
    area=sqrt(p*(p-a)*(p-b)*(p-c))
    return area

def area_cal(k,centt,dxx,dyy):
    kc=close_pt(k,centt,dxx,dyy)
#    logfile.write('kc' + str(kc) + '\n')
    area=0.0
    for i in range(numpt[k]-2):
        ptrs = [[],]*numpt[k]
    	ptrs[i]=[pt[k][i][0]+dxx, pt[k][i][1]+dyy]
    	ptrs[i+1]=[pt[k][i+1][0]+dxx, pt[k][i+1][1]+dyy]   	
    	if(i==kc): 
#    	   logfile.write('ptrs ii = '+str(centt) + '\n')
#           logfile.write('ptrs ii+1 = '+str(ptrs[i+1]) + '\n') 
    	   area=area+area2p(centt,ptrs[i+1])   	   
    	elif((i+1)==kc): 
#    	   logfile.write('ptrs ii = '+str(ptrs[i]) + '\n')
#           logfile.write('ptrs ii+1 = '+str(centt) + '\n')
    	   area=area+area2p(ptrs[i],centt)    	
    	else:
#    	   logfile.write('ptrs ii = '+str(ptrs[i]) + '\n')
#           logfile.write('ptrs ii+1 = '+str(ptrs[i+1]) + '\n')
           area=area+area2p(ptrs[i],ptrs[i+1])    	        
           
#        logfile.write('area'+str(area) + '\n')

    ptrs[0]=[pt[k][0][0]+dxx, pt[k][0][1]+dyy]
    ptrs[numpt[k]-2]=[pt[k][numpt[k]-2][0]+dxx, pt[k][numpt[k]-2][1]+dyy]      	
    if(kc==0): 
#       logfile.write('ptrs i = '+str(ptrs[numpt[k]-2]) + '\n')
#       logfile.write('ptrs i+1 = '+str(centt) + '\n')
       area=area+area2p(ptrs[numpt[k]-2],centt)
    elif(kc==(numpt[k]-2) ):
#       logfile.write('ptrs i = '+str(centt) + '\n')
#       logfile.write('ptrs i+1 = '+str(ptrs[0]) + '\n')    
       area=area+area2p(centt,ptrs[0])    	
    else:
#       logfile.write('ptrs i = '+str(ptrs[numpt[k]-2]) + '\n')
#       logfile.write('ptrs i+1 = '+str(ptrs[0]) + '\n') 
       area=area+area2p(ptrs[numpt[k]-2],ptrs[0]) 
           
    tarea=area/2.0
    return abs(tarea) 
#-------Part Area Calculation---------------------
def parea_cal(nppt,ppt,centt):
    area=0.0
    for i in range(nppt-1): 	 
    	   a1=area2p(centt,ppt[i])   	   
    	   d1=dist2p(centt,ppt[i])   	   
    	   a2=area2p(ppt[i],ppt[i+1])
    	   d2=dist2p(ppt[i],ppt[i+1])   	   
    	   a3=area2p(ppt[i+1],centt) 
    	   d3=dist2p(ppt[i+1],centt)    	      	   
    	   if(d1==0) or (d2==0) or (d3==0): 
    	      a1=0
    	      a2=0
    	      a3=0
           area=area+abs(a1+a2+a3)    	                             
    tarea=area/2.0
    return abs(tarea) 
    
def parea_cal0(nppt,ppt,centt):
    kc=close_ppt(nppt,ppt,centt)
    logfile.write('kc = '+ str(kc) +'\n')
    area=0.0
    for i in range(nppt-2): 	
    	if(i==kc): 
    	   area=area+area2p(centt,ppt[i+1])   	   
    	elif((i+1)==kc): 
    	   area=area+area2p(ppt[i],centt)    	
    	else:
           area=area+area2p(ppt[i],ppt[i+1])    	                  
     	
    if(kc==0): 
       area=area+area2p(ppt[nppt-2],centt)
    elif(kc==(nppt-2) ):   
       area=area+area2p(centt,ppt[0])    	
    else:
       area=area+area2p(ppt[nppt-2],ppt[0]) 
           
    tarea=area/2.0
    return abs(tarea) 
    
def close_ppt0(nppt,ppt,centt):
    dmin=1.0E10
    for i in range(nppt):  
    	ptt=[ppt[i][0],ppt[i][1]]
        dist=dist2p(ptt,centt)       
        if(dist < dmin): 
           dmin=dist
           kc=i
    return kc 
#-------------------------------------
def close_pt(k,centt,dxx,dyy):
    dmin=1.0E10
    for i in range(numpt[k]):  
    	ptt=[pt[k][i][0]+dxx,pt[k][i][1]+dyy]
#        logfile.write(' ptt = '+ str(ptt) + '\n')    	
#        logfile.write('centt = ' + str(centt) + '\n') 
        dist=dist2p(ptt,centt)       
#        logfile.write('dist =' + str(dist) + '\n')
        if(dist < dmin): 
           dmin=dist
           kc=i
#    logfile.write('dmin = '+ str(dmin) +'\n')
#    logfile.write('kc = '+ str(kc) +'\n')
    return kc 

##----- Weld center subroutine---------------------------------------
def cross2p(start, stop):
    cross2p=start[0]*stop[1]-start[1]*stop[0]
    return cross2p 

def add2x(start, stop):
    add2x=start[0]+stop[0]
    return add2x 

def add2y(start, stop):
    add2y=start[1]+stop[1]
    return add2y   
    
def centroid_cal(k,weld_area):
    cent_x=0.0
    cent_y=0.0
    for i in range(numpt[k]-1):
        ptrs = [[],]*numpt[k]
    	ptrs[i]=[pt[k][i][0], pt[k][i][1]]
    	ptrs[i+1]=[pt[k][i+1][0], pt[k][i+1][1]]   	
    	cent_x=cent_x+add2x(ptrs[i],ptrs[i+1])*cross2p(ptrs[i],ptrs[i+1])   	   
    	cent_y=cent_y+add2y(ptrs[i],ptrs[i+1])*cross2p(ptrs[i],ptrs[i+1]) 
   	
    centx=cent_x/(6.0*weld_area)
    centy=cent_y/(6.0*weld_area)
#data input anti clock wise
    wcent=[centx,centy,0.0]   
    return wcent 
#-------------------------------------------------------------
#--------------- Read pass_coordinates.out -------------------
#-------------------------------------------------------------

bead_file = os.path.join(cwd, args.weld_pass_coordinates_file)
bead_data = open(bead_file, "r" )

numpt=[[],]*nweld
pt = [[[],]*1000]*nweld

textLine = bead_data.readline()
textLine = bead_data.readline()
print(bead_file)
print(textLine)
layer = int(textLine)
logfile.write("Number of layer = " + str(layer) +'\n')
    
textLine = bead_data.readline()
lyps=[[],]*layer
for k in range(layer):
    textLine = bead_data.readline()
    data = textLine.split( ',' )  
    (nlayer,lyps[k])=map(int,data)
    logfile.write("Layer, Pass = " + str(nlayer) + "," + str(lyps[k]) +'\n')
#end for

xmin_weld=1.0E10
xmax_weld=-1.0E10
ymin_weld=1.0E10
ymax_weld=-1.0E10

nw=-1
for k in range(layer):
    for j in range(lyps[k]):    
        textLine = bead_data.readline()
        textLine = bead_data.readline()
        dataline = textLine.split(",")
    	nw=nw+1  
        (nlayer,npass,numpt[nw])=map(int,dataline)
        print nlayer,npass,numpt[nw]       
        logfile.write("Layer,Pass,Npt = " + str(nlayer) + ',' + str(npass)+ ',' + str(numpt[nw]) +'\n')
        textLine = bead_data.readline()    	
    	pt[nw] = [[],]*(numpt[nw]+1)
    	for i in range(numpt[nw]):    
            textLine = bead_data.readline()
	    dataline = textLine.split(",")
	    (nt,xt,yt)=map(float,dataline)
	    pt[nw][i]= [xt,yt]	    
            so=(str(i) + ',' + str(pt[nw][i][0]) + ',' + str(pt[nw][i][1]))
            logfile.write(so +'\n')
            if(pt[nw][i][0] > xmax_weld): xmax_weld=pt[nw][i][0]	
            if(pt[nw][i][0] < xmin_weld): xmin_weld=pt[nw][i][0]
            if(pt[nw][i][1] > ymax_weld): ymax_weld=pt[nw][i][1]	
            if(pt[nw][i][1] < ymin_weld): ymin_weld=pt[nw][i][1]
	#endfor
        pt[nw][numpt[nw]]=pt[nw][0]       
        so=(str(numpt[nw])+ ',' + str(pt[nw][numpt[nw]][0]) + ',' + str(pt[nw][numpt[nw]][1]))        
        logfile.write(so +'\n')
        numpt[nw]=numpt[nw]+1        
    #endfor
#end for
bead_data.close()
#------Area Calculation-----------------------------------------------------
weldarea=[[],]*nweld
wp_dim_w=[[],]*nweld
wp_dim_h=[[],]*nweld
cent=[ [[],]*2 ]*nweld
weldcent=[ [[],]*3 ]*nweld

for k in range(nweld):
    xmax=-1.0E10
    ymax=-1.0E10
    xmin=1.0E10
    ymin=1.0E10
    center_point = [0.0, 0.0]
    for i in range(numpt[k]-1):
        center_point[0]=center_point[0]+pt[k][i][0]
        center_point[1]=center_point[1]+pt[k][i][1]
        if(pt[k][i][0] > xmax): xmax=pt[k][i][0]
        if(pt[k][i][0] < xmin): xmin=pt[k][i][0]
        if(pt[k][i][1] > ymax): ymax=pt[k][i][1]	
        if(pt[k][i][1] < ymin): ymin=pt[k][i][1] 
    nt=numpt[k]-1
    center_point[0]=center_point[0]/nt
    center_point[1]=center_point[1]/nt
    cent[k]= center_point
    so=('center'+','+str(nt)+','+str(cent[k]))
    logfile.write(so +'\n')
    so=( 'xmin,xmax'+','+str(xmin)+','+str(xmax) )
    logfile.write(so +'\n')
    so=( 'ymin,ymax'+','+str(ymin)+','+str(ymax) )
    logfile.write(so +'\n')

    wp_dim_w[k] = (xmax-xmin)/2.0
    wp_dim_h[k] = (ymax-ymin)/2.0

    dxx=0.0
    dyy=0.0
    centt=pt[k][1] 
    weldarea[k]=area_cal(k,centt,dxx,dyy)
    so=('weld pass area = ' + str(weldarea[k]) )
    logfile.write(so +'\n')

#   calculate weld center and verify
    centt=centroid_cal(k,weldarea[k])
    verify=area_cal(k,centt,dxx,dyy)
    so=('Verified pass area = ' + str(verify) )
    logfile.write(so +'\n')    
    if (verify < weldarea[k]):
        weldcent[k]=centt 
    else:
        weldcent[k]=[-centt[0],-centt[1], 0.0] 
   
    so=('weld centroid = ' + str(weldcent[k]) )
    logfile.write(so +'\n')

#end for
#-------------------------------------------------------------
#---------------  output dflux subroutine  -------------------
#------------     model_dflux.for    -----------------
#-------------------------------------------------------------
def dflux_output(jshape,pipe_D,nweld,cent,wp_dim_w,wp_dim_h,wp_P,wp_TS,wp_eff,length):
    dfluxfile = data_IO.open_file(os.path.join(out_dir,"model_dflux.for"), "w" )
    dfluxfile.write('! Abaqus interface ' + '\n')
    dfluxfile.write('!      subroutine dflux(flux,sol,kstep,kinc,time,noel,npt,coords, ' + '\n')
    dfluxfile.write('!     & jltyp,temp,press,sname) ' + '\n')     
    dfluxfile.write('            ' + '\n')    
    dfluxfile.write('! Calculix interface  ' + '\n')  
    dfluxfile.write('      subroutine dflux(flux,sol,kstep,kinc,time,noel,npt,coords, ' + '\n')
    dfluxfile.write('     &     jltyp,temp,press,loadtype,area,vold,co,lakonl,konl, ' + '\n')
    dfluxfile.write('     &     ipompc,nodempc,coefmpc,nmpc,ikmpc,ilmpc,iscale,mi, ' + '\n')
    dfluxfile.write('     &     sti,xstateini,xstate,nstate_,dtime) ' + '\n')   
    dfluxfile.write(' ' + '\n')
    dfluxfile.write('      implicit real*8(a-h,o-z)     ' + '\n')
    dfluxfile.write('      DIMENSION COORDS(3),FLUX(2),TIME(2) ' + '\n')
    dfluxfile.write('      character*80 sname      ' + '\n')
    dfluxfile.write('      character*8 lakonl    ' + '\n')
    dfluxfile.write('      character*20 loadtype ' + '\n')
    dfluxfile.write('   ' + '\n')
    dfluxfile.write('      pi=acos(-1.0) ' + '\n')
    dfluxfile.write('      k=(kstep+2)/3 ' + '\n')
    dfluxfile.write('             ' + '\n')
    dfluxfile.write('      call heat_line_input(k,nwps,jshape,rad,power,speed,eff, ' + '\n')
    dfluxfile.write('     &  thold,a,b,cf,cr,x0,y0,z0,x1,y1,z1) ' + '\n')
    dfluxfile.write('            ' + '\n')  
    dfluxfile.write('      timenet=time(1)-thold ' + '\n')
    dfluxfile.write('      if(jshape.eq.1) then ' + '\n')
    dfluxfile.write('          xarc=  x0 ' + '\n')
    dfluxfile.write('		yarc=  y0 ' + '\n')
    dfluxfile.write('		zarc= speed*timenet + z0 ' + '\n')
    dfluxfile.write('          xcod=coords(1)-xarc	 ' + '\n')
    dfluxfile.write('		ycod=coords(2)-yarc ' + '\n')	
    dfluxfile.write('		zcod=coords(3)-zarc ' + '\n')      
    dfluxfile.write('      else if(jshape.eq.2) then ' + '\n')
    dfluxfile.write('		omega=speed*time(1)/rad	 ' + '\n')
    dfluxfile.write('		ythe=cos(omega)*rad  ' + '\n')
    dfluxfile.write('		zthe=sin(omega)*rad  ' + '\n')
    dfluxfile.write('		xthe=x0	 ' + '\n')
    dfluxfile.write(' 		xcod=coords(1)-xthe ' + '\n')	
    dfluxfile.write('		ycod=coords(2)-ythe ' + '\n')	 
    dfluxfile.write('		zcod=coords(3)-zthe ' + '\n')	
    dfluxfile.write('      endif ' + '\n')
    dfluxfile.write(' ' + '\n')
    dfluxfile.write('      call dellipse(power,eff,a,b,cf,cr,xcod,ycod,zcod,qflux) ' + '\n')

    dfluxfile.write(' \n'
                    '!     set flux to zero during cooling or depositing: \n'
                    '      if (mod(kstep,3).eq.0) then \n'
                    '         qflux = 0 \n'
                    '      endif \n'
                    '      if (mod(kstep+2,3).eq.0) then \n'
                    '         qflux = 0 \n'
                    '      endif \n'
                    '\n')

    dfluxfile.write('      flux(1)=qflux     ' + '\n')
    dfluxfile.write('                 ' + '\n')
    dfluxfile.write('      RETURN ' + '\n')
    dfluxfile.write('      END ' + '\n')
    dfluxfile.write(' ' + '\n')
    dfluxfile.write('	subroutine heat_line_input(k,nwps,jshape,rad,power,speed,eff, ' + '\n')
    dfluxfile.write('     &  thold,a,b,cf,cr,x0,y0,z0,x1,y1,z1) ' + '\n')
    dfluxfile.write(' ' + '\n')
    dfluxfile.write('      implicit real*8(a-h,o-z) ' + '\n')
    dfluxfile.write(' ' + '\n')
    dfluxfile.write('      if(k.eq.1) then ' + '\n')
    for k in range(nweld):
        if(k > 0): dfluxfile.write('      elseif(k.eq.'+ str(k+1) + ' )then ' + '\n')
        dfluxfile.write('         nwps=1 ' + '\n')
        dfluxfile.write('         jshape=' + str(jshape) + '\n')
        dfluxfile.write('         rad=' + str(pipe_D/2.0-cent[k][1]) + '\n')
        dfluxfile.write('         power=' + str(wp_P[k]) + '\n')
        dfluxfile.write('          speed=' + str(-1.0*wp_TS[k])  + '\n')
        dfluxfile.write('           eff=' + str(wp_eff[k])  + '\n')
        dfluxfile.write('            thold=0.25 ' + '\n')
        dfluxfile.write('         a=' + str(wp_dim_w[k]) + '\n')
        dfluxfile.write('          b=' + str(wp_dim_h[k]) +  '\n')
        dfluxfile.write('           cf=' + str(wp_dim_w[k]) + '\n')
        dfluxfile.write('            cr=' + str(2.0*wp_dim_w[k]) + '\n')
        dfluxfile.write('          x0=' + str(cent[k][0]) + '\n')
        dfluxfile.write('           y0=' + str(cent[k][1]) + '\n')
        dfluxfile.write('            z0=0.0 ' + '\n')
        dfluxfile.write('          x1=' + str(cent[k][0]) + '\n')
        dfluxfile.write('           y1=' + str(cent[k][0]) + '\n')
        dfluxfile.write('            z1=' + str(-length) + '\n')                     
    #endfor 
    dfluxfile.write('      endif  ' + '\n')
    dfluxfile.write('       ' + '\n')
    dfluxfile.write('      return     ' + '\n')  
    dfluxfile.write('      end   ' + '\n')    
    dfluxfile.write('   ' + '\n') 
    dfluxfile.write('	subroutine dellipse(powerk,effk,ak,bk,cfk,crk, ' + '\n')
    dfluxfile.write('     &	xcod,ycod,zcod,qflux) ' + '\n')
    dfluxfile.write(' ' + '\n')
    dfluxfile.write('      implicit real*8(a-h,o-z) ' + '\n')
    dfluxfile.write('  ' + '\n')
    dfluxfile.write('	pi=acos(-1.0) ' + '\n')
    dfluxfile.write('	 ' + '\n')
    dfluxfile.write('	cf=cfk ' + '\n')
    dfluxfile.write('	cr=crk ' + '\n')
    dfluxfile.write('	if(zcod.ge.0.0) then ' + '\n')
    dfluxfile.write('		ff=2*cf/(cf+cr) ' + '\n')
    dfluxfile.write('		fheat=ff ' + '\n')
    dfluxfile.write('		cheat=cf ' + '\n')
    dfluxfile.write('	else if(zcod.lt.0.0) then ' + '\n')
    dfluxfile.write('		fb=2*cr/(cf+cr) ' + '\n')
    dfluxfile.write('		fheat=fb ' + '\n')
    dfluxfile.write('		cheat=cr ' + '\n')
    dfluxfile.write('	else ' + '\n')
    dfluxfile.write('		stop "*** error in fheat calculation ***" ' + '\n')
    dfluxfile.write('	end if ' + '\n')
    dfluxfile.write(' ' + '\n')
    dfluxfile.write('      qtop=6.0*sqrt(3.0)*effk*powerk*fheat ' + '\n')
    dfluxfile.write('	qbot=pi*ak*bk*cheat*sqrt(pi)  ' + '\n')
    dfluxfile.write('	qmax=(qtop/qbot)  ' + '\n')
    dfluxfile.write(' ' + '\n')
    dfluxfile.write('      gcutk=ak/10  ' + '\n')
    dfluxfile.write('     	if(abs(xcod).lt.gcutk) then ' + '\n')
    dfluxfile.write('		xcod=gcutk ' + '\n')
    dfluxfile.write('	end if ' + '\n')
    dfluxfile.write('	if(abs(ycod).lt.gcutk) then ' + '\n')
    dfluxfile.write('		ycod=gcutk ' + '\n')
    dfluxfile.write('	endif ' + '\n')
    dfluxfile.write('	if(abs(zcod).lt.gcutk) then ' + '\n')
    dfluxfile.write('		zcod=gcutk ' + '\n')
    dfluxfile.write('	endif         ' + '\n')
    dfluxfile.write(' ' + '\n')
    dfluxfile.write('      rx2=(xcod*xcod)/(ak**2)	 ' + '\n')
    dfluxfile.write('	ry2=(ycod*ycod)/(bk**2) ' + '\n')
    dfluxfile.write('	rz2=(zcod*zcod)/(cheat**2) ' + '\n')
    dfluxfile.write(' ' + '\n')
    dfluxfile.write('	qflux=qmax*exp(-3.0*(rx2+ry2+rz2)) ' + '\n')
    dfluxfile.write('           ' + '\n')
    dfluxfile.write('!      write(7,*) "zcod",zcod ' + '\n')
    dfluxfile.write('!      write(7,*) "qtop,bbot,qmax=",qtop,qbot,qmax ' + '\n')
    dfluxfile.write('!      write(7,*) "abc f ",ak,bk,cheat,fheat ' + '\n')
    dfluxfile.write('!      write(7,*) "q =",qqflux ' + '\n')
    dfluxfile.write(' ' + '\n')
    dfluxfile.write('	return ' + '\n')
    dfluxfile.write('	end ' + '\n')
    dfluxfile.close()
#enddef
#-------------------------------------------------------------
#-------------------- output step files ----------------------
#------------------------- model_step.inp --------------------------
#-------------------------------------------------------------
def step_output(jshape, pipe_D, nweld, wp_TS, length, separate_step_files=False):


    ctime = 60.0
    cfinal = 15000.0
    for k in range(nweld):
        if(pipe_D > 0):
            length = 2.0*pi*(pipe_D/2.0-cent[k][1])
        tweld=length/wp_TS[k]
        tini=tweld/1000.0
        tmax=lwt/wp_TS[k]

        if separate_step_files:
            step_file_name = "model_step{:d}.inp".format(k+1)
            stepfile = open(os.path.join(out_dir, step_file_name), "w")
        else:
            if k==0:
                step_file_name = "model_step1.inp"
                stepfile = open(os.path.join(out_dir, step_file_name), "w")

        if separate_step_files & k>0:
            stepfile.write('*restart, read \n')

        stepfile.write('**********STEP ' + str(k*3+1) + ' Depositing********' + '\n')

        if separate_step_files:
            stepfile.write('*restart, write \n')

        stepfile.write('*STEP,INC=5000 '  + '\n')
        stepfile.write('*UNCOUPLED TEMPERATURE-DISPLACEMENT,DELTMX=50000.0'  + '\n')
        stepfile.write(' 0.1, 0.1, 1.0E-9, 0.1' + '\n')

        if(k==0):

            stepfile.write('** Increase the maximum number of cutbacks from 5 to 12. \n')
            stepfile.write('** The other settings are Calculix\'s default values. \n')
            stepfile.write('*CONTROLS, PARAMETERS = TIME INCREMENTATION \n')
            stepfile.write('4, 8, 9, 16, 10, 4, 0, 12 \n')
            stepfile.write('0.25 \n')

            stepfile.write('*MODEL CHANGE, TYPE=ELEMENT,REMOVE' + '\n')
            for j in range(nweld-1):
                jw=j+2
                stepfile.write(' WP' + str(jw) + "_extruded," + '\n')

            stepfile.write('*FILM,OP=NEW'  + '\n')
            stepfile.write('*INCLUDE,INPUT=model_film.in' + '\n')
            stepfile.write('*NODE FILE' + '\n')
            stepfile.write(' NT,U' + '\n')
            stepfile.write('*EL FILE' + '\n')
            stepfile.write(' S,HFL,PE' + '\n')
        else:
            stepfile.write('*MODEL CHANGE, TYPE=ELEMENT,ADD' + '\n')
            stepfile.write(' WP' + str(k+1) + '_extruded,' + '\n')

        stepfile.write('*END STEP' + '\n')

        stepfile.write('************STEP  ' + str(k*3+2) + ' Heating**********' + '\n')
        stepfile.write('*STEP,INC=5000'  + '\n')
        stepfile.write('*UNCOUPLED TEMPERATURE-DISPLACEMENT,DELTMX=50000.0'  + '\n')
        stepfile.write(" " + str(tini) + "," + str(tweld) + "," + '0.1E-09, ' + str(tmax) + '\n')
        stepfile.write('*DFLUX,OP=NEW'  + '\n')
        stepfile.write(' WP' + str(k+1) + '_extruded, BFNU' + '\n')
        stepfile.write('*END STEP' + '\n')

        stepfile.write('************STEP ' + str(k*3+3) + ' Cooling*********'  + '\n')
        stepfile.write('*STEP,INC=5000'   + '\n')
        stepfile.write('*UNCOUPLED TEMPERATURE-DISPLACEMENT,DELTMX=50000.0' + '\n')
        if( (k+1) == nweld):
            stepfile.write(' 0.1, ' + str(cfinal) + ', 1.0E-10,' + str(cfinal/3.0) + '\n')
        else:
            stepfile.write(' 0.1, ' + str(ctime) + ', 1.0E-10,' + str(ctime/3.0) + '\n')
        stepfile.write('*DFLUX,OP=NEW'  + '\n')
        stepfile.write('*END STEP' + '\n')

        if separate_step_files:
            stepfile.close()

    if not separate_step_files:
        stepfile.close()


dflux_Creat = dflux_output(jshape,pipe_D,nweld,cent,wp_dim_w,wp_dim_h,wp_P,wp_TS,wp_eff,length)
step_Creat = step_output(jshape,pipe_D,nweld,wp_TS,length, write_separate_step_files)
#--------------------------------------------------------
if (TeeType.find('T-Plate') != -1) or (TeeType.find('T-Pipe') != -1):
   if min(width1,width2) > 25.0:
      haz=20.0
   else:
      haz=min(width1,width2) 
   ymax_part=TeeGap+width3
   ymin_part=-thick1
   xmin_part=min(-width1,-thick2/2.0)
   xmax_part=max( width2, thick2/2.0)
else:
   if min(width1,width2) > 25.0:
      haz=20.0
   else:
      haz=min(width1,width2)      
   ymax_part=thick
   ymin_part=0
   xmin_part=-width1-hgsize
   xmax_part= width2+hgsize

if myGrooveType.find('Bead-on-plate') != -1 :
   p1x=abs(xmin_weld)
   p2x=abs(xmax_weld)
   pax=max(p1x,p2x)
   print "pax = ", pax
#
#-------------- Cooling Surface ---------
# 
cool_st = [[[],]*3]*100
cool_sp = [[[],]*3]*100

cool_file = os.path.join(cwd, "inputs/cool_surface.in")

if(os.path.isfile(cool_file)==True):
   logfile.write('Cooling Surface' +'\n') 
   cool_data = open(cool_file, 'r')
   
   textLine = cool_data.readline()
   ncool=int(textLine)
   for iii in range(ncool):
       textLine = cool_data.readline()
       dataline = textLine.split( ',' )     
       (xt,yt,ct)=map(float,dataline)    
       cool_st[iii]=[xt*25.4,yt*25.4,ct]
       
       textLine = cool_data.readline()
       dataline = textLine.split( ',' )     
       (xt,yt,ct)=map(float,dataline)      
       cool_sp[iii]=[xt*25.4,yt*25.4,ct]       
       
       so=(str(iii)+','+str(cool_st[iii]))
       logfile.write(so +'\n')       
       so=(str(iii)+','+str(cool_sp[iii]))       
       logfile.write(so +'\n')
   #end for  
   cool_data.close()

   for iii in range(ncool):    
       if(cool_st[iii][1] < ymin_part):   
       	  logfile.write("***ERROR***, cool start lower than the bottom")
    	  cool_st[iii][1] = ymin_part
       if(cool_st[iii][1] > ymax_part):   
    	  logfile.write("***ERROR***, cool start higher than the bottom")
    	  cool_st[iii][1] = ymax_part    
       if(cool_st[iii][0] < xmin_part):   
       	  logfile.write("***ERROR***, cool start is outside of left boundary")
    	  cool_st[iii][0] = xmin_part
       if(cool_st[iii][0] > xmax_part):   
    	  logfile.write("***ERROR***, cool start is outside of right boundary")
    	  cool_st[iii][0] = xmax_part  
       if(cool_sp[iii][1] < ymin_part):   
       	  logfile.write("***ERROR***, cool stop lower than the bottom")
    	  cool_sp[iii][1] = ymin_part
       if(cool_sp[iii][1] > ymax_part):   
    	  logfile.write("***ERROR***, cool stop higher than the bottom")
    	  cool_sp[iii][1] = ymax_part   
       if(cool_sp[iii][0] < xmin_part):   
       	  logfile.write("***ERROR***, cool stop is outside of left boundary")
    	  cool_sp[iii][0] = xmin_part
       if(cool_sp[iii][0] > xmax_part):   
    	  logfile.write("***ERROR***, cool stop is outside of right boundary")
    	  cool_sp[iii][0] = xmax_part 
   #end for	   
#
#--Temperature monitoring locations---------
# 

tc_file = os.path.join(cwd,"inputs/eweld_temperature_monitor.in" )

tc_pt = [[[],]*2]*100

if(os.path.isfile(tc_file)==True):
   #   logfile.write('Temperature monitoring points' +'\n')
   tc_data = open(tc_file, 'r')
   ntc = data_IO.read_int_from_file_line_offset(tc_data, "*Number of moniter points")

   for iii in range(ntc):
       points = data_IO.read_floats_from_file_line_offset(tc_data,"*X, Y, Z", ',', iii)
       xt = points[0]
       yt = points[1]
       tc_pt[iii] = [xt * 25.4, yt * 25.4]
       so = (str(iii) + ',' + str(tc_pt[iii]))
       logfile.write(so +'\n')
   tc_data.close()

# Deosn't work ...
# if(os.path.isfile(tc_file)==True):
#    logfile.write('Temperature monitoring points' +'\n')
#    tc_data = open(tc_file, 'r')
#    textLine = tc_data.readline()
#    textLine = tc_data.readline()
#    ntc=int(textLine)
#    textLine = tc_data.readline()
#    for iii in range(ntc):
#        textLine = tc_data.readline()
#        dataline = textLine.split( ',' )
#        print(dataline)
#        (xt,yt)=map(float,dataline)
#        tc_pt[iii]=[xt*25.4,yt*25.4]
#        so=(str(iii)+','+str(tc_pt[iii]))
#        logfile.write(so +'\n')
#    #end for
#    tc_data.close()

   for iii in range(ntc):    
       if(tc_pt[iii][1] < ymin_part):   
       	  logfile.write("***ERROR***, TC lower than the bottom")
    	  tc_pt[iii][1]=ymin_part
       if(tc_pt[iii][1] > ymax_part):   
    	  logfile.write("***ERROR***, TC higher than the bottom")
    	  tc_pt[iii][1] = ymax_part    
       if(tc_pt[iii][0] < xmin_part):   
       	  logfile.write("***ERROR***, TC is outside of left boundary")
    	  tc_pt[iii][0] = xmin_part
       if(tc_pt[iii][0] > xmax_part):   
    	  logfile.write("***ERROR***, TC is outside of right boundary")
    	  tc_pt[iii][0] = xmax_part  
   #end for	
#
#-----------------------------------------------------------
if(hgsize < 0.001):
   rd=1.0
else:
   rd=0.5
#endif

part_A1_pt = [[],]*100
part_A2_pt = [[],]*100
part_A3_pt = [[],]*100

part_W_pt = [[],]*100

part_B3_pt = [[],]*100
part_B2_pt = [[],]*100
part_B1_pt = [[],]*100

if myGrooveType.find('V-groove') != -1 :
    part_A1_pt[0]=[-hgsize-hazSize-hazExt, thick, 0.000]
    part_A1_pt[1]=[-width1-hgsize, thick, 0.000]
    part_A1_pt[2]=[-width1-hgsize, thick, -length]
    part_A1_pt[3]=[-hgsize-hazSize-hazExt, thick, -length]   
    part_A1_pt[4]=[-hgsize-hazSize-hazExt, thick, 0.000] 
    num_part_A1=5
    
    part_A2_pt[0]=[-hgsize-hazSize, 0.0]
    part_A2_pt[1]=[-hgsize-hazSize-hazExt, 0.0]
    part_A2_pt[2]=[-hgsize-hazSize-hazExt, thick]
    part_A2_pt[3]=[-hgsize-p1x-hazSize, thick]   
    part_A2_pt[4]=[-hgsize-hazSize, 0.0]
    num_part_A2=5
    centt=part_A2_pt[0]
    part_A2_area=parea_cal(num_part_A2,part_A2_pt,centt)    
    print "part_A2_area =", part_A2_area

    A2_EdgeMid=[-hgsize-hazSize-hazExt, thick/2.0, 0.0] 
 
    part_A3_pt[0]=[-hgsize-rd, 0.0]
    part_A3_pt[1]=[-hgsize-hazSize, 0.0]
    part_A3_pt[2]=[-hgsize-hazSize-p1x, thick]
    part_A3_pt[3]=[-hgsize-p1x-pene, thick]   
    part_A3_pt[4]=[-hgsize-rd, 0.0] 
    num_part_A3=5
    centt=part_A3_pt[0]
    part_A3_area=parea_cal(num_part_A3,part_A3_pt,centt)    
    print "part_A3_area =", part_A3_area

    part_W_pt[0]=[-hgsize-rd, 0.0] 
    part_W_pt[1]=[-hgsize-p1x-pene, thick]
    part_W_pt[2]=[-hgsize-p1x-hazSize-hazExt, thick]    
    part_W_pt[3]=[-hgsize-p1x-hazSize-hazExt, 3.0*thick]    
    part_W_pt[4]=[hgsize+p2x+hazSize+hazExt, 3.0*thick]    
    part_W_pt[5]=[hgsize+p2x+hazSize+hazExt, thick]    
    part_W_pt[6]=[hgsize+p2x+pene, thick]
    part_W_pt[7]=[hgsize+rd, 0.0]   
    part_W_pt[8]=[-hgsize-rd, 0.0]     
    num_part_W=9
    centt=part_W_pt[0]
    part_W_area=parea_cal(num_part_W,part_W_pt,centt)    
    print "part_W_area =", part_W_area

    part_B3_pt[0]=[hgsize+rd, 0.0]
    part_B3_pt[1]=[hazSize+hgsize, 0.0]
    part_B3_pt[2]=[hgsize+hazSize+p2x, thick]
    part_B3_pt[3]=[hgsize+p2x+pene, thick]   
    part_B3_pt[4]=[hgsize+rd, 0.0] 
    num_part_B3=5
    centt=part_B3_pt[0]
    part_B3_area=parea_cal(num_part_B3,part_B3_pt,centt)    
    print "part_B3_area =", part_B3_area

    part_B2_pt[0]=[hazSize+hgsize, 0.0]
    part_B2_pt[1]=[hazExt+hazSize+hgsize, 0.0]
    part_B2_pt[2]=[hazExt+hazSize+hgsize, thick]
    part_B2_pt[3]=[hazSize+hgsize+p2x, thick]   
    part_B2_pt[4]=[hazSize+hgsize, 0.0] 
    num_part_B2=5
    centt=part_B2_pt[0]
    part_B2_area=parea_cal(num_part_B2,part_B2_pt,centt)    
    print "part_B2_area =", part_B2_area

    B2_EdgeMid=[hgsize+hazSize+hazExt, thick/2.0, 0.0] 

    part_B1_pt[0]=[hazExt+hazSize+hgsize, thick, 0.0]
    part_B1_pt[1]=[width2+hgsize, thick, 0.0]
    part_B1_pt[2]=[width2+hgsize, thick, -length]
    part_B1_pt[3]=[hazExt+hazSize+hgsize, thick, -length]   
    part_B1_pt[4]=[hazExt+hazSize+hgsize, thick, 0.0]
    num_part_B1=5
    
elif myGrooveType.find('Compound-bevel') != -1 :
    if(root_high < 0.0001) and (hot_high < 0.0001):
 	    part_A_pt[0]=[-hgsize-hot_width, 0.0]
	    part_A_pt[1]=[-width1-hgsize, 0.0]
	    part_A_pt[2]=[-width1-hgsize, thick]
	    part_A_pt[3]=[-hgsize-p1x, thick]   
	    part_A_pt[4]=[-hgsize-hot_width, 0.0]
	    num_part_A=5
	    centt=part_A_pt[0]
	    part_A_area=parea_cal(num_part_A,part_A_pt,centt)    
	    print "part_A_area =", part_A_area

	    part_B_pt[0]=[hgsize+hot_width, 0.0]
	    part_B_pt[1]=[width2+hgsize, 0.0]
	    part_B_pt[2]=[width2+hgsize, thick]
	    part_B_pt[3]=[hgsize+p2x, thick]   
	    part_B_pt[4]=[hgsize+hot_width, 0.0]
	    num_part_B=5
	    centt=part_B_pt[0]
	    part_B_area=parea_cal(num_part_B,part_B_pt,centt)    
	    print "part_B_area =", part_B_area   
    else:
	    part_A_pt[0]=[-hgsize, 0.0]
	    part_A_pt[1]=[-width1-hgsize, 0.0]
	    part_A_pt[2]=[-width1-hgsize, thick]
	    part_A_pt[3]=[-hgsize-p1x, thick]   
	    part_A_pt[4]=[-hgsize-hot_width, root_high+hot_high]
	    part_A_pt[5]=[-hgsize, root_high]
	    part_A_pt[6]=[-hgsize, 0.0] 
	    num_part_A=7
	    centt=part_A_pt[0]
	    part_A_area=parea_cal(num_part_A,part_A_pt,centt)    
	    print "part_A_area =", part_A_area

	    part_B_pt[0]=[hgsize, 0.0]
	    part_B_pt[1]=[width2+hgsize, 0.0]
	    part_B_pt[2]=[width2+hgsize, thick]
	    part_B_pt[3]=[hgsize+p2x, thick]   
	    part_B_pt[4]=[hgsize+hot_width, root_high+hot_high]
	    part_B_pt[5]=[hgsize, root_high]
	    part_B_pt[6]=[hgsize, 0.0] 
	    num_part_B=7
	    centt=part_B_pt[0]
	    part_B_area=parea_cal(num_part_B,part_B_pt,centt)    
	    print "part_B_area =", part_B_area
elif myGrooveType.find('U-groove') != -1 :
    part_A1_pt[0]=[-hgsize-hazSize-hazExt, thick, 0.000]
    part_A1_pt[1]=[-width1-hgsize, thick, 0.000]
    part_A1_pt[2]=[-width1-hgsize, thick, -length]
    part_A1_pt[3]=[-hgsize-hazSize-hazExt, thick, -length]       
    part_A1_pt[4]=[-hgsize-hazSize-hazExt, thick, 0.000]
    num_part_A1=5

    part_A2_pt[0]=[-hgsize-hazSize, 0.0]
    part_A2_pt[1]=[-hgsize-hazSize-hazExt, 0.0]
    part_A2_pt[2]=[-hgsize-hazSize-hazExt, thick]
    part_A2_pt[3]=[-x3-hazSize, thick]   
    part_A2_pt[4]=[-hgsize-hazSize, 0.0]
    num_part_A2=5
    centt=part_A2_pt[0]
    part_A2_area=parea_cal(num_part_A2,part_A2_pt,centt)    
    print "part_A2_area =", part_A2_area
    
    A2_EdgeMid=[-hgsize-hazSize-hazExt, thick/2.0, 0.0]     

    part_A3_pt[0]=[-hgsize, 0.0]
    part_A3_pt[1]=[-hgsize-hazSize, 0.0]
    part_A3_pt[2]=[-x3-hazSize, thick]
    part_A3_pt[3]=[-x3, thick]   
    part_A3_pt[4]=[-x4, y4]
    part_A3_pt[5]=[-x5, y5]
    part_A3_pt[6]=[-hgsize, root_high] 
    part_A3_pt[7]=[-hgsize, 0.0]
    num_part_A3=8
    centt=part_A3_pt[0]
    part_A3_area=parea_cal(num_part_A3,part_A3_pt,centt)    
    print "part_A3_area =", part_A3_area


    part_W_pt[0]=[-x3, thick]
    part_W_pt[1]=[-x4, y4]
    part_W_pt[2]=[-x5, y5]
    part_W_pt[3]=[-hgsize, root_high]
    if(hgsize < 0.1):   
       part_W_pt[4]=[x5, y5] 
       part_W_pt[5]=[x4, y4]  
       part_W_pt[6]=[x3, thick]   
       part_W_pt[7]=[x3+hazSize+hazExt, thick]
       part_W_pt[8]=[x3+hazSize+hazExt, 3.0*thick] 
       part_W_pt[9]=[-x3-hazSize-hazExt, 3.0*thick]
       part_W_pt[10]=[-x3-hazSize-hazExt, thick] 
       part_W_pt[11]=[-x3, thick]      
       num_part_W=12    
    else:
       part_W_pt[4]=[-hgsize, 0.0]  
       part_W_pt[5]=[hgsize, 0.0]
       part_W_pt[6]=[hgsize, root_high] 
       part_W_pt[7]=[x5, y5] 
       part_W_pt[8]=[x4, y4]  
       part_W_pt[9]=[x3, thick]   
       part_W_pt[10]=[x3+hazSize+hazExt, thick]
       part_W_pt[11]=[x3+hazSize+hazExt, 3.0*thick] 
       part_W_pt[12]=[-x3-hazSize-hazExt, 3.0*thick]
       part_W_pt[13]=[-x3-hazSize-hazExt, thick] 
       part_W_pt[14]=[-x3, thick]      
       num_part_W=15
    
    centt=part_W_pt[0]
    part_W_area=parea_cal(num_part_W,part_W_pt,centt)    
    print "part_W_area =", part_W_area

    part_B3_pt[0]=[hgsize, 0.0]
    part_B3_pt[1]=[hgsize+hazSize, 0.0]
    part_B3_pt[2]=[x3+hazSize, thick]
    part_B3_pt[3]=[x3, thick]   
    part_B3_pt[4]=[x4, y4]
    part_B3_pt[5]=[x5, y5]
    part_B3_pt[6]=[hgsize, root_high] 
    part_B3_pt[7]=[hgsize, 0.0]
    num_part_B3=8
    centt=part_B3_pt[0]
    part_B3_area=parea_cal(num_part_B3,part_B3_pt,centt)    
    print "part_B3_area =", part_B3_area

    part_B2_pt[0]=[hgsize+hazSize, 0.0]
    part_B2_pt[1]=[hgsize+hazSize+hazExt, 0.0]
    part_B2_pt[2]=[hgsize+hazSize+hazExt, thick]
    part_B2_pt[3]=[x3+hazSize, thick]   
    part_B2_pt[4]=[hgsize+hazSize, 0.0]
    num_part_B2=5
    centt=part_B2_pt[0]
    part_B2_area=parea_cal(num_part_B2,part_B2_pt,centt)    
    print "part_B2_area =", part_B2_area

    B2_EdgeMid=[hgsize+hazSize+hazExt, thick/2.0, 0.0]    
    
    part_B1_pt[0]=[hgsize+hazSize+hazExt, thick, 0.000]
    part_B1_pt[1]=[width2+hgsize, thick, 0.000]
    part_B1_pt[2]=[width2+hgsize, thick, -length]
    part_B1_pt[3]=[hgsize+hazSize+hazExt, thick, -length]       
    part_B1_pt[4]=[hgsize+hazSize+hazExt, thick, 0.000]
    num_part_A1=5
elif myGrooveType.find('J-groove') != -1 :

    part_A1_pt[0]=[-hgsize-hazSize-hazExt, thick, 0.000]
    part_A1_pt[1]=[-width1-hgsize, thick, 0.000]
    part_A1_pt[2]=[-width1-hgsize, thick, -length]
    part_A1_pt[3]=[-hgsize-hazSize-hazExt, thick, -length]       
    part_A1_pt[4]=[-hgsize-hazSize-hazExt, thick, 0.000]
    num_part_A1=5

    part_A2_pt[0]=[-hgsize-hazSize, 0.0]
    part_A2_pt[1]=[-hgsize-hazSize-hazExt, 0.0]
    part_A2_pt[2]=[-hgsize-hazSize-hazExt, thick]
    part_A2_pt[3]=[-hgsize-hazSize, thick]   
    part_A2_pt[4]=[-hgsize-hazSize, 0.0]
    num_part_A2=5
    centt=part_A2_pt[0]
    part_A2_area=parea_cal(num_part_A2,part_A2_pt,centt)    
    print "part_A2_area =", part_A2_area
    
    A2_EdgeMid=[-hgsize-hazSize-hazExt, thick/2.0, 0.0]     

    part_A3_pt[0]=[-hgsize, 0.0]
    part_A3_pt[1]=[-hgsize-hazSize, 0.0]
    part_A3_pt[2]=[-hgsize-hazSize, thick]
    part_A3_pt[3]=[-hgsize, thick]   
    part_A3_pt[4]=[-hgsize, 0.0]
    num_part_A3=5
    centt=part_A3_pt[0]
    part_A3_area=parea_cal(num_part_A3,part_A3_pt,centt)    
    print "part_A3_area =", part_A3_area
    
    part_W_pt[0]=[-hgsize, thick]
    if(hgsize < 0.1):   
       part_W_pt[1]=[-hgsize, y5]
       part_W_pt[2]=[x5, y5] 
       part_W_pt[3]=[x4, y4]  
       part_W_pt[4]=[x3, thick]   
       part_W_pt[5]=[x3+hazSize+hazExt, thick] 
       part_W_pt[6]=[x3+hazSize+hazExt, 3.0*thick] 
       part_W_pt[7]=[-hgsize-hazSize-hazExt, 3.0*thick]
       part_W_pt[8]=[-hgsize-hazSize-hazExt, thick]       
       part_W_pt[9]=[-hgsize, thick]      
       num_part_W=10    
    else:
       part_W_pt[1]=[-hgsize, 0.0]  
       part_W_pt[2]=[hgsize, 0.0]
       part_W_pt[3]=[hgsize, root_high] 
       part_W_pt[4]=[x5, y5] 
       part_W_pt[5]=[x4, y4]  
       part_W_pt[6]=[x3, thick]   
       part_W_pt[7]=[x3+hazSize+hazExt, thick] 
       part_W_pt[8]=[x3+hazSize+hazExt, 3.0*thick] 
       part_W_pt[9]=[-hgsize-hazSize-hazExt, 3.0*thick] 
       part_W_pt[10]=[-hgsize-hazSize-hazExt, thick]
       part_W_pt[11]=[-hgsize, thick]       
       num_part_W=12
    
    centt=part_W_pt[0]
    part_W_area=parea_cal(num_part_W,part_W_pt,centt)    
    print "part_W_area =", part_W_area
  
    part_B3_pt[0]=[hgsize, 0.0]
    part_B3_pt[1]=[hgsize+hazSize, 0.0]
    part_B3_pt[2]=[x3+hazSize, thick]
    part_B3_pt[3]=[x3, thick]   
    part_B3_pt[4]=[x4, y4]
    part_B3_pt[5]=[x5, y5]
    part_B3_pt[6]=[hgsize, root_high] 
    part_B3_pt[7]=[hgsize, 0.0]
    num_part_B3=8
    centt=part_B3_pt[0]
    part_B3_area=parea_cal(num_part_B3,part_B3_pt,centt)    
    print "part_B3_area =", part_B3_area

    part_B2_pt[0]=[hgsize+hazSize, 0.0]
    part_B2_pt[1]=[hgsize+hazSize+hazExt, 0.0]
    part_B2_pt[2]=[hgsize+hazSize+hazExt, thick]
    part_B2_pt[3]=[x3+hazSize, thick]   
    part_B2_pt[4]=[hgsize+hazSize, 0.0]
    num_part_B2=5
    centt=part_B2_pt[0]
    part_B2_area=parea_cal(num_part_B2,part_B2_pt,centt)    
    print "part_B2_area =", part_B2_area

    B2_EdgeMid=[hgsize+hazSize+hazExt, thick/2.0, 0.0]    
    
    part_B1_pt[0]=[hgsize+hazSize+hazExt, thick, 0.000]
    part_B1_pt[1]=[width2+hgsize, thick, 0.000]
    part_B1_pt[2]=[width2+hgsize, thick, -length]
    part_B1_pt[3]=[hgsize+hazSize+hazExt, thick, -length]       
    part_B1_pt[4]=[hgsize+hazSize+hazExt, thick, 0.000]
    num_part_A1=5
   
elif myGrooveType.find('Bead-on-plate') != -1 :
    part_A_pt[0]=[0.0, 0.0]
    part_A_pt[1]=[-width1, 0.0]
    part_A_pt[2]=[-width1, thick]
    part_A_pt[3]=[0.0, thick]    
    part_A_pt[4]=[0.0, 0.0]
    num_part_A=5
    centt=part_A_pt[0]
    part_A_area=parea_cal(num_part_A,part_A_pt,centt)    
    print "part_A_area =", part_A_area
    
    part_B_pt[0]=[0.0, 0.0]
    part_B_pt[1]=[width2, 0.0]
    part_B_pt[2]=[width2, thick]
    part_B_pt[3]=[0.0, thick]   
    part_B_pt[4]=[0.0, 0.0] 
    num_part_B=5
    centt=part_B_pt[0]
    part_B_area=parea_cal(num_part_B,part_B_pt,centt)    
    print "part_B_area =", part_B_area
elif myGrooveType.find('Butt-joint') != -1 :
    part_A_pt[0]=[-hgsize, 0.0]
    part_A_pt[1]=[-width1-hgsize, 0.0]
    part_A_pt[2]=[-width1-hgsize, thick]
    part_A_pt[3]=[-hgsize-p1x, thick]   
    part_A_pt[4]=[-hgsize, root_high]
    part_A_pt[5]=[-hgsize, 0.0] 
    num_part_A=len(part_A_pt)
    centt=part_A_pt[0]
    part_A_area=parea_cal(num_part_A,part_A_pt,centt)    
    print "part_A_area =", part_A_area
    
    part_B_pt[0]=[hgsize, 0.0]
    part_B_pt[1]=[width2+hgsize, 0.0]
    part_B_pt[2]=[width2+hgsize, thick]
    part_B_pt[3]=[hgsize+p2x, thick]   
    part_B_pt[4]=[hgsize, root_high]
    part_B_pt[5]=[hgsize, 0.0] 
    num_part_B=len(part_B_pt)
    centt=part_B_pt[0]
    part_B_area=parea_cal(num_part_B,part_B_pt,centt)    
    print "part_B_area =", part_B_area
elif myGrooveType.find('Bevel-groove') != -1 :
    part_A_pt[0]=[-hgsize, 0.0]
    part_A_pt[1]=[-width1-hgsize, 0.0]
    part_A_pt[2]=[-width1-hgsize, thick]
    part_A_pt[3]=[-hgsize-p1x, thick]   
    part_A_pt[4]=[-hgsize, 0.0] 
    num_part_A=5
    centt=part_A_pt[0]
    part_A_area=parea_cal(num_part_A,part_A_pt,centt)    
    print "part_A_area =", part_A_area
    
    part_B_pt[0]=[hgsize, 0.0]
    part_B_pt[1]=[width2+hgsize, 0.0]
    part_B_pt[2]=[width2+hgsize, thick]
    part_B_pt[3]=[hgsize+p2x, thick]   
    part_B_pt[4]=[hgsize, root_high]
    part_B_pt[5]=[hgsize, 0.0] 
    
    print part_B_pt[3]
    num_part_B=6
    centt=part_B_pt[0]
    part_B_area=parea_cal(num_part_B,part_B_pt,centt)    
    print "part_B_area =", part_B_area
elif myGrooveType.find('Bevel-left') != -1 :
    part_A_pt[0]=[-hgsize, 0.0]
    part_A_pt[1]=[-width1-hgsize, 0.0]
    part_A_pt[2]=[-width1-hgsize, thick]
    part_A_pt[3]=[-hgsize-p1x, thick]   
    part_A_pt[4]=[-hgsize, 0.0] 
    num_part_A=5
    centt=part_A_pt[0]
    part_A_area=parea_cal(num_part_A,part_A_pt,centt)    
    print "part_A_area =", part_A_area
    
    part_B_pt[0]=[hgsize, 0.0]
    part_B_pt[1]=[width2+hgsize, 0.0]
    part_B_pt[2]=[width2+hgsize, thick]
    part_B_pt[3]=[hgsize+p2x, thick]   
    part_B_pt[4]=[hgsize, 0.0] 
    num_part_B=5
    centt=part_B_pt[0]
    part_B_area=parea_cal(num_part_B,part_B_pt,centt)    
    print "part_B_area =", part_B_area
elif myGrooveType.find('T-Bevel') != -1 :
    part_A_pt[0]=[ 0.0, 0.0]
    part_A_pt[1]=[-width1, 0.0]
    part_A_pt[2]=[-width1, -thick1]
    part_A_pt[3]=[ 0.0, -thick1]
    part_A_pt[4]=[ width2, -thick1]   
    part_A_pt[5]=[ width2, 0.0] 
    part_A_pt[6]=[ 0.0, 0.0]
    num_part_A=7
    centt=part_A_pt[0]
    part_A_area=parea_cal(num_part_A,part_A_pt,centt)    
    print "part_A_area =", part_A_area

    part_B_pt[0]=[ tee_x1, TeeGap]
    part_B_pt[1]=[ thick2/2.0, tee_y2]
    part_B_pt[2]=[ thick2/2.0, TeeGap+width3]
    part_B_pt[3]=[-thick2/2.0, TeeGap+width3]   
    part_B_pt[4]=[-thick2/2.0, tee_y5]
    part_B_pt[5]=[ tee_x6, TeeGap] 
    part_B_pt[6]=[ tee_x1, TeeGap] 
    num_part_B=7
    centt=part_B_pt[0]
    #centt=[5.645322, 4.757973]
    part_B_area=parea_cal(num_part_B,part_B_pt,centt)    
    print "part_B_area =", part_B_area
else:
    part_A_pt[0]=[-hgsize, 0.0]
    part_A_pt[1]=[-width-hgsize, 0.0]
    part_A_pt[2]=[-width-hgsize, thick]
    part_A_pt[3]=[-hgsize-p1x, thick]   
    part_A_pt[4]=[-hgsize, root_high]
    part_A_pt[5]=[-hgsize, 0.0] 
    num_part_A=len(part_A_pt)
    centt=part_A_pt[0]
    part_A_area=parea_cal(num_part_A,part_A_pt,centt)    
    print "part_A_area =", part_A_area

    part_B_pt[0]=[hgsize, 0.0]
    part_B_pt[1]=[width+hgsize, 0.0]
    part_B_pt[2]=[width+hgsize, thick]
    part_B_pt[3]=[hgsize+p2x, thick]   
    part_B_pt[4]=[hgsize, root_high]
    part_B_pt[5]=[hgsize, 0.0] 
    num_part_B=len(part_B_pt)
    centt=part_B_pt[0]
    part_B_area=parea_cal(num_part_B,part_B_pt,centt)    
    print "part_B_area =", part_B_area
#-------------------------------------------------------------
# Start Salome
#
import salome

salome.salome_init()
theStudy = salome.myStudy

import salome_notebook
notebook = salome_notebook.NoteBook(theStudy)
sys.path.insert( 0, r'C:/SALOME/SALOME-8.2.0-WIN64/WORK')

###
### GEOM component
###
#
import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS
#
geompy = geomBuilder.New(theStudy)
#
# Coordinate system
#
O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)

geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )
#-----------------------------
# Creating Plate_A1, Plate_A2, Plate_A3
#
if myGrooveType.find('V-groove') != -1 : 
   geomObj_A1 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
   Vertex_A11 = geompy.MakeVertex(part_A1_pt[0][0], part_A1_pt[0][1], part_A1_pt[0][2])
   Vertex_A12 = geompy.MakeVertex(part_A1_pt[1][0], part_A1_pt[1][1], part_A1_pt[1][2])
   Vertex_A13 = geompy.MakeVertex(part_A1_pt[2][0], part_A1_pt[2][1], part_A1_pt[2][2])
   Vertex_A14 = geompy.MakeVertex(part_A1_pt[3][0], part_A1_pt[3][1], part_A1_pt[3][2])
   geompy.addToStudy( Vertex_A11, 'Vertex_A11' )
   geompy.addToStudy( Vertex_A12, 'Vertex_A12' )
   geompy.addToStudy( Vertex_A13, 'Vertex_A13' )
   geompy.addToStudy( Vertex_A14, 'Vertex_A14' )
   
   Line_A11 = geompy.MakeLineTwoPnt(Vertex_A11, Vertex_A12)
   geompy.addToStudy( Line_A11, 'Line_A11' )
          
   Line_A12 = geompy.MakeLineTwoPnt(Vertex_A12, Vertex_A13)
   Line_A13 = geompy.MakeLineTwoPnt(Vertex_A13, Vertex_A14)
   Line_A14 = geompy.MakeLineTwoPnt(Vertex_A14, Vertex_A11)
   Face_A1 = geompy.MakeFaceWires([Line_A11, Line_A12, Line_A13, Line_A14], 1)
   #partA1 = geompy.MakePrismVecH(Face_A1, OY, -thick)
   
   Pobject = geompy.MakeCDG(Line_A14)
   A1_EdgeMid = geompy.PointCoordinates(Pobject)
   Pobject = geompy.MakeCDG(Face_A1)
   A1_FaceMid = geompy.PointCoordinates(Pobject)
 
   geomObj_A2 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
   sk = geompy.Sketcher2D()
   sk.addPoint(part_A2_pt[0][0], part_A2_pt[0][1])
   for i in range(num_part_A2-1):
       sk.addSegmentAbsolute(part_A2_pt[i+1][0], part_A2_pt[i+1][1])

   Sketch_A2 = sk.wire(geomObj_A2)
   Face_A2 = geompy.MakeFaceWires([Sketch_A2], 1)
   #partA2 = geompy.MakePrismVecH(Face_A2, OZ, -length)

   Pobject = geompy.MakeCDG(Face_A2)
   A2_FaceMid = geompy.PointCoordinates(Pobject)

   geomObj_A3 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
   sk = geompy.Sketcher2D()
   sk.addPoint(part_A3_pt[0][0], part_A3_pt[0][1])
   for i in range(num_part_A3-1):
       sk.addSegmentAbsolute(part_A3_pt[i+1][0], part_A3_pt[i+1][1])

   Sketch_A3 = sk.wire(geomObj_A3)
   Face_A3 = geompy.MakeFaceWires([Sketch_A3], 1)
   #partA3 = geompy.MakePrismVecH(Face_A3, OZ, -length)

   Pobject = geompy.MakeCDG(Face_A3)
   A3_FaceMid = geompy.PointCoordinates(Pobject)

   # Create a vector based on Vertex_A11 for defining a plane for a cooling surface in
   # mesh step
   coolingPlane = geompy.MakePlane(Vertex_A11, OY, 500)
   geompy.addToStudy( coolingPlane, 'coolingPlane')


elif myGrooveType.find('Compound-bevel') != -1 :
   for i in range(num_part_A-1):
       s.Line(point1=part_A_pt[i], point2=part_A_pt[i+1])

elif myGrooveType.find('U-groove') != -1 :
## - A1 - 
   geomObj_A1 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
   Vertex_A11 = geompy.MakeVertex(part_A1_pt[0][0], part_A1_pt[0][1], part_A1_pt[0][2])
   Vertex_A12 = geompy.MakeVertex(part_A1_pt[1][0], part_A1_pt[1][1], part_A1_pt[1][2])
   Vertex_A13 = geompy.MakeVertex(part_A1_pt[2][0], part_A1_pt[2][1], part_A1_pt[2][2])
   Vertex_A14 = geompy.MakeVertex(part_A1_pt[3][0], part_A1_pt[3][1], part_A1_pt[3][2])
   geompy.addToStudy( Vertex_A11, 'Vertex_A11' )
   geompy.addToStudy( Vertex_A12, 'Vertex_A12' )
   geompy.addToStudy( Vertex_A13, 'Vertex_A13' )
   geompy.addToStudy( Vertex_A14, 'Vertex_A14' )
   
   Line_A11 = geompy.MakeLineTwoPnt(Vertex_A11, Vertex_A12)
   geompy.addToStudy( Line_A11, 'Line_A11' )
          
   Line_A12 = geompy.MakeLineTwoPnt(Vertex_A12, Vertex_A13)
   Line_A13 = geompy.MakeLineTwoPnt(Vertex_A13, Vertex_A14)
   Line_A14 = geompy.MakeLineTwoPnt(Vertex_A14, Vertex_A11)
   Face_A1 = geompy.MakeFaceWires([Line_A11, Line_A12, Line_A13, Line_A14], 1)
   #partA1 = geompy.MakePrismVecH(Face_A1, OY, -thick)
   
   Pobject = geompy.MakeCDG(Line_A14)
   A1_EdgeMid = geompy.PointCoordinates(Pobject)
   Pobject = geompy.MakeCDG(Face_A1)
   A1_FaceMid = geompy.PointCoordinates(Pobject)
## - A2 - 
   geomObj_A2 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
   sk = geompy.Sketcher2D()
   sk.addPoint(part_A2_pt[0][0], part_A2_pt[0][1])
   for i in range(num_part_A2-1):
       sk.addSegmentAbsolute(part_A2_pt[i+1][0], part_A2_pt[i+1][1])

   Sketch_A2 = sk.wire(geomObj_A2)
   Face_A2 = geompy.MakeFaceWires([Sketch_A2], 1)
   #partA2 = geompy.MakePrismVecH(Face_A2, OZ, -length)

   Pobject = geompy.MakeCDG(Face_A2)
   A2_FaceMid = geompy.PointCoordinates(Pobject)
## - A3 - 
   geomObj_A3 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
   sk = geompy.Sketcher2D()
   sk.addPoint(part_A3_pt[0][0], part_A3_pt[0][1])
   for i in range(num_part_A3-1):
       sk.addSegmentAbsolute(part_A3_pt[i+1][0], part_A3_pt[i+1][1])

   Sketch_A3 = sk.wire(geomObj_A3)
   Face_A3 = geompy.MakeFaceWires([Sketch_A3], 1)
   #partA3 = geompy.MakePrismVecH(Face_A3, OZ, -length)

   Pobject = geompy.MakeCDG(Face_A3)
   A3_FaceMid = geompy.PointCoordinates(Pobject)

   #s.ArcByCenterEnds(center=(-hgsize-hot_width, root_high+radius), point1=part_A_pt[5], point2=part_A_pt[4], direction=CLOCKWISE)

elif myGrooveType.find('J-groove') != -1 :
## - A1 - 
   geomObj_A1 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
   Vertex_A11 = geompy.MakeVertex(part_A1_pt[0][0], part_A1_pt[0][1], part_A1_pt[0][2])
   Vertex_A12 = geompy.MakeVertex(part_A1_pt[1][0], part_A1_pt[1][1], part_A1_pt[1][2])
   Vertex_A13 = geompy.MakeVertex(part_A1_pt[2][0], part_A1_pt[2][1], part_A1_pt[2][2])
   Vertex_A14 = geompy.MakeVertex(part_A1_pt[3][0], part_A1_pt[3][1], part_A1_pt[3][2])
   geompy.addToStudy( Vertex_A11, 'Vertex_A11' )
   geompy.addToStudy( Vertex_A12, 'Vertex_A12' )
   geompy.addToStudy( Vertex_A13, 'Vertex_A13' )
   geompy.addToStudy( Vertex_A14, 'Vertex_A14' )
   
   Line_A11 = geompy.MakeLineTwoPnt(Vertex_A11, Vertex_A12)
   geompy.addToStudy( Line_A11, 'Line_A11' )
          
   Line_A12 = geompy.MakeLineTwoPnt(Vertex_A12, Vertex_A13)
   Line_A13 = geompy.MakeLineTwoPnt(Vertex_A13, Vertex_A14)
   Line_A14 = geompy.MakeLineTwoPnt(Vertex_A14, Vertex_A11)
   Face_A1 = geompy.MakeFaceWires([Line_A11, Line_A12, Line_A13, Line_A14], 1)
   #partA1 = geompy.MakePrismVecH(Face_A1, OY, -thick)
   
   Pobject = geompy.MakeCDG(Line_A14)
   A1_EdgeMid = geompy.PointCoordinates(Pobject)
   Pobject = geompy.MakeCDG(Face_A1)
   A1_FaceMid = geompy.PointCoordinates(Pobject)
## - A2 - 
   geomObj_A2 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
   sk = geompy.Sketcher2D()
   sk.addPoint(part_A2_pt[0][0], part_A2_pt[0][1])
   for i in range(num_part_A2-1):
       sk.addSegmentAbsolute(part_A2_pt[i+1][0], part_A2_pt[i+1][1])

   Sketch_A2 = sk.wire(geomObj_A2)
   Face_A2 = geompy.MakeFaceWires([Sketch_A2], 1)
   #partA2 = geompy.MakePrismVecH(Face_A2, OZ, -length)

   Pobject = geompy.MakeCDG(Face_A2)
   A2_FaceMid = geompy.PointCoordinates(Pobject)
## - A3 - 
   geomObj_A3 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
   sk = geompy.Sketcher2D()
   sk.addPoint(part_A3_pt[0][0], part_A3_pt[0][1])
   for i in range(num_part_A3-1):
       sk.addSegmentAbsolute(part_A3_pt[i+1][0], part_A3_pt[i+1][1])

   Sketch_A3 = sk.wire(geomObj_A3)
   Face_A3 = geompy.MakeFaceWires([Sketch_A3], 1)
   #partA3 = geompy.MakePrismVecH(Face_A3, OZ, -length)

   Pobject = geompy.MakeCDG(Face_A3)
   A3_FaceMid = geompy.PointCoordinates(Pobject)
   
elif myGrooveType.find('Bevel-groove') != -1 :
   for i in range(num_part_A-1):
       s.Line(point1=part_A_pt[i], point2=part_A_pt[i+1])
elif myGrooveType.find('Bevel-left') != -1 :
   for i in range(num_part_A-1):
       s.Line(point1=part_A_pt[i], point2=part_A_pt[i+1])
elif myGrooveType.find('Bead-on-plate') != -1 :
   for i in range(num_part_A-1):
       s.Line(point1=part_A_pt[i], point2=part_A_pt[i+1])
elif myGrooveType.find('Butt-joint') != -1 :
   for i in range(num_part_A-1):
       s.Line(point1=part_A_pt[i], point2=part_A_pt[i+1])
else:
   for i in range(num_part_A-1):
       s.Line(point1=part_A_pt[i], point2=part_A_pt[i+1])

geompy.addToStudy( Line_A12, 'Line_A12' )
geompy.addToStudy( Line_A13, 'Line_A13' )
geompy.addToStudy( Line_A14, 'Line_A14' )
geompy.addToStudy( Face_A1, 'Face_A1' )

geompy.addToStudy( Sketch_A2, 'Sketch_A2' )
geompy.addToStudy( Face_A2, 'Face_A2' )
geompy.addToStudy( Sketch_A3, 'Sketch_A3' )
geompy.addToStudy( Face_A3, 'Face_A3' )
#--------------------------------------------------------------------
# Creating Plate_B3 Plate_B2 Plate_B1
#
if myGrooveType.find('V-groove') != -1 :

   geomObj_B3 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
   sk = geompy.Sketcher2D()
   sk.addPoint(0.000000, 0.000000)
   sk.addPoint(part_B3_pt[0][0], part_B3_pt[0][1])
   for i in range(num_part_B3-1):
       sk.addSegmentAbsolute(part_B3_pt[i+1][0], part_B3_pt[i+1][1])
   
   Sketch_B3 = sk.wire(geomObj_B3)
   Face_B3 = geompy.MakeFaceWires([Sketch_B3], 1)
   #partB3 = geompy.MakePrismVecH(Face_B3, OZ, -200)    
   Pobject = geompy.MakeCDG(Face_B3)
   B3_FaceMid = geompy.PointCoordinates(Pobject)
   
   geomObj_B2 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
   sk = geompy.Sketcher2D()
   sk.addPoint(0.000000, 0.000000)
   sk.addPoint(part_B2_pt[0][0], part_B2_pt[0][1])
   for i in range(num_part_B2-1):
       sk.addSegmentAbsolute(part_B2_pt[i+1][0], part_B2_pt[i+1][1])
   
   Sketch_B2 = sk.wire(geomObj_B2)
   Face_B2 = geompy.MakeFaceWires([Sketch_B2], 1)
   #partB2 = geompy.MakePrismVecH(Face_B2, OZ, -200)  
   Pobject = geompy.MakeCDG(Face_B2)
   B2_FaceMid = geompy.PointCoordinates(Pobject)
   
   geomObj_B1 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
   Vertex_1 = geompy.MakeVertex(part_B1_pt[0][0], part_B1_pt[0][1], part_B1_pt[0][2])
   Vertex_2 = geompy.MakeVertex(part_B1_pt[1][0], part_B1_pt[1][1], part_B1_pt[1][2])
   Vertex_3 = geompy.MakeVertex(part_B1_pt[2][0], part_B1_pt[2][1], part_B1_pt[2][2])
   Vertex_4 = geompy.MakeVertex(part_B1_pt[3][0], part_B1_pt[3][1], part_B1_pt[3][2])
   Line_B11 = geompy.MakeLineTwoPnt(Vertex_1, Vertex_2)
   Line_B12 = geompy.MakeLineTwoPnt(Vertex_2, Vertex_3)
   Line_B13 = geompy.MakeLineTwoPnt(Vertex_3, Vertex_4)
   Line_B14 = geompy.MakeLineTwoPnt(Vertex_4, Vertex_1)
   Face_B1 = geompy.MakeFaceWires([Line_B11, Line_B12, Line_B13, Line_B14], 1)
   #partB1 = geompy.MakePrismVecH(Face_B1, OY, -thick)  

   Pobject = geompy.MakeCDG(Line_B14)
   B1_EdgeMid = geompy.PointCoordinates(Pobject)
   Pobject = geompy.MakeCDG(Face_B1)
   B1_FaceMid = geompy.PointCoordinates(Pobject)
   
elif myGrooveType.find('Compound-bevel') != -1 :
   for i in range(num_part_B-1):
       s.Line(point1=part_B_pt[i], point2=part_B_pt[i+1])

elif myGrooveType.find('U-groove') != -1 :

   geomObj_B3 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
   sk = geompy.Sketcher2D()
   sk.addPoint(0.000000, 0.000000)
   sk.addPoint(part_B3_pt[0][0], part_B3_pt[0][1])
   for i in range(num_part_B3-1):
       sk.addSegmentAbsolute(part_B3_pt[i+1][0], part_B3_pt[i+1][1])
   
   Sketch_B3 = sk.wire(geomObj_B3)
   Face_B3 = geompy.MakeFaceWires([Sketch_B3], 1)
   #partB3 = geompy.MakePrismVecH(Face_B3, OZ, -200)    
   Pobject = geompy.MakeCDG(Face_B3)
   B3_FaceMid = geompy.PointCoordinates(Pobject)
   
   geomObj_B2 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
   sk = geompy.Sketcher2D()
   sk.addPoint(0.000000, 0.000000)
   sk.addPoint(part_B2_pt[0][0], part_B2_pt[0][1])
   for i in range(num_part_B2-1):
       sk.addSegmentAbsolute(part_B2_pt[i+1][0], part_B2_pt[i+1][1])
   
   Sketch_B2 = sk.wire(geomObj_B2)
   Face_B2 = geompy.MakeFaceWires([Sketch_B2], 1)
   #partB2 = geompy.MakePrismVecH(Face_B2, OZ, -200)  
   Pobject = geompy.MakeCDG(Face_B2)
   B2_FaceMid = geompy.PointCoordinates(Pobject)
   
   geomObj_B1 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
   Vertex_1 = geompy.MakeVertex(part_B1_pt[0][0], part_B1_pt[0][1], part_B1_pt[0][2])
   Vertex_2 = geompy.MakeVertex(part_B1_pt[1][0], part_B1_pt[1][1], part_B1_pt[1][2])
   Vertex_3 = geompy.MakeVertex(part_B1_pt[2][0], part_B1_pt[2][1], part_B1_pt[2][2])
   Vertex_4 = geompy.MakeVertex(part_B1_pt[3][0], part_B1_pt[3][1], part_B1_pt[3][2])
   Line_B11 = geompy.MakeLineTwoPnt(Vertex_1, Vertex_2)
   Line_B12 = geompy.MakeLineTwoPnt(Vertex_2, Vertex_3)
   Line_B13 = geompy.MakeLineTwoPnt(Vertex_3, Vertex_4)
   Line_B14 = geompy.MakeLineTwoPnt(Vertex_4, Vertex_1)
   Face_B1 = geompy.MakeFaceWires([Line_B11, Line_B12, Line_B13, Line_B14], 1)
   #partB1 = geompy.MakePrismVecH(Face_B1, OY, -thick)  

   Pobject = geompy.MakeCDG(Line_B14)
   B1_EdgeMid = geompy.PointCoordinates(Pobject)
   Pobject = geompy.MakeCDG(Face_B1)
   B1_FaceMid = geompy.PointCoordinates(Pobject)

   #s.ArcByCenterEnds(center=(hgsize+hot_width, root_high+radius), point1=part_B_pt[4], point2=part_B_pt[5], direction=CLOCKWISE)

elif myGrooveType.find('J-groove') != -1 :

   geomObj_B3 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
   sk = geompy.Sketcher2D()
   sk.addPoint(0.000000, 0.000000)
   sk.addPoint(part_B3_pt[0][0], part_B3_pt[0][1])
   for i in range(num_part_B3-1):
       sk.addSegmentAbsolute(part_B3_pt[i+1][0], part_B3_pt[i+1][1])
   
   Sketch_B3 = sk.wire(geomObj_B3)
   Face_B3 = geompy.MakeFaceWires([Sketch_B3], 1)
   #partB3 = geompy.MakePrismVecH(Face_B3, OZ, -200)    
   Pobject = geompy.MakeCDG(Face_B3)
   B3_FaceMid = geompy.PointCoordinates(Pobject)
   
   geomObj_B2 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
   sk = geompy.Sketcher2D()
   sk.addPoint(0.000000, 0.000000)
   sk.addPoint(part_B2_pt[0][0], part_B2_pt[0][1])
   for i in range(num_part_B2-1):
       sk.addSegmentAbsolute(part_B2_pt[i+1][0], part_B2_pt[i+1][1])
   
   Sketch_B2 = sk.wire(geomObj_B2)
   Face_B2 = geompy.MakeFaceWires([Sketch_B2], 1)
   #partB2 = geompy.MakePrismVecH(Face_B2, OZ, -200)  
   Pobject = geompy.MakeCDG(Face_B2)
   B2_FaceMid = geompy.PointCoordinates(Pobject)
   
   geomObj_B1 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
   Vertex_1 = geompy.MakeVertex(part_B1_pt[0][0], part_B1_pt[0][1], part_B1_pt[0][2])
   Vertex_2 = geompy.MakeVertex(part_B1_pt[1][0], part_B1_pt[1][1], part_B1_pt[1][2])
   Vertex_3 = geompy.MakeVertex(part_B1_pt[2][0], part_B1_pt[2][1], part_B1_pt[2][2])
   Vertex_4 = geompy.MakeVertex(part_B1_pt[3][0], part_B1_pt[3][1], part_B1_pt[3][2])
   Line_B11 = geompy.MakeLineTwoPnt(Vertex_1, Vertex_2)
   Line_B12 = geompy.MakeLineTwoPnt(Vertex_2, Vertex_3)
   Line_B13 = geompy.MakeLineTwoPnt(Vertex_3, Vertex_4)
   Line_B14 = geompy.MakeLineTwoPnt(Vertex_4, Vertex_1)
   Face_B1 = geompy.MakeFaceWires([Line_B11, Line_B12, Line_B13, Line_B14], 1)
   #partB1 = geompy.MakePrismVecH(Face_B1, OY, -thick)  

   Pobject = geompy.MakeCDG(Line_B14)
   B1_EdgeMid = geompy.PointCoordinates(Pobject)
   Pobject = geompy.MakeCDG(Face_B1)
   B1_FaceMid = geompy.PointCoordinates(Pobject)

   #s.ArcByCenterEnds(center=(hgsize+hot_width, root_high+radius), point1=part_B_pt[4], point2=part_B_pt[5], direction=CLOCKWISE)

elif myGrooveType.find('Bevel-groove') != -1 :
   for i in range(num_part_B-1):
       s.Line(point1=part_B_pt[i], point2=part_B_pt[i+1])
elif myGrooveType.find('Bevel-left') != -1 :
   for i in range(num_part_B-1):
       s.Line(point1=part_B_pt[i], point2=part_B_pt[i+1])
elif myGrooveType.find('Bead-on-plate') != -1 :
   for i in range(num_part_B-1):
       s.Line(point1=part_B_pt[i], point2=part_B_pt[i+1])       
elif myGrooveType.find('Butt-joint') != -1 :
   for i in range(num_part_B-1):
       s.Line(point1=part_B_pt[i], point2=part_B_pt[i+1])
else:
   for i in range(num_part_B-1):
       s.Line(point1=part_B_pt[i], point2=part_B_pt[i+1])
#------------------------------------------------------------------
#
geompy.addToStudy( Line_B11, 'Line_B11' )
geompy.addToStudy( Line_B12, 'Line_B12' )
geompy.addToStudy( Line_B13, 'Line_B13' )
geompy.addToStudy( Line_B14, 'Line_B14' )
geompy.addToStudy( Face_B1, 'Face_B1' )

geompy.addToStudy( Sketch_B2, 'Sketch_B2' )
geompy.addToStudy( Face_B2, 'Face_B2' )
geompy.addToStudy( Sketch_B3, 'Sketch_B3' )
geompy.addToStudy( Face_B3, 'Face_B3' )

#--------------------------------------------------------------------
# Creating Plate_W
#
geomObj_W = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
sk = geompy.Sketcher2D()
sk.addPoint(0.000000, 0.000000)

if myGrooveType.find('V-groove') != -1 :

   sk.addPoint(part_W_pt[0][0], part_W_pt[0][1])
   for i in range(num_part_W-1):
       sk.addSegmentAbsolute(part_W_pt[i+1][0], part_W_pt[i+1][1])

elif myGrooveType.find('Compound-bevel') != -1 :

   for i in range(num_part_B-1):
       s.Line(point1=part_B_pt[i], point2=part_B_pt[i+1])

elif myGrooveType.find('U-groove') != -1 :
   sk.addPoint(part_W_pt[0][0], part_W_pt[0][1])
   for i in range(num_part_W-1):
       sk.addSegmentAbsolute(part_W_pt[i+1][0], part_W_pt[i+1][1])

   #s.ArcByCenterEnds(center=(hgsize+hot_width, root_high+radius), point1=part_B_pt[4], point2=part_B_pt[5], direction=CLOCKWISE)
elif myGrooveType.find('J-groove') != -1 :
   sk.addPoint(part_W_pt[0][0], part_W_pt[0][1])
   for i in range(num_part_W-1):
       sk.addSegmentAbsolute(part_W_pt[i+1][0], part_W_pt[i+1][1])
       
   #s.ArcByCenterEnds(center=(hgsize+hot_width, root_high+radius), point1=part_B_pt[4], point2=part_B_pt[5], direction=CLOCKWISE)

elif myGrooveType.find('Bevel-groove') != -1 :

   for i in range(num_part_B-1):
       s.Line(point1=part_B_pt[i], point2=part_B_pt[i+1])
elif myGrooveType.find('Bevel-left') != -1 :

   for i in range(num_part_B-1):
       s.Line(point1=part_B_pt[i], point2=part_B_pt[i+1])
elif myGrooveType.find('Bead-on-plate') != -1 :

   for i in range(num_part_B-1):
       s.Line(point1=part_B_pt[i], point2=part_B_pt[i+1])       
elif myGrooveType.find('Butt-joint') != -1 :

   for i in range(num_part_B-1):
       s.Line(point1=part_B_pt[i], point2=part_B_pt[i+1])
else:
   for i in range(num_part_B-1):
       s.Line(point1=part_B_pt[i], point2=part_B_pt[i+1])

Sketch_W = sk.wire(geomObj_W)
Face_W = geompy.MakeFaceWires([Sketch_W], 1)
#partW = geompy.MakePrismVecH(Face_W, OZ, -length)
#----------------------------------------------
#
geompy.addToStudy( Sketch_W, 'Sketch_W' )
geompy.addToStudy( Face_W, 'Face_W' )

#--------------------------------------------------------------------
# Creating Bead
#
print "checking ----------------------"
for k in range(nweld): 
    print numpt[k]    
    print "0,", pt[k][0][0], pt[k][0][1]   
    for i in range(numpt[k]-1):
        print i+1, pt[k][i+1][0], pt[k][i+1][1]
    #end for
print "Checking -----------------------"
Sketch_P = [ [] ]*nweld  
Face_P = [ [] ]*nweld
Face_PC = [ [] ]*nweld
for k in range(nweld): 
    geomObj_W = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
    sk = geompy.Sketcher2D()
    sk.addPoint(pt[k][0][0], pt[k][0][1])
    
    print numpt[k]
    for i in range(numpt[k]-1):
        sk.addSegmentAbsolute(pt[k][i+1][0], pt[k][i+1][1])
        print i+1, pt[k][i+1][0], pt[k][i+1][1]
    #end for
    
    Sketch_P[k] = sk.wire(geomObj_W)  
    Face_P[k] = geompy.MakeFaceWires([Sketch_P[k]], 1)
    Pobj = geompy.MakeCDG(Face_P[k])
    Face_PC[k] = geompy.PointCoordinates(Pobj)
    
    geompy.addToStudy( Sketch_P[k], 'Sketch_P' + str(k+1) )
    geompy.addToStudy( Face_P[k], 'Face_P' + str(k+1)  )  
    
    #myFace.extend([Face_W])
#end for
#--------------------------------------------------------------------
# Partition Weld and merge faces
#
for k in range(nweld):
    if(k == 0):
       cutFace=Face_W
    else:
       cutFace=resuFace
    Partition_1 = geompy.MakePartition([cutFace], [Face_P[k]], [], [], geompy.ShapeType["FACE"], 0, [], 0)
    geompy.addToStudy( Partition_1, 'Partition_' + str(k+1) )
    createdFace = geompy.ExtractShapes(Partition_1, geompy.ShapeType["FACE"], True)
    print createdFace
    npf = len(createdFace)
    print "npf =", npf
    dist_max = 1.0E-7
    area_min = 1.0E+7
    jmax=-1
    jmin=-1
    jsv=-1
    for i in range(npf):
        Pobj = geompy.MakeCDG(createdFace[i])
        Pt = geompy.PointCoordinates(Pobj)
        dist=dist3D(Pt, Face_PC[k])
        if(dist > dist_max):
           dist_max = dist
           resuFace = createdFace[i]
           jmax=i
        props = geompy.BasicProperties(createdFace[i]) 
        if(props[1] < area_min):
           area_min = props[1]
           svFace = createdFace[i]
           jmin=i                    
    #end for
    print area_min
    if(area_min < 1.0):
       jsv=jmin
       if(jmin == 0):
         createdFace[jmin+1] = geompy.MakeFuseList([svFace, createdFace[jmin+1]], True, True)
       else:
         createdFace[jmin-1] = geompy.MakeFuseList([svFace, createdFace[jmin-1]], True, True)       
    for i in range(npf): 
        if(i == jmax):
           skip=-1
        elif(i == jsv):
           skip=-1
        else:
           if(k==0 and i==0):
              weldFace = [createdFace[i]]
           else:
              weldFace.extend([createdFace[i]])       
    #end for
    print k,weldFace  
#end for

fuseFace= [Face_A1,Face_A2,Face_A3,Face_B1,Face_B2,Face_B3]

nF = len(weldFace)
for i in range(nF):
    fuseFace.extend([weldFace[i]])  

Fuse_1 = geompy.MakeFuseList(fuseFace, True, True)
geompy.addToStudy( Fuse_1, 'Fuse_1' )

#--------------------------------------------------------------------
# Create geometry groups
#
EdgeIDs = geompy.ExtractShapes(Fuse_1, geompy.ShapeType["EDGE"], True)
nEdge=len(EdgeIDs)
print 'Number of edges = ', nEdge
for i in range(nEdge):
    geompy.addToStudyInFather( Fuse_1, EdgeIDs[i], 'Edge_' + str(i+1) )

A1E_min=1.0E7
A1E_id=-1

A2E_min=1.0E7
A2E_id=-1

B1E_min=1.0E7
B1E_id=-1

B2E_min=1.0E7
B2E_id=-1

for i in range(nEdge):
    Pobject = geompy.MakeCDG(EdgeIDs[i])
    Pt = geompy.PointCoordinates(Pobject)
 
    dist=dist3D(Pt, A1_EdgeMid)
    if(dist < A1E_min):
       A1E_min=dist
       A1E_id=i
    
    dist=dist3D(Pt, A2_EdgeMid)
    if(dist < A2E_min):
       A2E_min=dist
       A2E_id=i
       
    dist=dist3D(Pt, B1_EdgeMid)
    if(dist < B1E_min):
       B1E_min=dist
       B1E_id=i
       
    dist=dist3D(Pt, B2_EdgeMid)
    if(dist < B2E_min):
       B2E_min=dist
       B2E_id=i
#End For

if(A1E_min > sv or A1E_id == -1):
   print "***Error = ", A1E_min
if(A2E_min > sv or A2E_id == -1):
   print "***Error = ", A2E_min
if(B1E_min > sv or B1E_id == -1):
   print "***Error = ", B1E_min
if(B2E_min > sv or B2E_id == -1):
   print "***Error = ", B2E_min

print "A2E_id, B2E_id = ", A2E_id, B2E_id
geomObj_yy = geompy.GetInPlace(Fuse_1, EdgeIDs[A2E_id], True)
[geomObj_yp] = geompy.SubShapeAll(geomObj_yy, geompy.ShapeType["EDGE"])
FetchID1 = geompy.GetSameIDs(Fuse_1, geomObj_yp)

geomObj_yy = geompy.GetInPlace(Fuse_1, EdgeIDs[B2E_id], True)
[geomObj_yp] = geompy.SubShapeAll(geomObj_yy, geompy.ShapeType["EDGE"])
FetchID2 = geompy.GetSameIDs(Fuse_1, geomObj_yp)

GroupID = [ FetchID1[0], FetchID2[0] ]
edge_3E = geompy.CreateGroup(Fuse_1, geompy.ShapeType["EDGE"])
geompy.UnionIDs(edge_3E, GroupID)
geompy.addToStudyInFather( Fuse_1, edge_3E, 'edge_3E' )

print "A1E_id, B1E_id = ", A1E_id, B1E_id
geomObj_yy = geompy.GetInPlace(Fuse_1, EdgeIDs[A1E_id], True)
[geomObj_yp] = geompy.SubShapeAll(geomObj_yy, geompy.ShapeType["EDGE"])
FetchID1 = geompy.GetSameIDs(Fuse_1, geomObj_yp)

geomObj_yy = geompy.GetInPlace(Fuse_1, EdgeIDs[B1E_id], True)
[geomObj_yp] = geompy.SubShapeAll(geomObj_yy, geompy.ShapeType["EDGE"])
FetchID2 = geompy.GetSameIDs(Fuse_1, geomObj_yp)

GroupID = [ FetchID1[0], FetchID2[0] ]
Edge_match = geompy.CreateGroup(Fuse_1, geompy.ShapeType["EDGE"])
geompy.UnionIDs(Edge_match, GroupID)
geompy.addToStudyInFather( Fuse_1, Edge_match, 'Edge_match' )
#--------------------------- 
FaceIDs = geompy.ExtractShapes(Fuse_1, geompy.ShapeType["FACE"], True)
nFace=len(FaceIDs)
print "nFace = ", nFace
for i in range(nFace):
    geompy.addToStudyInFather( Fuse_1, FaceIDs[i], 'Face_' + str(i+1) )

A1F_min=1.0E7
A2F_min=1.0E7
A3F_min=1.0E7

B1F_min=1.0E7
B2F_min=1.0E7
B3F_min=1.0E7

PC_min = [ [],]*nweld 
PC_id  = [ [],]*nweld 
for k in range(nweld):
    PC_min[k] = 1.0E7 
    PC_id[k]  = -1
#end For

for m in range(nFace):
    Pobject = geompy.MakeCDG(FaceIDs[m])
    Pt = geompy.PointCoordinates(Pobject)
    for k in range(nweld):
        dist=dist3D(Pt, Face_PC[k])
	if(dist < PC_min[k]):
	   PC_min[k]=dist
           PC_id[k]=m
    
    dist=dist3D(Pt, A1_FaceMid)
    if(dist < A1F_min):
       A1F_min=dist
       A1F_id=m
    
    dist=dist3D(Pt, A2_FaceMid)
    if(dist < A2F_min):
       A2F_min=dist
       A2F_id=m

    dist=dist3D(Pt, A3_FaceMid)
    if(dist < A3F_min):
       A3F_min=dist
       A3F_id=m
       
    dist=dist3D(Pt, B1_FaceMid)
    if(dist < B1F_min):
       B1F_min=dist
       B1F_id=m
       
    dist=dist3D(Pt, B2_FaceMid)
    if(dist < B2F_min):
       B2F_min=dist
       B2F_id=m
       
    dist=dist3D(Pt, B3_FaceMid)
    if(dist < B3F_min):
       B3F_min=dist
       B3F_id=m
#End for    

if(A1F_min > sv or A1F_id == -1):
   print "***Error = ", A1F_min
if(A2F_min > sv or A2F_id == -1):
   print "***Error = ", A2F_min
if(A3F_min > sv or A3F_id == -1):
   print "***Error = ", A2F_min
   
if(B1F_min > sv or B1F_id == -1):
   print "***Error = ", B1F_min
if(B2F_min > sv or B2F_id == -1):
   print "***Error = ", B2F_min
if(B3F_min > sv or B3F_id == -1):
   print "***Error = ", B3F_min   
WP = [ [] ]*(nweld+1)
for k in range(nweld):
    if(PC_min[k] > (1000.0*sv) or PC_id[k] == -1):
       print "***Error in pass id = ", k, ",", PC_min[k]
    print "weld pass center, PC_id = ", PC_id[k]
    geomObj_yy = geompy.GetInPlace(Fuse_1, FaceIDs[PC_id[k]], True)
    [geomObj_yp] = geompy.SubShapeAll(geomObj_yy, geompy.ShapeType["FACE"])
    FetchID = geompy.GetSameIDs(Fuse_1, geomObj_yp)
    WP[k+1] = geompy.CreateGroup(Fuse_1, geompy.ShapeType["FACE"])
    geompy.UnionIDs(WP[k+1], FetchID)
    geompy.addToStudyInFather( Fuse_1, WP[k+1], 'WP' + str(k+1) ) 
#end for   

print "A1F_id = ", A1F_id
geomObj_yy = geompy.GetInPlace(Fuse_1, FaceIDs[A1F_id], True)
[geomObj_yp] = geompy.SubShapeAll(geomObj_yy, geompy.ShapeType["FACE"])
FetchID = geompy.GetSameIDs(Fuse_1, geomObj_yp)

PA1 = geompy.CreateGroup(Fuse_1, geompy.ShapeType["FACE"])
geompy.UnionIDs(PA1, FetchID)
geompy.addToStudyInFather( Fuse_1, PA1, 'PA1' )

print "A2F_id = ", A2F_id
geomObj_yy = geompy.GetInPlace(Fuse_1, FaceIDs[A2F_id], True)
[geomObj_yp] = geompy.SubShapeAll(geomObj_yy, geompy.ShapeType["FACE"])
FetchID = geompy.GetSameIDs(Fuse_1, geomObj_yp)

PA2 = geompy.CreateGroup(Fuse_1, geompy.ShapeType["FACE"])
geompy.UnionIDs(PA2, FetchID)
geompy.addToStudyInFather( Fuse_1, PA2, 'PA2' )

print "A3F_id = ", A3F_id
geomObj_yy = geompy.GetInPlace(Fuse_1, FaceIDs[A3F_id], True)
[geomObj_yp] = geompy.SubShapeAll(geomObj_yy, geompy.ShapeType["FACE"])
FetchID = geompy.GetSameIDs(Fuse_1, geomObj_yp)

PA3 = geompy.CreateGroup(Fuse_1, geompy.ShapeType["FACE"])
geompy.UnionIDs(PA3, FetchID)
geompy.addToStudyInFather( Fuse_1, PA3, 'PA3' )

print "B3F_id = ", B3F_id
geomObj_yy = geompy.GetInPlace(Fuse_1, FaceIDs[B3F_id], True)
[geomObj_yp] = geompy.SubShapeAll(geomObj_yy, geompy.ShapeType["FACE"])
FetchID = geompy.GetSameIDs(Fuse_1, geomObj_yp)

PB3 = geompy.CreateGroup(Fuse_1, geompy.ShapeType["FACE"])
geompy.UnionIDs(PB3, FetchID)
geompy.addToStudyInFather( Fuse_1, PB3, 'PB3' )

print "B2F_id = ", B2F_id
geomObj_yy = geompy.GetInPlace(Fuse_1, FaceIDs[B2F_id], True)
[geomObj_yp] = geompy.SubShapeAll(geomObj_yy, geompy.ShapeType["FACE"])
FetchID = geompy.GetSameIDs(Fuse_1, geomObj_yp)

PB2 = geompy.CreateGroup(Fuse_1, geompy.ShapeType["FACE"])
geompy.UnionIDs(PB2, FetchID)
geompy.addToStudyInFather( Fuse_1, PB2, 'PB2' )

print "B1F_id = ", B1F_id
geomObj_yy = geompy.GetInPlace(Fuse_1, FaceIDs[B1F_id], True)
[geomObj_yp] = geompy.SubShapeAll(geomObj_yy, geompy.ShapeType["FACE"])
FetchID = geompy.GetSameIDs(Fuse_1, geomObj_yp)

PB1 = geompy.CreateGroup(Fuse_1, geompy.ShapeType["FACE"])
geompy.UnionIDs(PB1, FetchID)
geompy.addToStudyInFather( Fuse_1, PB1, 'PB1' )

Group_HAZ = geompy.CreateGroup(Fuse_1, geompy.ShapeType["FACE"])
geompy.UnionList(Group_HAZ, [PA3, PB3])
geompy.addToStudyInFather( Fuse_1, Group_HAZ, 'Group_HAZ' )

Group_Ext = geompy.CreateGroup(Fuse_1, geompy.ShapeType["FACE"])
geompy.UnionList(Group_Ext, [PA2, PB2])
geompy.addToStudyInFather( Fuse_1, Group_Ext, 'Group_Ext' )

###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New(theStudy)
Mesh_1 = smesh.Mesh(Fuse_1)
smesh.SetName(Mesh_1.GetMesh(), 'Mesh_1')

NETGEN_2D = Mesh_1.Triangle(algo=smeshBuilder.NETGEN_1D2D)
NETGEN_2D_Parameters_Global = NETGEN_2D.Parameters()
NETGEN_2D_Parameters_Global.SetMaxSize( gelemaxsize )
NETGEN_2D_Parameters_Global.SetSecondOrder( 0 )
NETGEN_2D_Parameters_Global.SetOptimize( 1 )
NETGEN_2D_Parameters_Global.SetFineness( 2 )
NETGEN_2D_Parameters_Global.SetMinSize( geleminsize )
NETGEN_2D_Parameters_Global.SetUseSurfaceCurvature( 1 )
NETGEN_2D_Parameters_Global.SetFuseEdges( 1 )
NETGEN_2D_Parameters_Global.SetQuadAllowed( 1 )
smesh.SetName(NETGEN_2D.GetAlgorithm(), 'NETGEN_2D')
smesh.SetName(NETGEN_2D_Parameters_Global, 'NETGEN 2D Parameters_Global')

numEleLen = int(length/lwt)
print "Number of elements along traveling direction = ", numEleLen
eleSizeTravel = length/float(numEleLen)
print "Element size along traveling direction = ", eleSizeTravel

Regular_1D_match = Mesh_1.Segment(geom=Edge_match)
Sub_mesh_match = Regular_1D_match.GetSubMesh()
Local_Length_match = Regular_1D_match.NumberOfSegments(numEleLen)
smesh.SetName(Sub_mesh_match, 'Sub_mesh_match')
smesh.SetName(Regular_1D_match.GetAlgorithm(), 'Regular_1D_match')
smesh.SetName(Local_Length_match, 'Local Length_match')

MeshOrder = [Sub_mesh_match]

Regular_1D_3E = Mesh_1.Segment(geom=edge_3E)
Sub_mesh_3E = Regular_1D_3E.GetSubMesh()
Number_of_Segments_3E = Regular_1D_3E.NumberOfSegments(nelethick)
smesh.SetName(Sub_mesh_3E, 'Sub_mesh_3E')
smesh.SetName(Regular_1D_3E.GetAlgorithm(), 'Regular_1D_3E')
smesh.SetName(Number_of_Segments_3E, 'Number of Segments_3E')

MeshOrder.extend([Sub_mesh_3E])

print "Element Size in the weld = ", weldelesize

for k in range(nweld):
    Regular_1D_P = Mesh_1.Segment(geom=WP[k+1])
    Sub_mesh_P = Regular_1D_P.GetSubMesh()
    Local_Length_P = Regular_1D_P.LocalLength(weldelesize,None,1e-007)
    MeshOrder.extend([Sub_mesh_P])
    smesh.SetName(Sub_mesh_P, 'Sub_mesh_P' + str(k+1) )
#end for

Regular_1D_HAZ = Mesh_1.Segment(geom=Group_HAZ)
Sub_mesh_HAZ = Regular_1D_HAZ.GetSubMesh()
Local_Length_HAZ = Regular_1D_HAZ.LocalLength(hazelesize,None,1e-007)
smesh.SetName(Sub_mesh_HAZ, 'Sub_mesh_HAZ' )

print "Element Size in the HAZ = ", hazelesize

MeshOrder.extend([Sub_mesh_HAZ])

Regular_1D_Ext = Mesh_1.Segment(geom=Group_Ext)
Sub_mesh_Ext = Regular_1D_Ext.GetSubMesh()
Local_Length_Ext = Regular_1D_Ext.LocalLength(extelesize,None,1e-007)

print "Element Size in the Ext = ", extelesize
MeshOrder.extend([Sub_mesh_Ext])

isDone = Mesh_1.SetMeshOrder( [MeshOrder])

isDone = Mesh_1.Compute()

## Set names of Mesh objects

PA1_1 = Mesh_1.GroupOnGeom(PA1,'PA1',SMESH.FACE)
PA2_1 = Mesh_1.GroupOnGeom(PA2,'PA2',SMESH.FACE)
PA3_1 = Mesh_1.GroupOnGeom(PA3,'PA3',SMESH.FACE)
PB3_1 = Mesh_1.GroupOnGeom(PB3,'PB3',SMESH.FACE)
PB2_1 = Mesh_1.GroupOnGeom(PB2,'PB2',SMESH.FACE)
PB1_1 = Mesh_1.GroupOnGeom(PB1,'PB1',SMESH.FACE)

#smesh.SetName(PA1_1, 'PA1')
#smesh.SetName(PA2_1, 'PA2')
#smesh.SetName(PA3_1, 'PA3')
#smesh.SetName(PB1_1, 'PB1')
#smesh.SetName(PB2_1, 'PB2')
#smesh.SetName(PB3_1, 'PB3')

print "Number of elements through thickness = ", nelethick
eleSizeThick = thick/float(nelethick)
print "Element Size through thickness = ", eleSizeThick

[ PA1_extruded, PA1_top ] = Mesh_1.ExtrusionSweepObjects( [], [], [ PA1_1 ], [ 0, -eleSizeThick, 0 ], nelethick, 1 )
[ PB1_extruded, PB1_top ] = Mesh_1.ExtrusionSweepObjects( [], [], [ PB1_1 ], [ 0, -eleSizeThick, 0 ], nelethick, 1 )

[ PA2_extruded, PA2_top ] = Mesh_1.ExtrusionSweepObjects( [], [], [ PA2_1 ], [ 0, 0, -eleSizeTravel ], numEleLen, 1 )
[ PA3_extruded, PA3_top ] = Mesh_1.ExtrusionSweepObjects( [], [], [ PA3_1 ], [ 0, 0, -eleSizeTravel ], numEleLen, 1 )
[ PB3_extruded, PB3_top ] = Mesh_1.ExtrusionSweepObjects( [], [], [ PB3_1 ], [ 0, 0, -eleSizeTravel ], numEleLen, 1 )
[ PB2_extruded, PB2_top ] = Mesh_1.ExtrusionSweepObjects( [], [], [ PB2_1 ], [ 0, 0, -eleSizeTravel ], numEleLen, 1 )

smesh.SetName(PB1_extruded, 'PB1_extruded')
smesh.SetName(PB2_extruded, 'PB2_extruded')
smesh.SetName(PB3_extruded, 'PB3_extruded')
smesh.SetName(PA3_extruded, 'PA3_extruded')
smesh.SetName(PA2_extruded, 'PA2_extruded')
smesh.SetName(PA1_extruded, 'PA1_extruded')

#smesh.SetName(PA1_top, 'PA1_top')
#smesh.SetName(PA2_top, 'PA2_top')
#smesh.SetName(PA3_top, 'PA3_top')
#smesh.SetName(PB1_top, 'PB1_top')
#smesh.SetName(PB2_top, 'PB2_top')
#smesh.SetName(PB3_top, 'PB3_top')

# Create a group of faces that are located on the top plane for the convective/film
aCriteria = []
aCriterion = smesh.GetCriterion(SMESH.FACE,SMESH.FT_BelongToPlane,SMESH.FT_Undefined,
                                'coolingPlane')
aCriteria.append(aCriterion)
aFilter_1 = smesh.GetFilterFromCriteria(aCriteria)
aFilter_1.SetMesh(Mesh_1.GetMesh())
FilmSurface = Mesh_1.GroupOnFilter( SMESH.FACE, 'FilmSurface', aFilter_1 )
smesh.SetName(FilmSurface, 'FilmSurface')


groupAll = [ PA1_1, PA2_1, PA3_1, PB3_1, PB2_1, PB1_1, PA2_extruded, PA2_top, PA3_extruded, PA3_top, PB3_extruded, PB3_top, PB2_extruded, PB2_top, PB1_extruded, PB1_top, PA1_extruded, PA1_top ]

for k in range(nweld):
    WC='WP'+ str(k+1)
    WD='WP'+ str(k+1) + '_1'
    WE='WP'+ str(k+1) + '_extruded'
    WT='WP'+ str(k+1) + '_top'
    
    WD = Mesh_1.GroupOnGeom(WP[k+1],'WP' + str(k+1),SMESH.FACE)
    smesh.SetName(WD, 'WP' + str(k+1) )
    [ WE, WT ] = Mesh_1.ExtrusionSweepObjects( [], [], [ WD ], [ 0, 0, -eleSizeTravel ], numEleLen, 1 )
    smesh.SetName(WE, 'WP'+ str(k+1) + '_extruded')
    smesh.SetName(WT, 'WP'+ str(k+1) + '_top')

for k in range(nweld):   
    WPt = Mesh_1.GroupOnGeom(WP[k+1],'WP' + str(k+1) +'ST',SMESH.NODE)

# Group_face = Mesh_1.CreateEmptyGroup( SMESH.FACE, 'Group_face' )
# nbAdd = Group_face.AddFrom( Mesh_1.GetMesh() )
# #Group_face.Clear()
# Group_face_ElemIDs = Group_face.GetListOfID()
# print len(Group_face_ElemIDs)
# for i in range(len(Group_face_ElemIDs)+1):
#     ele= Group_face.GetID(i)
#     Mesh_1.RemoveElements([ele])

Group_edge = Mesh_1.CreateEmptyGroup( SMESH.EDGE, 'Group_edge' )
nbAdd = Group_edge.AddFrom( Mesh_1.GetMesh() )
#Group_edge.Clear()
Group_edge_ElemIDs = Group_edge.GetListOfID()
print len(Group_edge_ElemIDs)
for i in range(len(Group_edge_ElemIDs)+1):
    ele= Group_edge.GetID(i)
    Mesh_1.RemoveElements([ele])

l_groups =  Mesh_1.GetGroups()
for group in l_groups:
    name = group.GetName()
    if name == "Group_face":
        Mesh_1.RemoveGroup(group)
    if name == "Group_edge":
        Mesh_1.RemoveGroup(group)
    if name == "PA1":
        Mesh_1.RemoveGroup(group)
    if name == "PA1_top":
        Mesh_1.RemoveGroup(group)
    if name == "PA2":
        Mesh_1.RemoveGroup(group)
    if name == "PA2_top":
        Mesh_1.RemoveGroup(group)
    if name == "PA3":
        Mesh_1.RemoveGroup(group)
    if name == "PA3_top":
        Mesh_1.RemoveGroup(group)
    if name == "PB1":
        Mesh_1.RemoveGroup(group)
    if name == "PB1_top":
        Mesh_1.RemoveGroup(group)
    if name == "PB2":
        Mesh_1.RemoveGroup(group)
    if name == "PB2_top":
        Mesh_1.RemoveGroup(group)
    if name == "PB3":
        Mesh_1.RemoveGroup(group)
    if name == "PB3_top":
        Mesh_1.RemoveGroup(group)
    for k in range(nweld):
        WPC="WP" + str(k+1)
        WPT="WP" + str(k+1) + "_top"
        if name == WPC:
           Mesh_1.RemoveGroup(group)
        if name == WPT:
           Mesh_1.RemoveGroup(group)   
           
coincident_nodes_on_part = Mesh_1.FindCoincidentNodesOnPart( Mesh_1, distmerge, [], 0 )
Mesh_1.MergeNodes(coincident_nodes_on_part, [])

Mesh_1.RenumberNodes()
Mesh_1.RenumberElements()

if os.path.isfile('Mesh_3D_old.unv'):
    os.remove('Mesh_3D_old.unv')
if os.path.isfile('Mesh_3D.unv'):
    os.rename('Mesh_3D.unv', 'Mesh_3D_old.unv')
try:
  Mesh_1.ExportUNV( os.path.join(out_dir,'Mesh_3D.unv' ))
except:
  print 'ExportUNV() failed. Invalid file name?'
