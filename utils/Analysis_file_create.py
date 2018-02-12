##################################################################
#
#   Analysis file creation, Version 1.000 
#   technical contact: yyang@ewi.org;yupyang@gmail.com 
#
##################################################################
#
import os
import os.path
import shutil
from math import *
import argparse
import data_IO
from calculix import calculix_utils as cu

cwd=os.getcwd() 



##------------------------------------------------------------------
#
# read eweld.in
#
##-------------------------------------------------------------------
def read_eweld_in(eweld_file, logfile):

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
    #endif
    
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
    numWeld=nweld
    return numWeld,myMaterial1,myMaterial2,FillerMaterial
#enddef
##------------------------------------------------------------------
#
# read eweld_boundary_condition.in
#
##-------------------------------------------------------------------
def read_bc_in(bc_file, logfile):

    fix_dir = [[[],]*3]*100
    fix_cod = [[[],]*3]*100

    filein = open(bc_file, "r" )
    lines = filein.readlines()

    textLine = lines[1]
    numfix = int(lines[1])
    logfile.write("Number of fixed point = " + str(numfix) +'\n')  

    for k in range(numfix):
        textLine = lines[k+3]
        dataline = textLine.split( ',' )  
        (xt,yt,zt,fx,fy,fz)=map(float,dataline)
        fix_cod[k]=[xt,yt,zt]
	logfile.write("Fix pt = " + str(k) + "," +  str(fix_cod[k][0]) + "," + str(fix_cod[k][1]) + "," + str(fix_cod[k][2]) +'\n')

        fix_dir[k]=[fx,fy,fz]             
        logfile.write("Fix pt = " + str(k)+ "," + str(fix_dir[k][0]) + "," + str(fix_dir[k][1]) + "," + str(fix_dir[k][2]) +'\n')
    #endif
    filein.close()
    return numfix,fix_cod,fix_dir
#enddef
##------------------------------------------------------------------
#
# read eweld_boundary_condition.in
#
##-------------------------------------------------------------------
def read_ini_in(ini_file, logfile):

    filein = open(ini_file, "r" )
    lines = filein.readlines()

    textLine = lines[2]
    preheat = int(lines[2])
    logfile.write("Preheat = " + str(preheat) +'\n')  
    
    textLine = lines[4]
    interpass = int(lines[4])
    logfile.write("Interpass = " + str(interpass) +'\n')
    
    filein.close()
    return preheat,interpass
#enddef
##------------------------------------------------------------------
#
# read user setting
#
##-------------------------------------------------------------------
#
def read_input(setfile):
    filein = open( setfile, "r" )

    text = filein.readline()
    text = filein.readline()
    model_node = text.strip()

    text = filein.readline()
    text = filein.readline()
    model_ele_t = text.strip()

    text = filein.readline()
    text = filein.readline()
    model_ele_s = text.strip()

    text = filein.readline()
    text = filein.readline()
    model_group = text.strip()

    text = filein.readline()
    text = filein.readline()
    model_film = text.strip()

    text = filein.readline()
    text = filein.readline()
    model_bod= text.strip()

    text = filein.readline()
    text = filein.readline()
    model_mat= text.strip()

    text = filein.readline()
    text = filein.readline()
    model_therm = text.strip()

    text = filein.readline()
    text = filein.readline()
    model_mech= text.strip()

    text = filein.readline()
    text = filein.readline()
    numWeld= int(text.strip())

    cooltime=[[],]*numWeld
    power=[[],]*numWeld
    speed=[[],]*numWeld
    eff=[[],]*numWeld
    thold=[[],]*numWeld         
    weldpass=[[],]*numWeld 	
    numCe=[[],]*numWeld
    text = filein.readline()
    for i in range(numWeld):
        text = filein.readline()
        dataline = text.split( ',' ) 
        weldpass[i]=dataline[1].strip()
        numCe[i]=int(dataline[2].strip())
	cooltime[i]=dataline[3].strip()    
    	power[i]=dataline[4].strip()
	speed[i]=dataline[5].strip()
	eff[i]=dataline[6].strip()
	thold[i]=dataline[7].strip()
	print i,weldpass[i],power[i],speed[i],eff[i]

    filein.close()
    return numWeld,cooltime,power,speed,eff,thold,weldpass,numCe,model_node,model_ele_t,model_ele_s,model_group,model_film,model_bod,model_mat,model_therm,model_mech
#
##------------------------------------------------------------------
#
# read nodes
#
##-------------------------------------------------------------------
#
def read_coordinate_pre(maxn,inp_fname, logfile):
    logfile.write('Read Node coordinate' +'\n')
    finp = data_IO.open_file(inp_fname)
    # loop through the file until EOF is reached
    numNode = 0
    ndidmax=0
    while ( 1 ):
        text = finp.readline()
        # EOF
        if not text:
            break

        # upper case
        textUpper = (text.strip()).upper()

        # *NODE line
        if( textUpper.startswith('*NODE') ):
               for iii in range(maxn):
	           text = finp.readline()
                   textUpper = (text.strip()).upper()
		   if(textUpper.startswith('**')): break
		   if(textUpper.startswith('*ELEMENT')): break
                   dataline = text.split( ',' )     
		   (nt,xt,yt,zt)=map(float,dataline)    
                   ndid=int(nt)
                   if(ndid > ndidmax): ndidmax=ndid 
                   numNode += 1	       
               break           
    # end while
    finp.close()

    # check whether the Job file is processed properly
    if (numNode > 0):
        print( "Nodes have been successfully read!")
    else:
        print( "Error: No nodes found in the job file!")
        return 1
        
    return numNode,ndidmax
