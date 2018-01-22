c********************************************************************
      implicit real*8(a-h,o-z)

      dimension npass(50)	
      
      dimension ptl(100,2),ptm(100,2),ptr(100,2)
      dimension threept(3,2)
      dimension cent(100,2),rad(50)
      dimension pcd(50,25,15,2),ncord(50,25)       
      dimension area_layer(50),areaps(50,25)
      dimension pcent(50,25,2)
      
      character(len=500) outDir
      call get_output_path(outDir)

      open(unit=10,file=trim(adjustl(outDir))//"pass_coordinates.out") 
      open(unit=20,file=trim(adjustl(outDir))//"pass_area.out") 	
      open(unit=30,file=trim(adjustl(outDir))//"pass_center_area.out") 	
      
      call eweld_input(th,vland,angle,gap,
     &     reinf,pene,ptclose,layer,npass)

      call corner_point(gap,reinf,pene,layer,vland,th,angle,ptl,ptm,ptr)

      call point_on_groove(reinf,layer,angle,ptl,ptm,ptr)   
      
      call arc_cent_rad(layer,ptl,ptm,ptr,threept,cent,rad)
      
      call area_per_layer(layer,ptl,ptm,ptr,area_layer)
      
      call pass_coord(layer,npass,ptl,ptm,ptr,cent,rad,
     $     area_layer,pcd,ncord,areaps)
      
      do 10 i=1,layer
         write(20,'(i2,10(",",f15.6))') i,area_layer(i),
     &        (areaps(i,jp),jp=1,npass(i))
 10   continue

      call merge_closept(ptclose,layer,npass,ncord,pcd)
      call broken_side(ptclose,layer,npass,ncord,pcd)
      
      do 15 i=1,layer
         do 35 j=1,npass(i)
            call parea_cal(i,j,layer,npass,ncord,pcd,pcent,areaps)
 35      continue
 15   continue   

      write(10,'("*Number-of-Layers")')  
      write(10,'(I2)') layer 
      
      write(10,'("*Layer,Number-of-Passes")')  
      do 70 i=1,layer
         write(10,'(I2,1(",",I2))') layer,npass(i) 
 70   continue      

      do 20 i=1,layer
         write(20,'(i2,10(",",f15.6))') i,area_layer(i),
     &        (areaps(i,jp),jp=1,npass(i))
         do 40 j=1,npass(i)
            write(30,'(i2,",",I2,3(",",f15.6))') i,j,pcent(i,j,1),
     &           pcent(i,j,2),areaps(i,j)
            write(10,'("*Layer,Pass,Number-of-Point")')
            write(10,'(I2,2(",",I2))') i,j,ncord(i,j)
            write(10,'("*Point, X, Y")')
            do 60 k=1,ncord(i,j)
               write(10,'(i2,2(",",f15.6))') k,pcd(i,j,k,1),pcd(i,j,k,2)
 60         continue
 40      continue
 20   continue  

      close(10)
      close(20)
      close(30)
      
      end

!------------------------------------------------------------------------------
      subroutine get_output_path(outDir)
!     Set output directory from command line input
      character(len=500) outDir
!     Check if any arguments are found
      narg=command_argument_count()
      if(narg>0)then
         call get_command_argument(1,outDir)
         outDir = adjustl(outDir)
      else
         outDir = ""
      end if
      end

!------------------------------------------------------------------------------
      subroutine broken_side(ptclose,layer,npass,ncord,pcd)
      
      implicit real*8(a-h,o-z)
      
      dimension pcd(50,25,15,2),ncord(50,25)    
      dimension npass(50)
      
      do 10 i=1,layer
         do 30 j=1,npass(i)
            do 50 k=1,ncord(i,j)            
               i1=i
               j1=j
               k1=k
               call broken(ptclose,i1,j1,k1,layer,npass,ncord,pcd)
 50         continue      
 30      continue   
 10   continue 

      return      
      end

      subroutine broken(ptclose,i1,j1,k1,layer,npass,ncord,pcd)
      
      implicit real*8(a-h,o-z)
      
      dimension pcd(50,25,15,2),ncord(50,25)    
      dimension npass(50)
      
      px=pcd(i1,j1,k1,1)
      py=pcd(i1,j1,k1,2)  
      write(1100,'(3I2,2f15.6)') i1,j1,k1,pcd(i1,j1,k1,1),
     &     pcd(i1,j1,k1,2)
      do 10 i=1,layer
         do 30 j=1,npass(i)
            do 50 k=1,ncord(i,j)        
               p1x=pcd(i,j,k,1)
               p1y=pcd(i,j,k,2)             
               if(k.eq.ncord(i,j)) then
                  p2x=pcd(i,j,1,1)
                  p2y=pcd(i,j,1,2)           
               else
                  p2x=pcd(i,j,k+1,1)
                  p2y=pcd(i,j,k+1,2)     
               endif
               if((px.gt.p1x.and.px.lt.p2x).or.   
     &              (px.lt.p1x.and.px.gt.p2x)) then
               call dist2line(p1x,p1y,p2x,p2y,px,py,dist)
               if(dist.gt.0.and.dist.le.(0.5*ptclose)) then 
                  kf=k+1
                  write(1100,*) "insert", i, j, kf
                  write(1100,'(6F15.6)') p1x,p1y,px,py,p2x,p2y
                  write(1100,*) "dist =", dist
                  call insert(i,j,kf,px,py,ncord,pcd)
                  ncord(i,j)=ncord(i,j)+1
                  return
               endif
            endif
 50      continue      
 30   continue   
 10   continue 

      return      
      end
      
      subroutine insert(i,j,kf,px,py,ncord,pcd)
      
      implicit real*8(a-h,o-z)
      
      dimension pcd(50,25,15,2),ncord(50,25)    
      
      do 50 k=ncord(i,j),kf,-1        
         pcd(i,j,k+1,1)=pcd(i,j,k,1)
         pcd(i,j,k+1,2)=pcd(i,j,k,2)         
         if(k.eq.kf) then   
            pcd(i,j,k,1)=px
            pcd(i,j,k,2)=py
         endif
 50   continue      

      return      
      end
      
!     Ref https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
      
      subroutine dist2line(p1x,p1y,p2x,p2y,px,py,dist)
      
      implicit real*8(a-h,o-z)
      
      dx = p2x - p1x
      dy = p2y - p1y
!     top=abs(dy*px - dx*py + p2x*py1 - p2y*p1x)
      t1=dx*(p1y-py)
      t2=(p1x-px)*dy
      
      top=abs(t1-t2)
      bot=sqrt(dy**2 + dx**2)
      
      dist = top/bot
      
      return      
      end
!------------------------------------------------------------------------------
      subroutine merge_closept(ptclose,layer,npass,ncord,pcd)
      
      implicit real*8(a-h,o-z)
      
      dimension pcd(50,25,15,2),ncord(50,25)    
      dimension npass(50)
      
      do 10 i=1,layer
         do 30 j=1,npass(i)
            do 50 k=1,ncord(i,j)            
               i1=i
               j1=j
               k1=k
               call mergept(ptclose,i1,j1,k1,layer,npass,ncord,pcd)
 50         continue      
 30      continue   
 10   continue 

      return      
      end

      subroutine mergept(ptclose,i1,j1,k1,layer,npass,ncord,pcd)
      
      implicit real*8(a-h,o-z)
      
      dimension pcd(50,25,15,2),ncord(50,25)    
      dimension npass(50)
      
      p1x=pcd(i1,j1,k1,1)
      p1y=pcd(i1,j1,k1,2)  
      write(1100,'(3I2,2f15.6)') i1,j1,k1,pcd(i1,j1,k1,1),
     &     pcd(i1,j1,k1,2)
      do 10 i=1,layer
         do 30 j=1,npass(i)
            do 50 k=1,ncord(i,j)        
               p2x=pcd(i,j,k,1)
               p2y=pcd(i,j,k,2)     
               call dist2pt(p1x,p1y,p2x,p2y,dist)
               if(dist.gt.0.and.dist.le.ptclose) then 
C                  write(1100,'(3I2,2f15.6)') i,j,k,pcd(i,j,k,1),pcd(i,j,k,2)       
                  pcd(i1,j1,k1,1)=(p1x+p2x)/2.0
                  pcd(i1,j1,k1,2)=(p1y+p2y)/2.0
                  pcd(i,j,k,1)=(p1x+p2x)/2.0
                  pcd(i,j,k,2)=(p1y+p2y)/2.0 
                  write(1100,*) "Found"
                  write(1100,'(3I2,2f15.6)') i1,j1,k1,pcd(i1,j1,k1,1),
     &                 pcd(i1,j1,k1,2)
C                  write(1100,'(3I2,2f15.6)') i,j,k,pcd(i,j,k,1),pcd(i,j,k,2)
               endif
 50         continue      
 30      continue   
 10   continue 

      return      
      end
      
      subroutine dist2pt(p1x,p1y,p2x,p2y,dist)
      
      implicit real*8(a-h,o-z)
      
      dx = p2x - p1x
      dy = p2y - p1y
      dist = sqrt(dx**2 + dy**2)
      
      return      
      end
!------------------------------------------------------------------------------
      subroutine pass_coord(layer,npass,ptl,ptm,ptr,cent,rad,
     $     area_layer,pcd,ncord,areaps)
      
      implicit real*8(a-h,o-z)
      
      dimension ptl(100,2),ptm(100,2),ptr(100,2)
      dimension cent(100,2),rad(50)  	
      dimension pcd(50,25,15,2),ncord(50,25)    
      dimension area_layer(50),npass(50),areaps(50,25)
      
      do 10 i=1,layer
         write(1100,*) area_layer(i),npass(i)
         if(npass(i).eq.1) then 
            areaps(i,1)=area_layer(i) 
            call pass_coord_npass1(i,ptl,ptm,ptr,pcd,ncord)   
         else
            area_pass=area_layer(i)/npass(i) 
            dxb=(ptr(i,1)-ptl(i,1))/1000.0
            dxt=(ptr(i+1,1)-ptl(i+1,1))/1000.0
            cx1=cent(i,1)
            cy1=cent(i,2)
            cx2=cent(i+1,1)
            cy2=cent(i+1,2)
            rr1=rad(i)  
            rr2=rad(i+1)
            write(1100,*) cx1,cy1,cx2,cy2,rr1,rr2
            do 30 j=1,npass(i)
               if(j.eq.1) then  
                  pst1x=ptl(i,1)
                  pst1y=ptl(i,2)
                  pst4x=ptl(i+1,1)
                  pst4y=ptl(i+1,2)
               endif
               do 50 k=1,1000         
                  p1x=pst1x
                  p1y=pst1y
                  p2x=pst1x + k*dxb
                  p2y= cy1 + sqrt(rr1**2-(p2x-cx1)**2)  
                  p4x=pst4x
                  p4y=pst4y
                  p3x=pst4x + k*dxt 
                  p3y=cy2 + sqrt(rr2**2-(p3x-cx2)**2)
!     write(1100,*) p2x,p2y
!     write(1100,*) p4x,p4y
                  call area_4pt(p1x,p1y,p2x,p2y,p3x,p3y,p4x,p4y,area)
!     if reaching to the right edge
                  if(j.eq.npass(i)) then        
                     p2x=ptr(i,1)
                     p2y=ptr(i,2)  
                     p3x=ptr(i+1,1) 
                     p3y=ptr(i+1,2)
                     call area_4pt(p1x,p1y,p2x,p2y,p3x,p3y,p4x,p4y,
     &                    areaps(i,j))
                     call pscoord(i,j,p1x,p1y,p2x,p2y,p3x,p3y,p4x,p4y,
     &                    pcd,ncord)
                     goto 30
                  endif            
                  if(area.ge.area_pass) then
                     areaps(i,j)=area
!                     write(1100,'("compare",3f15.6)') area,area_pass,areaps(i,j)
                     pst1x=p2x
                     pst1y=p2y
                     pst4x=p3x
                     pst4y=p3y
                     call pscoord(i,j,p1x,p1y,p2x,p2y,p3x,p3y,p4x,p4y,
     &                    pcd,ncord)
                     goto 30
                  endif
 50            continue      
 30         continue
         endif   
 10   continue 

      return      
      end
!------------------------------------------------------------------------------
      subroutine pscoord(i,j,p1x,p1y,p2x,p2y,p3x,p3y,p4x,p4y,pcd,ncord)
      
      implicit real*8(a-h,o-z)

      dimension pcd(50,25,15,2),ncord(50,25)    

      ncord(i,j)=4
      pcd(i,j,1,1)=p1x
      pcd(i,j,1,2)=p1y
      pcd(i,j,2,1)=p2x
      pcd(i,j,2,2)=p2y              
      pcd(i,j,3,1)=p3x
      pcd(i,j,3,2)=p3y
      pcd(i,j,4,1)=p4x
      pcd(i,j,4,2)=p4y    

      return      
      end
!------------------------------------------------------------------------------
      subroutine pass_coord_npass1(i,ptl,ptm,ptr,pcd,ncord)
      
      implicit real*8(a-h,o-z)
      
      dimension ptl(100,2),ptm(100,2),ptr(100,2)	
      dimension pcd(50,25,15,2),ncord(50,25)    

      ncord(i,1)=6 
      pcd(i,1,1,1)=ptl(i,1)
      pcd(i,1,1,2)=ptl(i,2)
      pcd(i,1,2,1)=ptm(i,1)
      pcd(i,1,2,2)=ptm(i,2)              
      pcd(i,1,3,1)=ptr(i,1)
      pcd(i,1,3,2)=ptr(i,2)
      pcd(i,1,4,1)=ptr(i+1,1)
      pcd(i,1,4,2)=ptr(i+1,2)
      pcd(i,1,5,1)=ptm(i+1,1)
      pcd(i,1,5,2)=ptm(i+1,2)
      pcd(i,1,6,1)=ptl(i+1,1)
      pcd(i,1,6,2)=ptl(i+1,2)      

      return      
      end
!------------------------------------------------------------------------------
      subroutine area_per_layer(layer,ptl,ptm,ptr,area_layer)
      
      implicit real*8(a-h,o-z)
      
      dimension ptl(100,2),ptm(100,2),ptr(100,2)      
      dimension area_layer(50)
      
      do 10 i=1,layer
         p1x=ptl(i,1)
         p1y=ptl(i,2)
         p2x=ptm(i,1)
         p2y=ptm(i,2)              
         p3x=ptm(i+1,1)
         p3y=ptm(i+1,2)
         p4x=ptl(i+1,1)
         p4y=ptl(i+1,2)      
         call area_4pt(p1x,p1y,p2x,p2y,p3x,p3y,p4x,p4y,area_l)
!     write(1100,*) "area 1", i, area_l
         
         p1x=ptm(i,1)
         p1y=ptm(i,2)
         p2x=ptr(i,1)
         p2y=ptr(i,2)              
         p3x=ptr(i+1,1)
         p3y=ptr(i+1,2)
         p4x=ptm(i+1,1)
         p4y=ptm(i+1,2)      
         call area_4pt(p1x,p1y,p2x,p2y,p3x,p3y,p4x,p4y,area_r)
!     write(1100,*) "area 2", i, area_r
         
         area_layer(i) = area_l + area_r         
         write(1100,*) "area", i, area_layer(i)
 10   continue     

      return      
      end
!------------------------------------------------------------------------------
      subroutine arc_cent_rad(layer,ptl,ptm,ptr,threept,cent,rad)
      
      implicit real*8(a-h,o-z)
      
      dimension ptl(100,2),ptm(100,2),ptr(100,2)

      dimension threept(3,2)
      
      dimension cent(100,2),rad(50)
      
      nt= layer + 1
      do 10 i=1,nt
         threept(1,1)=ptl(i,1)
         threept(1,2)=ptl(i,2)
         threept(2,1)=ptm(i,1)
         threept(2,2)=ptm(i,2)              
         threept(3,1)=ptr(i,1)
         threept(3,2)=ptr(i,2)     
         call circle_3pt(threept,centx,centy,radius)  
         cent(i,1) = centx
         cent(i,2) = centy
         rad(i) = radius
         write(1100,'(i2,3(",",F15.6))') i, cent(i,1),cent(i,2),rad(i)
 10   continue     

      return      
      end
!------------------------------------------------------------------------------
      subroutine point_on_groove(reinf,layer,angle,ptl,ptm,ptr)
      
!     g - groove
      
      implicit real*8(a-h,o-z)
      
      dimension ptl(100,2),ptm(100,2),ptr(100,2)
      
      pi=acos(-1.0)    
      write(1100,*) 
      
      delt_left =  (ptl(layer+1,2)-ptl(1,2))/layer
      delt_right = (ptr(layer+1,2)-ptr(1,2))/layer
      delt_mid =   (ptm(layer+1,2)-ptm(1,2))/layer
      
      nt = layer + 1
      do 10 i=2,layer       
         ptl(i,1)=ptl(1,1)+(i-1)*delt_left*ptl(layer+1,1)/ptl(layer+1,2)
         ptl(i,2)=(i-1)*delt_left
         
         ptm(i,1) =  0.0
         ptm(i,2) =  (i-1)*delt_mid         
         
         ptr(i,1)=ptr(1,1)+(i-1)*delt_right*ptr(layer+1,1)/
     &        ptr(layer+1,2)
         ptr(i,2)=(i-1)*delt_right
         
         write(1100,*) i, ptl(i,1), ptl(i,2)  
         write(1100,*) i, ptm(i,1), ptm(i,2)  
         write(1100,*) i, ptr(i,1), ptr(i,2)  
         write(1100,*)
 10   continue 

      return      
      end
!------------------------------------------------------------------------------
      subroutine eweld_input(th,vland,angle,gap,
     &     reinf,pene,ptclose,layer,npass)
      implicit real*8(a-h,o-z)
      CHARACTER*8 x_groove
      dimension npass(50)	

      open(unit=2000,file="inputs/eweld.in",status='old')   
      write(1100,'("*Plate length")')
      read(2000,*)
      read(2000,*) ttt
      tlen=ttt*25.4
      write(1100,*) "length = ", tlen
      
      write(1100,'("*Plate thickness")')
      read(2000,*)
      read(2000,*) ttt
      th=ttt*25.4
      write(1100,*) "thickness = ", th

      write(1100,'("*Plate width")')
      read(2000,*)
      read(2000,*) w1, w2           
      width1=w1*25.4
      width2=w2*25.4
      write(1100,*) "width1, width2 = ", width1, width2
      
      write(1100,'("*Material")')
      read(2000,*)
      read(2000,*) 
      
      write(1100,'("*FillerMaterial")')
      read(2000,*)
      read(2000,*)                                     
      
      write(1100,'("*Weld Type")')
      read(2000,*)
      read(2000,*)      
      
      write(1100,'("*Weld Reinforcement")')
      read(2000,*)
      read(2000,*) ttt
      reinf=ttt*25.4
      write(1100,*) "Reinforcement = ", reinf              

      write(1100,'("*Weld penetration")')
      read(2000,*)
      read(2000,*) ttt
      pene=ttt*25.4
      write(1100,*) "Penetration = ", pene
      
      write(1100,'("*Weld root gap value")')
      read(2000,*)
      read(2000,*) ttt
      gap=ttt*25.4             
      write(1100,*) "gap = ", gap 
      
      write(1100,'("*Tolerance for point Coordinate")')
      read(2000,*)
      read(2000,*) ttt
      ptclose=ttt*25.4
      write(1100,*) "Tolerance for point Coordinate = ", ptclose
      
      write(1100,'("*Mesh Size")')
      read(2000,*)
      read(2000,*) ttt
      dmesh=ttt*25.4
      write(1100,*) "Mesh size = ", dmesh              
      
      write(1100,'("*Number of layer")')
      read(2000,*)
      read(2000,*) layer
      write(1100,*) "layer =", layer
      
      write(1100,'("*Layer, Number of passes")')
      read(2000,*)

      do 70 i=1,layer
         read(2000,*) nt,npass(i)
         write(1100,*) "nt, npass(i)", nt, npass(i)
 70   continue 

      write(1100,'("*Joint Type")')
      read(2000,*)
      read(2000,*) 

      write(1100,'("*Groove dimensions")')
      read(2000,*)
      read(2000,*) x_groove              
      read(2000,*) vland
      read(2000,*) angle
      vland=vland*25.4
      angle=angle/2
      write(1100,*) "vland, angle = ", vland, angle 	

 40   close(2000) 

      return      
      end
c------------------------------------------------------------------------------
      subroutine corner_point(gap,reinf,pene,layer,vland,th,
     &     angle,ptl,ptm,ptr)

!     b - bottom; t - top; l - left; r - right; m - middle
      
      implicit real*8(a-h,o-z)
      
      dimension ptl(100,2),ptm(100,2),ptr(100,2)
      
      pi=acos(-1.0)    
!     write(1100,*) "pi = ", pi
!     bottom 3 points
      
      if(gap.lt.0.001) then
         rd=1.0
      else
         rd=0.5
      endif
      
      ptl(1,1) = -rd - gap/2.0
      ptl(1,2) =  0.0      
      
      ptm(1,1) = 0.0
      ptm(1,2) = 0.0 - reinf/3.0
      
      ptr(1,1) = rd + gap/2.0
      ptr(1,2) = 0.0
c      write(1100,*) "bottom 3 points "
      ibot=1
c      write(1100,*) ibot, ptl(1,1),ptl(1,2)
c      write(1100,*) ibot, ptm(1,1),ptm(1,2)
c      write(1100,*) ibot, ptr(1,1),ptr(1,2)      
!  top 3 points     
      jtop = layer + 1
      
      ptl(jtop,1) = -gap/2.0 -(th-vland)*tan(angle*pi/180.0) - pene
      ptl(jtop,2) = th

      ptm(jtop,1) = 0.0
      ptm(jtop,2) = th + reinf      
      
      ptr(jtop,1) = gap/2.0 + (th-vland)*tan(angle*pi/180.0) + pene
      ptr(jtop,2) = th
      
c      write(1100,*) "top 3 points "    
c      write(1100,*) jtop, ptl(layer+1,1),ptl(layer+1,2)
c      write(1100,*) jtop,ptm(layer+1,1),ptm(layer+1,2)
c      write(1100,*)jtop, ptr(layer+1,1),ptr(layer+1,2)
      return
      end
!*************************************************
      subroutine area_4pt(p1x,p1y,p2x,p2y,p3x,p3y,p4x,p4y,area)
      
      implicit real*8(a-h,o-z)
      
      pi=acos(-1.0)    
!     write(1100,*) "pi = ", pi
      
      dx = p2x - p1x
      dy = p2y - p1y
      ba=sqrt(dx*dx + dy*dy)
      dx = p3x - p2x
      dy = p3y - p2y
      cb=sqrt(dx*dx + dy*dy)
      dx = p4x - p3x
      dy = p4y - p3y
      dc=sqrt(dx*dx + dy*dy)
      dx = p1x - p4x
      dy = p1y - p4y
      ad=sqrt(dx*dx + dy*dy)      
      dx = p4x - p2x
      dy = p4y - p2y
      db=sqrt(dx*dx + dy*dy)  

!     write(1100,*) "ba = ", ba
!     write(1100,*) "cb = ", cb
!     write(1100,*) "dc = ", dc
!     write(1100,*) "ad = ", ad
!     write(1100,*) "db = ", db
      
      theta_a = acos( (ba*ba + ad*ad - db*db)/(2.0*ba*ad) )     
      theta_c = acos( (cb*cb + dc*dc - db*db)/(2.0*cb*dc) )

!     write(1100,*) "angle 1 ", theta_a
!     write(1100,*) "angle 2 ", theta_c    
!     
!     write(1100,*) "angle 1 ", theta_a*180/pi
!     write(1100,*) "angle 2 ", theta_c*180/pi
      
      theta = (theta_a + theta_c)/2.0
      s = (ba + cb + dc + ad )/2.0
      
      sa = s - ba
      sb = s - cb
      sc = s - dc
      sd = s - ad
      area = sqrt(sa*sb*sc*sd - ba*cb*dc*ad*cos(theta)*cos(theta) )
      
      return
      end
!----------------------------------------------
      subroutine circle_3pt(threept,centx,centy,radius)
      
      implicit real*8(a-h,o-z)
      
      dimension threept(3,2)
      
      TOL = 0.0000001;

      p1x = threept(1,1)
      p1y = threept(1,2)
      p2x = threept(2,1)
      p2y = threept(2,2)
      p3x = threept(3,1)
      p3y = threept(3,2)
      
      pt1pow = p1x**2 + p1y**2
      pt2pow = p2x**2 + p2y**2
      pt3pow = p3x**2 + p3y**2
      
      yDelta_a = p2y - p1y;
      xDelta_a = p2x - p1x;
      yDelta_b = p3y - p2y;
      xDelta_b = p3x - p2x;
      
      aSlope = yDelta_a/xDelta_a
      bSlope = yDelta_b/xDelta_b  
      
      top = aSlope*bSlope*(p1y-p3y)+bSlope*(p1x+p2x)-aSlope*(p2x+p3x)
      bot = 2*(bSlope-aSlope) 
      centx = top/bot
      
      term = centx - (p1x+p2x)/2
      centy = -term/aSlope + (p1y+p2y)/2
      
      radius = sqrt( (p2x-centx)**2 + (p2y-centy)**2 )
      
      return
      end
!-------Area Calculation-----------------------------------------------------
      subroutine parea_cal(ii,jj,layer,npass,ncord,pcd,pcent,areaps)    
      implicit real*8(a-h,o-z)
      
      dimension pcent(50,25,2),pcd(50,25,15,2),areaps(100,10)
      dimension ncord(50,25),npass(50)

      do 10 i=1,layer
         do 30 j=1,npass(i)

            pctx=0
            pcty=0
            do 50 k=1,ncord(i,j)            
               pctx = pctx + pcd(i,j,k,1)
               pcty = pcty + pcd(i,j,k,2)     	
 50         continue          
            pcent(i,j,1)=pctx/ncord(i,j)
            pcent(i,j,2)=pcty/ncord(i,j)

            p1x=pcent(i,j,1)
            p1y=pcent(i,j,2)
            nt=ncord(i,j)-1 
            area=0
            do 70 k=1,ncord(i,j)           
               p2x = pcd(i,j,k,1)
               p2y = pcd(i,j,k,2)
               if(k.eq.ncord(i,j)) then
                  p3x = pcd(i,j,1,1)
                  p3y = pcd(i,j,1,2)           
               else
                  p3x = pcd(i,j,k+1,1)
                  p3y = pcd(i,j,k+1,2) 
               endif          
               call area_3pt(p1x,p1y,p2x,p2y,p3x,p3y,area3p)
               area=area+area3p
c               write(1100,*) i,j,k,area3p
 70         continue       
            areaps(i,j)=area
c            write(1100,'("C,A",2I2,3F15.6)') i,j,pcent(i,j,1),
c     $           pcent(i,j,2),areaps(i,j)

 30      continue   
 10   continue 
      
      return
      end      
      
      subroutine area_3pt(p1x,p1y,p2x,p2y,p3x,p3y,area3p)
      implicit real*8(a-h,o-z)
      
      call dist2pt(p1x,p1y,p2x,p2y,a)
      call dist2pt(p2x,p2y,p3x,p3y,b)
      call dist2pt(p3x,p3y,p1x,p1y,c)
      
      p=(a+b+c)/2
      area3p=sqrt(p*(p-a)*(p-b)*(p-c))
      
      return
      end      
