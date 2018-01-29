! Abaqus interface 
!      subroutine dflux(flux,sol,kstep,kinc,time,noel,npt,coords, 
!     & jltyp,temp,press,sname) 
            
! Calculix interface  
      subroutine dflux(flux,sol,kstep,kinc,time,noel,npt,coords, 
     &     jltyp,temp,press,loadtype,area,vold,co,lakonl,konl, 
     &     ipompc,nodempc,coefmpc,nmpc,ikmpc,ilmpc,iscale,mi, 
     &     sti,xstateini,xstate,nstate_,dtime) 
 
      implicit real*8(a-h,o-z)     
      DIMENSION COORDS(3),FLUX(2),TIME(2) 
      character*80 sname      
      character*8 lakonl    
      character*20 loadtype 
   
      pi=acos(-1.0) 
      k=(kstep+2)/3 
             
      call heat_line_input(k,nwps,jshape,rad,power,speed,eff, 
     &  thold,a,b,cf,cr,x0,y0,z0,x1,y1,z1) 
            
      timenet=time(1)-thold 
      if(jshape.eq.1) then 
          xarc=  x0 
		yarc=  y0 
		zarc= speed*timenet + z0 
          xcod=coords(1)-xarc	 
		ycod=coords(2)-yarc 
		zcod=coords(3)-zarc 
      else if(jshape.eq.2) then 
		omega=speed*time(1)/rad	 
		ythe=cos(omega)*rad  
		zthe=sin(omega)*rad  
		xthe=x0	 
 		xcod=coords(1)-xthe 
		ycod=coords(2)-ythe 
		zcod=coords(3)-zthe 
      endif 
 
      call dellipse(power,eff,a,b,cf,cr,xcod,ycod,zcod,qflux) 
      flux(1)=qflux     
                 
      RETURN 
      END 
 
	subroutine heat_line_input(k,nwps,jshape,rad,power,speed,eff, 
     &  thold,a,b,cf,cr,x0,y0,z0,x1,y1,z1) 
 
      implicit real*8(a-h,o-z) 
 
      if(k.eq.1) then 
         nwps=1 
         jshape=1
         rad=-2.14488883333
         power=5000.0
          speed=-3.175
           eff=0.5
            thold=0.25 
         a=3.80996
          b=2.7093335
           cf=3.80996
            cr=7.61992
          x0=0.0
           y0=2.14488883333
            z0=0.0 
          x1=0.0
           y1=0.0
            z1=-25.4
      elseif(k.eq.2 )then 
         nwps=1 
         jshape=1
         rad=-7.3795974
         power=5000.0
          speed=-3.175
           eff=0.5
            thold=0.25 
         a=3.3059595
          b=2.7939765
           cf=3.3059595
            cr=6.611919
          x0=-2.7759826
           y0=7.3795974
            z0=0.0 
          x1=-2.7759826
           y1=-2.7759826
            z1=-25.4
      elseif(k.eq.3 )then 
         nwps=1 
         jshape=1
         rad=-7.3860682
         power=5000.0
          speed=-3.175
           eff=0.5
            thold=0.25 
         a=3.3158775
          b=2.7939765
           cf=3.3158775
            cr=6.631755
          x0=2.736311
           y0=7.3860682
            z0=0.0 
          x1=2.736311
           y1=2.736311
            z1=-25.4
      elseif(k.eq.4 )then 
         nwps=1 
         jshape=1
         rad=-11.11358625
         power=5000.0
          speed=-3.175
           eff=0.5
            thold=0.25 
         a=2.4838405
          b=2.6774885
           cf=2.4838405
            cr=4.967681
          x0=-5.70676325
           y0=11.11358625
            z0=0.0 
          x1=-5.70676325
           y1=-5.70676325
            z1=-25.4
      elseif(k.eq.5 )then 
         nwps=1 
         jshape=1
         rad=-11.83318775
         power=5000.0
          speed=-3.175
           eff=0.5
            thold=0.25 
         a=2.1756105
          b=2.3788765
           cf=2.1756105
            cr=4.351221
          x0=-1.9824905
           y0=11.83318775
            z0=0.0 
          x1=-1.9824905
           y1=-1.9824905
            z1=-25.4
      elseif(k.eq.6 )then 
         nwps=1 
         jshape=1
         rad=-11.8504175
         power=5000.0
          speed=-3.175
           eff=0.5
            thold=0.25 
         a=2.1350935
          b=2.3626995
           cf=2.1350935
            cr=4.270187
          x0=1.83203025
           y0=11.8504175
            z0=0.0 
          x1=1.83203025
           y1=1.83203025
            z1=-25.4
      elseif(k.eq.7 )then 
         nwps=1 
         jshape=1
         rad=-11.130816
         power=5000.0
          speed=-3.175
           eff=0.5
            thold=0.25 
         a=2.5631835
          b=2.695771
           cf=2.5631835
            cr=5.126367
          x0=5.6166565
           y0=11.130816
            z0=0.0 
          x1=5.6166565
           y1=5.6166565
            z1=-25.4
      endif  
       
      return     
      end   
   
	subroutine dellipse(powerk,effk,ak,bk,cfk,crk, 
     &	xcod,ycod,zcod,qflux) 
 
      implicit real*8(a-h,o-z) 
  
	pi=acos(-1.0) 
	 
	cf=cfk 
	cr=crk 
	if(zcod.ge.0.0) then 
		ff=2*cf/(cf+cr) 
		fheat=ff 
		cheat=cf 
	else if(zcod.lt.0.0) then 
		fb=2*cr/(cf+cr) 
		fheat=fb 
		cheat=cr 
	else 
		stop "*** error in fheat calculation ***" 
	end if 
 
      qtop=6.0*sqrt(3.0)*effk*powerk*fheat 
	qbot=pi*ak*bk*cheat*sqrt(pi)  
	qmax=(qtop/qbot)  
 
      gcutk=ak/10  
     	if(abs(xcod).lt.gcutk) then 
		xcod=gcutk 
	end if 
	if(abs(ycod).lt.gcutk) then 
		ycod=gcutk 
	endif 
	if(abs(zcod).lt.gcutk) then 
		zcod=gcutk 
	endif         
 
      rx2=(xcod*xcod)/(ak**2)	 
	ry2=(ycod*ycod)/(bk**2) 
	rz2=(zcod*zcod)/(cheat**2) 
 
	qflux=qmax*exp(-3.0*(rx2+ry2+rz2)) 
           
!      write(7,*) "zcod",zcod 
!      write(7,*) "qtop,bbot,qmax=",qtop,qbot,qmax 
!      write(7,*) "abc f ",ak,bk,cheat,fheat 
!      write(7,*) "q =",qqflux 
 
	return 
	end 