#
##-----------
#
def read_coordinate(maxn,inp_fname, logfile, ndidmax,num_node):
    logfile.write('Read Node coordinate' +'\n')

    nd_id= [[[],]*1]*(ndidmax+1)
    nd_cod=[[[],]*3]*(ndidmax+1)

    finp = open( inp_fname, 'r' )
    # loop through the file until EOF is reached
    numNode = 0
    while ( 1 ):
        text = finp.readline()
        # EOF
        if not text:
            break
        #end if

        # upper case
        textUpper = (text.strip()).upper()

        # *NODE line
        if( textUpper.startswith('*NODE') ):
               for iii in range(maxn):
	           text = finp.readline()
                   textUpper = (text.strip()).upper()
		   if(textUpper.startswith('**')): break
		   if(textUpper.startswith('*ELEMENT')): break
                   numNode += 1	       
	           dataline = text.split( ',' )     
	           (nt,xt,yt,zt)=map(float,dataline)    
                   nd_id[iii]=int(nt)
                   nd_cod[nd_id[iii]]=[xt,yt,zt]
                   #print nd_id[iii], nd_cod[iii]
               break           
    # end while
    finp.close()

    # check whether the Job file is processed properly
    if (numNode==num_node):
        print( "Nodes have been successfully read!")
    else:
        print( "Error: No nodes found in the job file!")
        return 1
        
    return numNode,nd_id,nd_cod
#
##------------------------------------------------------------------
#
# read elements
#
##-------------------------------------------------------------------
#
def read_element_pre(maxn,inp_fname,out_fname, logfile):
    logfile.write('Read Element' +'\n')       
    finp = open( inp_fname, 'r' )
    outf = open( out_fname, 'w' )
    # loop through the file until EOF is reached
    numEle = 0
    eleidmax=0
    while ( 1 ):
        text = finp.readline()
        # EOF
        if not text:
            break
        #end if

        # upper case
        textUpper = (text.strip()).upper()

        # *Element line
        if( textUpper.startswith('*ELEMENT') ):
               outf.write(text.strip() +'\n')
               for iii in range(maxn):
	           text = finp.readline().strip()
                   textUpper = (text.strip()).upper() 
                                      
                   if(textUpper.startswith('*ELEMENT')==True): 
                      outf.write(text.strip() +'\n')
		   
		   if(textUpper.startswith('*SYSTEM')): 
		      break
		   elif(textUpper.startswith('*NSET')): 
		      break
		   elif(textUpper.startswith('*ELSET')): 
		      break
		   elif(textUpper.startswith('**')): 
		      outf.write(text.strip() +'\n')		      
		   elif(textUpper.startswith('*ELEMENT')==False):            	              
                      text = text.rstrip(',')
   	              dataline = text.split( ',' )     
                      outf.write(text.strip() +'\n')
  	              if(len(dataline)==9):  	                  	                 
                         numEle += 1			  		         
		         eleid=int(dataline[0])
		         if(eleid > eleidmax): eleidmax=eleid 
 		      elif(len(dataline)==7):
                         numEle += 1			  		         
		         eleid=int(dataline[0])
		         if(eleid > eleidmax): eleidmax=eleid	         
		      elif(len(dataline)==5):
                         numEle += 1
                         eleid=int(dataline[0])
		         if(eleid > eleidmax): eleidmax=eleid 	              
  	              elif(len(dataline)==4):
                         numEle += 1			  		         
		         eleid=int(dataline[0])
			 if(eleid > eleidmax): eleidmax=eleid
		      else:
                         eleid=int(dataline[6])
                         logfile.write(str(len(dataline)) +'\n')
                         logfile.write(str(dataline) +'\n')
                         logfile.write(str(eleid) +'\n')  		         
  		         logfile.write("***ERROR***, in reading global element" +'\n')
                      #print numEle, ele[ele_id[numEle-1]]
               break           
    # end while
    finp.close()
    outf.close()
    
    # check whether the Job file is processed properly
    if (numEle > 0):
        print "Elements have been successfully read!"  
    else:
        print "Error: No elements found in the job file!"
        return 1
        
    return numEle,eleidmax
#
##-----------
#
def read_element(maxn,inp_fname, logfile, eleidmax, num_ele):

    logfile.write('Read Element' +'\n')

    ele_id=[[[],]*1]*(eleidmax+1)
    eletype=[[[],]*1]*(eleidmax+1)

    ele=[[],]*(eleidmax+1)
    for i in range(eleidmax):
        ele[i]=[[],]*8

    finp = open( inp_fname, 'r' )
    # loop through the file until EOF is reached
    numEle = 0
    while ( 1 ):
        text = finp.readline()
        # EOF
        if not text:
            break
        #end if

        # upper case
        textUpper = (text.strip()).upper()

        # *Element line
        if( textUpper.startswith('*ELEMENT') ):
               for iii in range(maxn):
	           text = finp.readline().strip()
                   textUpper = (text.strip()).upper()
		   if(textUpper.startswith('*SYSTEM')): 
		      break
		   elif(textUpper.startswith('*NSET')): 
		      break
		   elif(textUpper.startswith('*ELSET')): 
		      break
		   elif(textUpper.startswith('**')): 
		      icontinue=1
		   elif(textUpper.startswith('*ELEMENT')==False):       
   	              #print text
	              text = text.rstrip(',')   	              
   	              dataline = text.split( ',' )     
		      #print int(dataline[1]),int(dataline[2])   
  	              if(len(dataline)==9):  	                 
                         numEle += 1			  		         
		         ele_id[numEle-1]=int(dataline[0])
		         eletype[ele_id[numEle-1]]=8
		         ele[ele_id[numEle-1]]=[int(dataline[1]),int(dataline[2]),int(dataline[3]),int(dataline[4]),int(dataline[5]),int(dataline[6]),int(dataline[7]),int(dataline[8])]
  	              elif(len(dataline)==7):
                         numEle += 1			  		         
		         ele_id[numEle-1]=int(dataline[0])
		         eletype[ele_id[numEle-1]]=6
		         ele[ele_id[numEle-1]]=[int(dataline[1]),int(dataline[2]),int(dataline[3]),int(dataline[4]),int(dataline[5]),int(dataline[6]),0,0]	         
		      elif(len(dataline)==5):
                         numEle += 1
                         ele_id[numEle-1]=int(dataline[0])
		         eletype[ele_id[numEle-1]]=4
		         ele[ele_id[numEle-1]]=[int(dataline[1]),int(dataline[2]),int(dataline[3]),int(dataline[4])]  	              
  	              elif(len(dataline)==4):
                         numEle += 1			  		         
		         ele_id[numEle-1]=int(dataline[0])
		         eletype[ele_id[numEle-1]]=3
		         ele[ele_id[numEle-1]]=[int(dataline[1]),int(dataline[2]),int(dataline[3]),0]
		      else:
                         logfile.write(str(dataline) +'\n')
  		         logfile.write("***ERROR***, in reading global element" +'\n')
                      #print numEle, ele[ele_id[numEle-1]]
               break           
    # end while
    finp.close()

    # check whether the Job file is processed properly
    if (numEle==num_ele):
        print("Elements have been successfully read!")
    else:
        print( "Error: No elements found in the job file!")
        return 1
        
    return numEle,ele_id,eletype,ele
#
##------------------------------------------------------------------
#
# read Film
#
##-------------------------------------------------------------------
#
def read_film(maxn,inp_fname,out_fname, logfile):
    logfile.write('Read Film' +'\n')       
    finp = open( inp_fname, 'r' )
    outf = open( out_fname, 'w' )
    # loop through the file until EOF is reached
    numFilm = 0
    while ( 1 ):
        text = finp.readline()
        # EOF
        if not text:
            break
        #end if

        # upper case
        textUpper = (text.strip()).upper()

        # *Element line
        if( textUpper.startswith('*FILM') ):
               #outf.write(text.strip() +'\n')
               for iii in range(maxn):
	           text = finp.readline()
                   textUpper = (text.strip()).upper()
		   if(textUpper.startswith('*END')): 
		      break
		   elif(textUpper.startswith('**')): 
		      break
		   else:         
                      numFilm += 1	                   
                   outf.write(text.strip() +'\n')
               break           
    # end while
    finp.close()
    outf.close()
    
    # check whether the Job file is processed properly
    if (numFilm > 0):
        print "Film have been successfully read!"  
    else:
        print "Error: No Film found in the job file!"
        return 1
        
    return numFilm
#
#
##------------------------------------------------------------------
#
# read group
#
##-------------------------------------------------------------------
#
def create_group(maxn,inp_fname,out_fname, logfile):
    logfile.write('Read group' +'\n')       
    finp = open( inp_fname, 'r' )
    outf = open( out_fname, 'w' )
    # loop through the file until EOF is reached
    numgroup = 0
    while ( 1 ):
        text = finp.readline()
        # EOF
        if not text:
            break

        # upper case
        textUpper = (text.strip()).upper()

        # *Element line
        if( textUpper.startswith('*NSET') ):
               outf.write(text.strip() +'\n')
               for iii in range(maxn):
                   text = finp.readline()
                   if text == '':
                       break
                   textUpper = (text.strip()).upper()
                   if(textUpper.startswith('*STEP')):
                       break
                   else:
                       numgroup += 1
                       outf.write(text.strip() +'\n')

        elif( textUpper.startswith('*ELSET') ):
            outf.write(text.strip() +'\n')
            for iii in range(maxn):
                text = finp.readline()
                if text == '':
                    break
                textUpper = (text.strip()).upper()
                if(textUpper.startswith('*STEP')):
                    break
                else:
                    numgroup += 1
                    outf.write(text.strip() +'\n')

    finp.close()
    outf.close()
    
    # check whether the Job file is processed properly
    if (numgroup > 0):
        print "Group have been successfully read!"  
    else:
        print "Error: No group found in the job file!"
        return 1
        
    return numgroup
#
##------------------------------------------------------------------
#
# create model_ele_x.in
#
##-------------------------------------------------------------------
#
def create_elet(inp_fname,out_fname, logfile):
    logfile.write('Read ele_t.in' +'\n')       
    finp = open( inp_fname, 'r' )
    outf = open( out_fname, 'w' )
    # loop through the file until EOF is reached
    while ( 1 ):
        text = finp.readline()
        # EOF
        if not text:
            break
        #end if

        # upper case
        textUpper = (text.strip()).upper()

        # *Element line
        if( textUpper.startswith('*ELEMENT,TYPE=C3D8I') ):
            dataline = text.split( ',' )
            text=dataline[0] + ", TYPE=DC3D8, " + dataline[2]
            outf.write(text.strip() +'\n')
        elif( textUpper.startswith('*ELEMENT,TYPE=C3D8R') ):
            dataline = text.split( ',' )
            text=dataline[0] + ", TYPE=DC3D8, " + dataline[2]
            outf.write(text.strip() +'\n')
        elif( textUpper.startswith('*ELEMENT,TYPE=C3D8') ):
            dataline = text.split( ',' )
            text=dataline[0] + ", TYPE=DC3D8, " + dataline[2]
            outf.write(text.strip() +'\n')            
        elif( textUpper.startswith('*ELEMENT,TYPE=AC3D6') ):
            dataline = text.split( ',' )
            text=dataline[0] + ", TYPE=DC3D6, " + dataline[2]
            outf.write(text.strip() +'\n')                        
        elif( textUpper.startswith('*ELEMENT,TYPE=C3D6') ):
            dataline = text.split( ',' )
            text=dataline[0] + ", TYPE=DC3D6, " + dataline[2]
            outf.write(text.strip() +'\n')                        
        elif( textUpper.startswith('*ELEMENT,TYPE=C3D4') ):
            dataline = text.split( ',' )
            text=dataline[0] + ", TYPE=DC3D4, " + dataline[2]
            outf.write(text.strip() +'\n') 
        elif( textUpper.startswith('*ELEMENT,TYPE=S4') ):
            dataline = text.split( ',' )
            text=dataline[0] + ", TYPE=DS4, " + dataline[2]
            outf.write(text.strip() +'\n')
        elif( textUpper.startswith('*ELEMENT,TYPE=S4R') ):
            dataline = text.split( ',' )
            text=dataline[0] + ", TYPE=DS4, " + dataline[2]
            outf.write(text.strip() +'\n')
        elif( textUpper.startswith('*ELEMENT,TYPE=S3') ):
            dataline = text.split( ',' )
            text=dataline[0] + ", TYPE=DS3, " + dataline[2]
            outf.write(text.strip() +'\n')
        else:
            outf.write(text.strip() +'\n')
    # end while
    finp.close()
    outf.close()
           
    return 0

def create_eles(inp_fname,out_fname, logfile):
    logfile.write('Read ele_t.in' +'\n')       
    finp = open( inp_fname, 'r' )
    outf = open( out_fname, 'w' )
    # loop through the file until EOF is reached
    while ( 1 ):
        text = finp.readline()
        # EOF
        if not text:
            break
        #end if

        # upper case
        textUpper = (text.strip()).upper()

        # *Element line
        if( textUpper.startswith('*ELEMENT,TYPE=C3D8I') ):
            dataline = text.split( ',' )
            text=dataline[0] + ", TYPE=C3D8R, " + dataline[2]
            outf.write(text.strip() +'\n')
        elif( textUpper.startswith('*ELEMENT,TYPE=DC3D8') ):
            dataline = text.split( ',' )
            text=dataline[0] + ", TYPE=C3D8R, " + dataline[2]
            outf.write(text.strip() +'\n')
        elif( textUpper.startswith('*ELEMENT,TYPE=DC3D6') ):
            dataline = text.split( ',' )
            text=dataline[0] + ", TYPE=C3D6, " + dataline[2]
            outf.write(text.strip() +'\n')                        
        elif( textUpper.startswith('*ELEMENT,TYPE=DS4') ):
            dataline = text.split( ',' )
            text=dataline[0] + ", TYPE=S4R, " + dataline[2]
            outf.write(text.strip() +'\n')
        elif( textUpper.startswith('*ELEMENT,TYPE=DS3') ):
            dataline = text.split( ',' )
            text=dataline[0] + ", TYPE=S3, " + dataline[2]
            outf.write(text.strip() +'\n')
        else:
            outf.write(text.strip() +'\n')
    # end while
    finp.close()
    outf.close()
           
    return 0


def output_element_files(out_dir, inp_fname, ele, ele_id, eletype):
    out_c3d8 = data_IO.open_file(os.path.join(out_dir, 'model_ele8.in'), 'w')
    out_c3d6 = data_IO.open_file(os.path.join(out_dir, 'model_ele6.in'), 'w')
    out_s4 = data_IO.open_file(os.path.join(out_dir, 'model_ele4.in'), 'w')

    # inp_fname="ele_temp.in"
    # model_ele_t="model_ele_t.in"
    # out_fname=model_ele_t
    # ttt=create_elet(inp_fname,out_fname)
    # print "model_ele_s.in has been created!"

    # inp_fname="ele_temp.in"
    # model_ele_s="model_ele_s.in"
    # out_fname=model_ele_s
    # ttt=create_eles(inp_fname,out_fname)
    # print "model_ele_s.in has been created!"

    # -----------------------------------------------------------------
    # Read and output group file
    #

    # Create a subset of elements that contain the named element sets only
    mesh = cu.Mesh()
    mesh.read_mesh_from_inp(inp_fname)
    mesh.remove_element_set_by_name('FilmSurface')
    mesh_elements_in_sets = mesh.get_all_elements()
    named_elements = []
    named_element_types = []
    for element in ele_id:
        if element in mesh_elements_in_sets:
            named_elements.append(element)
            named_element_types.append(eletype[element])
    print("len(named_elements): {:d}".format(len(named_elements)))

    # for ie in range(num_ele):
    #     eleIn=ele_id[ie]
    #     nodepe=eletype[eleIn]

    for iElem, eleIn in enumerate(named_elements):
        nodepe = named_element_types[iElem]
        ec = eleIn
        numD = 8
        elemNodesStr = str(eleIn).rjust(numD) + ", " + \
                       ", ".join(str(x).rjust(numD) for x in ele[ec][:nodepe]) + "\n"

        if (nodepe == 8):
            out_c3d8.write(elemNodesStr)

        if (nodepe == 6):
            out_c3d6.write(elemNodesStr)

        if (nodepe == 4):
            out_s4.write(elemNodesStr)

    out_c3d8.close()
    out_c3d6.close()
    out_s4.close()


def determine_cent(numxsym,xsymNode,xfull,yfull):   
    dmin=1.0E7
    for id in range(numxsym):
        node=xsymNode[id]
        x1=nd_cod[node][0]
        y1=nd_cod[node][1]
        x2=xfull
        y2=yfull
        ttt=dist2p(x1,y1,x2,y2)
        if(ttt < dmin): zfixNode=node                                          
    return zfixNode

def dist2p(x1,y1,x2,y2):
    a=x1-x2
    b=y1-y2
    dist2p=sqrt(a*a+b*b)
    return dist2p


def element_cent(eleIn,eletype,ele,nd_cod):
    numNdtheEle=eletype[eleIn]
    cent[0]=0
    cent[1]=0
    cent[2]=0
    for jj in range(numNdtheEle):
        nd=ele[eleIn][jj]
	cent[0]=cent[0]+nd_cod[nd][0]
	cent[1]=cent[1]+nd_cod[nd][1]
	cent[2]=cent[2]+nd_cod[nd][2]	
    elecent[0]=cent[0]/numNdtheEle
    elecent[1]=cent[1]/numNdtheEle  
    elecent[2]=cent[2]/numNdtheEle     
    return elecent
    
def dist3d(x1,y1,z1,x2,y2,z2):
    a=x1-x2
    b=y1-y2
    c=z1-z2
    dist=sqrt(a*a+b*b+c*c)
    return dist
##------------------------------------------------------------------
#
# Create node file
#
##------------------------------------------------------------------- 
def create_node_in(out_fname,num_node,nd_id,nd_cod):
    fout = data_IO.open_file( out_fname, 'w' )
    for iii in range(num_node):    
        node=nd_id[iii]
        [xt,yt,zt]=nd_cod[node]

        fout.write(str(node).rjust(8) + ", " + str(xt).rjust(18)
                   + ", " + str(yt).rjust(18) + ", " + str(zt).rjust(18) + '\n')
    fout.close()
    return 0
##------------------------------------------------------------------
#
# Create bc file
#
##------------------------------------------------------------------- 
def output_bc(out_fname,num_node,nd_id,nd_cod,numfix,fix_cod,fix_dir,nfmin):
    """ Write an input file in CalculiX format to specify the fix nodes on the mesh.

    Given an array of fix point coordinates (fix_cod) and fix directions (fix_dir),
    find the closest mesh nodes to each of the fix points and
    fix that points in the required directions.
    """
    fout = data_IO.open_file( out_fname, 'w' )
    
    for jjj in range(numfix):
        dmin=1.0E10
        [x2,y2,z2]=fix_cod[jjj]
        print jjj,x2,y2,z2
        for iii in range(num_node):    
            node=nd_id[iii]
            [x1,y1,z1]=nd_cod[node]
            dist=dist3d(x1,y1,z1,x2,y2,z2)
            if(dist < dmin): 
               dmin=dist
               nfmin[jjj]=node
               print x1,y1,z1,dmin,node
            #endif
        #endfor    
        fout.write("*NSET,NSET=FIX" + str(jjj) + '\n')
        fout.write(str(nfmin[jjj]) + "," + '\n')
    #endfor
    
    fout.write("*BOUNDARY,OP=NEW \n ")
    
    for jjj in range(numfix):
        if(fix_dir[jjj][0] >0): fout.write("FIX" + str(jjj) + ", 1,1" + '\n')        
        if(fix_dir[jjj][1] >0): fout.write("FIX" + str(jjj) + ", 2,2" + '\n')  
        if(fix_dir[jjj][2] >0): fout.write("FIX" + str(jjj) + ", 3,3" + '\n')  
    #endfor
    fout.close()
    return 0

def output_therm(inp_fname):
    out_structure = open(inp_fname, 'w' ) 
    text = '*HEADING '
    out_structure.write(str(text) + '\n')   
    text = ' Thermal Analysis'
    out_structure.write(str(text) + '\n')  
    text = '*PREPRINT, MODEL=YES, ECHO=NO, HISTORY=YES'
    out_structure.write(str(text) + '\n')  
    text = '*NODE, SYSTEM=R,NSET=ALLND,INPUT=model_node.in'
    out_structure.write(str(text) + '\n')  
    text = '*INCLUDE,INPUT=model_ele_c3d8.in'
    out_structure.write(str(text) + '\n') 
    text = '*INCLUDE,INPUT=model_ele_c3d6.in'
    out_structure.write(str(text) + '\n') 
    text = '*INCLUDE,INPUT=model_ele_s4.in'
    out_structure.write(str(text) + '\n')  
    text = '*INCLUDE,INPUT=model_group.in'
    out_structure.write(str(text) + '\n')
    text = '*****************************************'
    out_structure.write(str(text) + '\n')

    return 0

def output_mech(inp_fname):
    out_structure = open(inp_fname, 'w' ) 
    text = '*HEADING '
    out_structure.write(str(text) + '\n')   
    text = ' Mechanical Analysis'
    out_structure.write(str(text) + '\n')  
    text = '*PREPRINT, MODEL=YES, ECHO=NO, HISTORY=YES'
    out_structure.write(str(text) + '\n')  
    text = '*NODE, SYSTEM=R,NSET=ALLND,INPUT=model_node.in'
    out_structure.write(str(text) + '\n')  
    text = '*INCLUDE,INPUT=model_ele_c3d8.in'
    out_structure.write(str(text) + '\n') 
    text = '*INCLUDE,INPUT=model_ele_c3d6.in'
    out_structure.write(str(text) + '\n') 
    text = '*INCLUDE,INPUT=model_ele_s4.in'
    out_structure.write(str(text) + '\n')  
    text = '*INCLUDE,INPUT=model_group.in'
    out_structure.write(str(text) + '\n')
    text = '*****************************************'
    out_structure.write(str(text) + '\n')

    return 0

##------------------------------------##                
def output10_perline(fout,media_film):
    
    numD=8
    numES=len(media_film)

    k = 0
    while media_film[k] != -1:    
        
        first = str(media_film[k])    
        
        k = k + 1    
        if(k > (numES-1)): 
           fout.write(str(first.rjust(numD)) + '\n')
           break
        second = str(media_film[k])    
        
        k = k + 1   
        if(k > (numES-1)): 
           fout.write( str(first.rjust(numD)) + ',' +  str(second.rjust(numD)) + '\n')
           break
        third = str(media_film[k])    

        k = k + 1   
        if(k > (numES-1)): 
           fout.write( str(first.rjust(numD)) + ',' +  str(second.rjust(numD)) + ',' + str(third.rjust(numD)) + '\n')
           break
        fouth = str(media_film[k])

        k = k + 1   
        if(k > (numES-1)): 
           fout.write( str(first.rjust(numD)) + ',' +  str(second.rjust(numD)) + ',' + str(third.rjust(numD)) + ',' + str(fouth.rjust(numD)) + '\n')
           break
        fifth = str(media_film[k])
        
        k = k + 1 
        if(k > (numES-1)): 
           fout.write( str(first.rjust(numD)) + ',' +  str(second.rjust(numD)) + ',' + str(third.rjust(numD)) + ',' + str(fouth.rjust(numD)) + ',' + str(fifth.rjust(numD)) + '\n')
           break
        sixth = str(media_film[k])
        
        k = k + 1 
        if(k > (numES-1)): 
           fout.write( str(first.rjust(numD)) + ',' +  str(second.rjust(numD)) + ',' + str(third.rjust(numD)) + ',' + str(fouth.rjust(numD)) + ',' + str(fifth.rjust(numD)) + ',' + str(sixth.rjust(numD)) + '\n')
           break
        seventh = str(media_film[k])
        
        k = k + 1 
        if(k > (numES-1)): 
           fout.write( str(first.rjust(numD)) + ',' +  str(second.rjust(numD)) + ',' + str(third.rjust(numD)) + ',' + str(fouth.rjust(numD)) + ',' + str(fifth.rjust(numD)) + ',' + str(sixth.rjust(numD)) + ',' + str(seventh.rjust(numD)) + '\n')
           break        
        eighth = str(media_film[k])
        
        k = k + 1 
        if(k > (numES-1)): 
           fout.write( str(first.rjust(numD)) + ',' +  str(second.rjust(numD)) + ',' + str(third.rjust(numD)) + ',' + str(fouth.rjust(numD)) + ',' + str(fifth.rjust(numD)) + ',' + str(sixth.rjust(numD)) + ',' + str(seventh.rjust(numD)) + ',' + str(eighth.rjust(numD)) + '\n')
           break         
        nineth = str(media_film[k])
        
        k = k + 1 
        if(k > (numES-1)): 
           fout.write( str(first.rjust(numD)) + ',' +  str(second.rjust(numD)) + ',' + str(third.rjust(numD)) + ',' + str(fouth.rjust(numD)) + ',' + str(fifth.rjust(numD)) + ',' + str(sixth.rjust(numD)) + ',' + str(seventh.rjust(numD)) + ',' + str(eighth.rjust(numD)) + ',' + str(nineth.rjust(numD)) + '\n')
           break        
        tenth = str(media_film[k])
        
        k = k + 1 
        if(k > (numES-1)): 
           fout.write( str(first.rjust(numD)) + ',' +  str(second.rjust(numD)) + ',' + str(third.rjust(numD)) + ',' + str(fouth.rjust(numD)) + ',' + str(fifth.rjust(numD)) + ',' + str(sixth.rjust(numD)) + ',' + str(seventh.rjust(numD)) + ',' + str(eighth.rjust(numD)) + ',' + str(nineth.rjust(numD)) + ',' + str(tenth.rjust(numD)) + '\n')
           break

        
        fout.write( str(first.rjust(numD)) + ',' +  str(second.rjust(numD)) + ',' + str(third.rjust(numD)) + ',' + str(fouth.rjust(numD)) + ',' + str(fifth.rjust(numD)) + ',' + str(sixth.rjust(numD)) + ',' + str(seventh.rjust(numD)) + ',' + str(eighth.rjust(numD)) + ',' + str(nineth.rjust(numD)) + ',' + str(tenth.rjust(numD)) + '\n')

    last = media_film[-1]
    
    return 0
##------------------------------------------------------------------
#
# Create file
#
##------------------------------------------------------------------- 
def read_pass_ele(maxn,inp_fname,phase):       
    vp=[[],]
    phase = phase.upper()
    # print "phase = ", phase
    uphase = (phase.strip()).upper()

    finp = open( inp_fname, 'r' )
    # loop through the file until EOF is reached
    numvp = 0
    while ( 1 ):
        text = finp.readline()
        # EOF
        if not text:
            break

        # upper case
        textUpper = (text.strip()).upper()

        # *Element line
        if(textUpper.startswith(uphase) ):
            for iii in range(maxn):
                text = finp.readline()
                textUpper = (text.strip()).upper()
                if(textUpper.startswith('*SURFACE')):
                    break
                elif(textUpper.startswith('*NSET')):
                    break
                elif(textUpper.startswith('*ELSET')):
                    break
                elif(textUpper.startswith('**')):
                    break
                else:
                    dataline = (text.strip()).split( ',' )
                    #print int(dataline[1]),int(dataline[2])
                    #print len(dataline)
                    for ie in range(len(dataline)):
                        if(dataline[ie]):
                            if(numvp==0):
                                vp[0]=dataline[ie]
                                numvp += 1
                            else:
                                vp.append(dataline[ie])
                                numvp += 1			  		         
                    break
    # end while
    finp.close()
    
    # check whether the Job file is processed properly
    if (numvp > 0):
        print("weld pass element have been successfully read!")
    else:
        print( "phase = ", phase)
        print( "Error: No weld pass element found in the job file!")
        return 1
        
    return numvp,vp 

def read_pass_dir(inp_fname,phase):       
    finp = open( inp_fname, 'r' )
    # loop through the file until EOF is reached
    numvp = 0
    while ( 1 ):
        text = finp.readline()
        # EOF
        if not text:
            break
        #end if

        # upper case
        textUpper = (text.strip()).upper()
	
	#print "phase = ", phase
        uphase = (phase.strip()).upper()
        
        # *Element line
        if( textUpper.startswith(uphase) ):
	    text = finp.readline()        
            dataline = (text.strip()).split( ',' )     
	    vp=int(dataline[0])
            numvp += 1         			  		         
            break           
    # end while
    finp.close()
    
    # check whether the Job file is processed properly
    if (numvp == 1):
        print ("weld pass element have been successfully read!")
    else:
        print("Error: No weld pass element found in the job file!")
        print("phase = ", phase)
        return 1
        
    return vp 

def read_pass_stop(inp_fname,phase):       
    finp = open( inp_fname, 'r' )
    # loop through the file until EOF is reached
    numvp = 0
    while ( 1 ):
        text = finp.readline()
        # EOF
        if not text:
            break
        #end if

        # upper case
        textUpper = (text.strip()).upper()
	
	#print "phase = ", phase
        uphase = (phase.strip()).upper()
         
        # *Element line
        if( textUpper.startswith(uphase) ):
	    text = finp.readline()        
            dataline = (text.strip()).split( ',' )     
	    vp=int(dataline[0])
            numvp += 1         			  		         
            break           
    # end while
    finp.close()
    
    # check whether the Job file is processed properly
    if (numvp == 1):
        print("weld pass element have been successfully read!")
    else:
        vp=-99999
        
    return vp
   
def output_sequence(out_fname,numWeld,power,speed,eff,thold,numSt,numCe,wpst,wpmv,wpsp,numwp,wp,weldpass):

    out_seq = open(out_fname, 'w' ) 
    
    text = '*NUMBER_OF_WELD'
    out_seq.write(str(text) + '\n')
    
    text = str(numWeld) + ","
    out_seq.write(str(text) + '\n')    
    
    for i in range(numWeld):
        text = "*WELD ================== " + weldpass[i] + "========================="
        out_seq.write(str(text) + '\n')         
        
        text = "*WELD_PARAMETER (power; speed; arc efficiency; holding time at start)"
        out_seq.write(str(text) + '\n')    

        text = power[i] + "," + speed[i] + "," +  eff[i] + "," +  thold[i]
        out_seq.write(str(text) + '\n')

        text = "*NSET, NSET=" + weldpass[i] + "ST"
        out_seq.write(str(text) + '\n')

        text = str(numSt[i]) + "," + str(numCe[i])
        out_seq.write(str(text) + '\n')

        ttt=output10_perline(out_seq,wpst[i])

        text = "*NSET, NSET=" + weldpass[i] + "MV"
        out_seq.write(str(text) + '\n')

        text = str(wpmv[i]) + ","
        out_seq.write(str(text) + '\n')

        text = "*NSET, NSET=" + weldpass[i] + "SP"
        out_seq.write(str(text) + '\n')

        text = str(wpsp[i]) + ","
        out_seq.write(str(text) + '\n')

     
        text = "*ELSET,ELSET=" + weldpass[i]
        out_seq.write(str(text) + '\n')        

        text = str(numwp[i]) + ", 1.0"
        out_seq.write(str(text) + '\n')

        ttt=output10_perline(out_seq,wp[i])
        
        text = "*END"
        out_seq.write(str(text) + '\n') 
    
    out_seq.close()
    return 0    

def output_material(out_fname,numWeld,myMaterial1,myMaterial2,FillerMaterial):

    out_seq = data_IO.open_file(out_fname, 'w' )
    
    text = '*ELSET,ELSET=MAT1'
    out_seq.write(str(text) + '\n')
    text = ' EPA1_extruded, EPA2_extruded, EPA3_extruded '
    out_seq.write(str(text) + '\n')

    text  = '*ELSET,ELSET=MAT2'
    out_seq.write(str(text) + '\n')
    text = ' EPB1_extruded, EPB2_extruded, EPB3_extruded '
    out_seq.write(str(text) + '\n')    
    
    text = "*ELSET,ELSET=WELD"
    out_seq.write(str(text) + '\n') 
    for i in range(numWeld):    
        text = " EWP" + str(i+1) + "_extruded, "
        if(i==(numWeld-1)): 
           out_seq.write(str(text) + '\n')    
        else:
           out_seq.write(str(text))   
        #endif
    
    text = '*SOLID SECTION,ELSET=MAT1,MATERIAL=' + myMaterial1
    out_seq.write(str(text) + '\n')
    text = '*MATERIAL,NAME=' + myMaterial1
    out_seq.write(str(text) + '\n')
    text = '*INCLUDE,INPUT=' + 'material/Material_' + myMaterial1 + '.in'
    #text = '*INCLUDE,INPUT=Material_' + myMaterial1 + '.in'
    out_seq.write(str(text) + '\n')    

    text = '*SOLID SECTION,ELSET=MAT2,MATERIAL=' + myMaterial2
    out_seq.write(str(text) + '\n')
    text = '*MATERIAL,NAME=' + myMaterial2
    out_seq.write(str(text) + '\n')
    text = '*INCLUDE,INPUT=' + 'material/Material_' + myMaterial2 + '.in'
    #text = '*INCLUDE,INPUT=material_' + myMaterial2 + '.in'
    out_seq.write(str(text) + '\n')  

    text = '*SOLID SECTION,ELSET=WELD,MATERIAL=' + FillerMaterial
    out_seq.write(str(text) + '\n')
    text = '*MATERIAL,NAME=' + FillerMaterial
    out_seq.write(str(text) + '\n')
    
    #if os.name == 'posix':
    #   bc_file=cwd + "/inputs/eweld_boundary_condition.in"       
    #elif os.name == 'nt':
    #   bc_file=cwd + "/inputs/eweld_boundary_condition.in" 
    #endif
    
    text = '*INCLUDE,INPUT=' + 'material/Material_' + FillerMaterial + '.in'
    #text = '*INCLUDE,INPUT=Material_' + FillerMaterial + '.in'
    out_seq.write(str(text) + '\n')  

    out_seq.close()
    return 0       
    
def output_ini(out_fname,preheat,interpass):

    out_seq = data_IO.open_file(out_fname, 'w' )
    
    text = '*INITIAL CONDITIONS,TYPE=TEMPERATURE'
    out_seq.write(str(text) + '\n')
    text = ' Nall, ' + str(preheat)
    out_seq.write(str(text) + '\n') 
    
    out_seq.close()
    return 0



#---------------------------------------------------------------------------
"""
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
main program
"""

def main():

    parser = argparse.ArgumentParser(
        description='Create BC, element, group, init_temperature, material and node '
                    'files for a welding case')

    parser.add_argument("--model_inp_file", default= "./nodesElems.inp",
                        help='The mesh file in .inp format (converted mesh from .unv by '
                             'unical) - default:"./nodesElems.inp"')

    # parser.add_argument("--inputs_dir", default= "./inputs",
    #                     help='The directory that has the eweld.in, '
    #                          'eweld_boundary_condition.in, and '
    #                          'eweld_preheat_interpass_temperature.in files '
    #                          '- default:"./inputs"')

    parser.add_argument("--eweld_file", default="inputs/eweld.in",
                        help='The input file specifying geometry, materials, type, ...'
                             '(default:"./inputs/eweld.in")')

    parser.add_argument("--eweld_BC_file", default="inputs/eweld_boundary_condition.in",
                        help='The input file specifying boundary conditions '
                             '(default:"./inputs/eweld_boundary_condition.in")')

    parser.add_argument("--eweld_preheat_temp_file",
                        default="inputs/eweld_preheat_interpass_temperature.in",
                        help='The input file specifying preheat and interpass '
                             'temperatures '
                             '(default:"./inputs/eweld_preheat_interpass_temperature.in")')


    parser.add_argument("--out_dir", default= "./",
                        help='The output directory - default:"./"')
    parser.add_argument("--log_dir", default= "./",
                        help='The log directory - default:"./"')


    parser.add_argument("--write_node_file", dest='write_node_file',
                        action='store_true',
                        help='If set, the model_node.in will be written - '
                             'by default model_node.in file will not be written.')

    parser.add_argument("--write_element_files", dest='write_element_files',
                        action='store_true',
                        help='If set, the element files will be written  '
                             '(i.e, model_ele4.in, model_ele6.in and model_ele8.in) - '
                             'by default element files will not be written.')

    parser.add_argument("--write_group_file", dest='write_group_file',
                        action='store_true',
                        help='If set, the model_group.in will be written - '
                             'by default model_group.in file will not be written.')

    parser.set_defaults(write_element_files=False)
    parser.set_defaults(write_group_file=False)
    parser.set_defaults(write_node_file=False)


    args = parser.parse_args()
    #    inputs_dir = args.inputs_dir
    eweld_file = args.eweld_file
    bc_file = args.eweld_BC_file
    ini_file = args.eweld_preheat_temp_file
    out_dir = args.out_dir
    log_dir = args.log_dir
    write_element_files = args.write_element_files
    write_group_file = args.write_group_file
    write_node_file = args.write_node_file

    logfile = data_IO.open_file(os.path.join(log_dir, "Analysis_file_create.log"), "w" )

    maxn=1000000
    #setfile="step0_model_create.inp"
    #(numWeld,cooltime,power,speed,eff,thold,weldpass,numCe,model_node,model_ele_t,model_ele_s,model_group,model_film,model_bod,model_mat,model_therm,model_mech)=read_input(setfile)
    #print "Number of Weld = ", numWeld
    #print "Weld pass seq = ", weldpass
    
    #--------------------------------------------------------------
    # Read eweld.in
    #
    # eweld_file = os.path.join(inputs_dir, "eweld.in")

    (numWeld,myMaterial1,myMaterial2,FillerMaterial)=read_eweld_in(eweld_file, logfile)
    #--------------------------------------------------------------
    # Read aeweld_preheat_interpass_temperature.in
    # output model_ini_temperature.in
    #      

    # ini_file = os.path.join(inputs_dir, "eweld_preheat_interpass_temperature.in")
    (preheat,interpass)=read_ini_in(ini_file, logfile)

    out_fname = os.path.join(out_dir, "model_ini_temperature.in")
    ttt=output_ini(out_fname,preheat,interpass)
    #--------------------------------------------------------------
    # Read eweld_boundary_conditions.in
    #      
    # bc_file = os.path.join(inputs_dir, "eweld_boundary_condition.in" )

    (numfix,fix_cod,fix_dir)=read_bc_in(bc_file, logfile)
    #--------------------------------------------------------------
    # output model_materials.in
    #          
    out_fname = os.path.join(out_dir,"model_material.in")
    ttt=output_material(out_fname,numWeld,myMaterial1,myMaterial2,FillerMaterial)


    inp_fname= args.model_inp_file #"Model3d.inp"

    # if(os.path.isfile(inp_fname)==True) :
    #     #--------------------------------------------------------------
    #     # Read node
    #     #
    (num_node,ndidmax)=read_coordinate_pre(maxn,inp_fname, logfile)
    print("Number of Node in global model =", num_node)
    print("Maximum Node id =", ndidmax)
    text = "Number of Node in global model =" + str(num_node)
    logfile.write(text + '\n')
    text = "Maximum Node id =" + str(ndidmax)
    logfile.write(text + '\n')
	
    (numNode,nd_id,nd_cod)=read_coordinate(maxn,inp_fname, logfile, ndidmax,num_node)

    if write_node_file:
        model_node = os.path.join(out_dir, "model_node.in")
        out_fname = model_node
        ttt=create_node_in(out_fname,num_node,nd_id,nd_cod)

    #--------------------------------------------------------------
	# output model_materials.in
	#          
    out_fname = os.path.join(out_dir, "model_bc.in")
    nfmin = [[],]*100
    ttt=output_bc(out_fname,num_node,nd_id,nd_cod,numfix,fix_cod,fix_dir,nfmin)
    #-----------------------------------------------------------------
    # Read elements
    #


    out_fname="ele_temp.in"
    (num_ele,eleidmax)=read_element_pre(maxn,inp_fname,out_fname, logfile)
    print("Number of element =", num_ele)
    print("Maximum ele id =", eleidmax)
	
    text = "Number of element =" + str(num_ele)
    logfile.write(text + '\n')
    text = "Maximum ele id =" + str(eleidmax)
    logfile.write(text + '\n')

    (numEle,ele_id,eletype,ele)=read_element(maxn,inp_fname, logfile, eleidmax, num_ele)
    print("numEle =", numEle)

    if write_element_files:
        output_element_files(out_dir, inp_fname, ele, ele_id, eletype)

    if write_group_file:
        model_group_file= os.path.join(out_dir, "model_group.in")
        numgroup=create_group(maxn,inp_fname, model_group_file, logfile)
        print("model_group.in has been created!")
        
    #-----------------------------------------------------------------
    # Read film
    #
    #model_film="model_film.in"
    #out_fname=model_film
    #numFilm=read_film(maxn,inp_fname,out_fname)
    #print "Number of Film =", numFilm

    # move file
    os.remove("ele_temp.in")
             
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


if __name__ == "__main__":
    main()
