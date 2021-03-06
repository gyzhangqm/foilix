C***********************************************************************
C  POLAR PLOTTING FACILITY FOR MSES AND XFOIL
C
C    INPUT:
C     * Polar file(s) generated by MSES or XFOIL
C     * Reference data files in the format:
C
C         CD(1)  CL(1)
C         CD(2)  CL(2)
C          .      .
C          .      .
C         999.0  999.0
C         alpha(1)  CL(1)
C         alpha(2)  CL(2)
C           .       .
C           .       .
C         999.0   999.0
C         alpha(1)  Cm(1)
C         alpha(2)  Cm(2)
C           .       .
C           .       .
C         999.0   999.0
C         Xtr/c(1)  CL(1)
C         Xtr/c(2)  CL(2)
C           .        .
C           .        .
C         999.0   999.0
C         
C         The number of points in each set (CD-CL, alpha-CL, etc.) 
C         is arbitrary, and can be zero.
C
C     * pplot.def  plot parameter file (optional)
C
C***********************************************************************
C
      PROGRAM PPLOT
      INCLUDE 'PPLOT.INC'
C
      LOGICAL ERROR, LGETFN, LERR, ERR
      REAL RINP(10)
      REAL CPOLO(NAX,IPTOT,NPX), VPOLO(NAX,2,NPX)
C
      LPLOT = .FALSE.
C
      PI = 4.0*ATAN(1.0)
C
      CALL PLINITIALIZE
C
C...Get default settings
      CALL GETDEF
C
C...Try to read default file "pplot.def" for stored plot setup
      LU = 10
      OPEN(LU,FILE='pplot.def',STATUS='OLD',ERR=2)
      CALL RDDEF(LU,LERR)
      CLOSE(LU)
      IF(LERR) THEN
       WRITE(*,*)
       WRITE(*,*) 'Read error on file  pplot.def'
       WRITE(*,*) 'Using default settings'
       WRITE(*,*)
       CALL GETDEF
      ELSE
       WRITE(*,*)
       WRITE(*,*) 'Settings read from file  pplot.def'
       WRITE(*,*)
      ENDIF
      GO TO 3
C
 2    CONTINUE
      WRITE(*,*)
      WRITE(*,*) 'No  pplot.def  file found'
      WRITE(*,*) 'Using default settings'
      WRITE(*,*)
C
 3    CONTINUE
C
C---- Check for command line args (load file names)
      NPOL = 0
      DO II=1, NPX
        FNAME = ' '
        CALL GETARG0(II,FNAME)
        IF(FNAME.NE.' ') THEN
          NPOL = NPOL + 1
          FNPOL(NPOL) = FNAME
         ELSE
          IF(NPOL.GT.0) THEN
            IOPTS = 11
            GO TO 10
           ELSE
            GO TO 5
          ENDIF
        ENDIF
      END DO
C
    5 WRITE(*,1000)
      IF(NPOL.GT.0) WRITE(*,1010)
      WRITE(*,1020)
      WRITE(*,1050)
C
 1000 FORMAT(/'  1  Read polars          (-1 for new set)'
     &       /'  2  Read reference data  (-2 for new set)'
     &      //'  3  Plot CD(CL)'
     &      //'  4  Hardcopy current plot'
     &       /'  5  Change plot settings'
     &       /'  6  Zoom'
     &       /'  7  Unzoom'
     &       /'  8  Annotation menu'
     &      //'  9  Set CD(CL) modifiers')
 1010 FORMAT(/' 11  Re-read current polars'
     &       /' 12  Re-read current reference data')
 1020 FORMAT(/' 13  Plot Vz(V)'
     &       /' 19  Set aicraft parameters')
 1050 FORMAT(/'   Select option (0=quit): ', $)
C
      READ(*,*,ERR=5) IOPTS
      IOPT = ABS(IOPTS)
C
      GO TO (900, 10, 20, 30, 40, 50, 60, 70, 80, 90, 900,
     &            10, 20,130,  5,  5,  5,  5,  5,190,   5 ), IOPT+1
      GO TO 5
C
C=============================================
C---- read polars
 10   CONTINUE
      IF    (IOPTS.EQ.-1) THEN
C----- read new polars
       IP1 = 1
       IP2 = NPX
      ELSEIF(IOPTS.EQ. 1) THEN
C----- read additional polars
       IP1 = NPOL+1
       IP2 = NPX
      ELSE
C----- re-read old polars
       IP1 = 1
       IP2 = NPOL
      ENDIF
C
      DO 105 IP = IP1, IP2
        IF(IOPTS.EQ.1 .OR. IOPTS.EQ.-1) THEN
          CALL ASKS('Enter polar data filename or <return>^',FNPOL(IP))
        ENDIF
        IF(FNPOL(IP)(1:1) .EQ. ' ') GO TO 108
C
        LU = 9
        CALL POLREAD(LU,FNPOL(IP),ERROR,
     &    NAX,NA(IP),CPOL(1,1,IP), 
     &    REYN(IP),MACH(IP),ACRIT(IP),XTRIP(1,IP),
     &    PTRAT(IP),ETAP(IP),
     &    NAME(IP),IRETYP(IP),IMATYP(IP),
     &    ISX,NBL(IP),CPOLSD(1,1,1,IP),
     &    CODE,VERSION )
        IF(ERROR) THEN
         WRITE(*,*) 'Polar file READ error'
         GO TO 108
        ENDIF
C
        WRITE(*,8000) NAME(IP)
        IF(IMATYP(IP).EQ.1) WRITE(*,8011) MACH(IP)
        IF(IMATYP(IP).EQ.2) WRITE(*,8012) MACH(IP)
        IF(IMATYP(IP).EQ.3) WRITE(*,8013) MACH(IP)
        IF(IRETYP(IP).EQ.1) WRITE(*,8021) REYN(IP)/1.0E6 
        IF(IRETYP(IP).EQ.2) WRITE(*,8022) REYN(IP)/1.0E6
        IF(IRETYP(IP).EQ.3) WRITE(*,8023) REYN(IP)/1.0E6
        WRITE(*,8030) ACRIT(IP)
        IF(PTRAT(IP).NE.0.0) THEN
         WRITE(*,8040) PTRAT(IP)
         WRITE(*,8041) ETAP(IP)
        ENDIF
C
 8000   FORMAT(1X,A)
 8011   FORMAT('             Ma =', F7.3,       $)
 8012   FORMAT('    sqrt(CL)*Ma =', F7.3,       $)
 8013   FORMAT('          CL*Ma =', F7.3,       $)
 8021   FORMAT('             Re =', F7.3,' e 6',$)
 8022   FORMAT('    sqrt(CL)*Re =', F7.3,' e 6',$)
 8023   FORMAT('          CL*Re =', F7.3,' e 6',$)
 8030   FORMAT('          Ncrit =', F6.2         )
 8040   FORMAT('          pi_p  =', F8.4,       $)
 8041   FORMAT('          eta_p =', F8.4         )
C
 105  CONTINUE
      IP = IP2+1
C
 108  CONTINUE
      NPOL = IP-1
      IP2 = MIN(IP2,NPOL)
C
      DO IP = IP1, IP2
        CALL STRIP(NAME(IP),NNAME)
cccc        CALL GETTYP(NAX,NA(IP),CPOL(1,1,IP),IMATYP(IP),IRETYP(IP))
cc        ICOL(IP) = 2 + IP
cc        ILIN(IP) = IP
      ENDDO
CCC   CALL MINMAX(NAX,NPOL,NA,CPOL,CPOLPLF)
Co
C---- are these dimensional polars?
      DO IP = IP1, IP2
        CALL GETCLEN(NAME(IP),CCLEN,NCLEN)
        IF(NCLEN.GT.0) THEN
         LCLEN = .TRUE.
         GO TO 5
        ENDIF
      ENDDO
      IF(.NOT.LPLOT) GO TO 30
      GO TO 5
C
C=============================================
C---- read reference data
 20   CONTINUE
      IF(IOPTS.EQ.12 ) THEN
C------ re-read old data sets
        ID1 = 1
        ID2 = NDAT
        LGETFN = .FALSE.
      ELSEIF(IOPTS.GT.0) THEN
C------ read additional data sets
        ID1 = NDAT+1
        ID2 = NDX
        LGETFN = .TRUE.
      ELSE
C------ read new data sets
        ID1 = 1
        ID2 = NDX
        LGETFN = .TRUE.
      ENDIF
C
      DO 25 ID = ID1, ID2
        IF(LGETFN) THEN
         CALL ASKS('Enter reference data filename or <return>^',
     &              FNREF(ID))
         IF(FNREF(ID)(1:1) .EQ. ' ') GO TO 27
        ENDIF
C
        LU = 9
        OPEN(LU,FILE=FNREF(ID),STATUS='OLD',ERR=27)
        CALL POLREF(LU, FNREF(ID), ERROR,
     &              NFX, NF(1,ID), XYREF(1,1,1,ID), LABREF(ID) )
        CLOSE(LU)
        IF(ERROR) GO TO 27
C
        NDAT = ID
C
        CALL STRIP(LABREF(ID),NLAB)
        IF(NLAB.EQ.0) THEN
          CALL ASKS('Enter label for reference data^',LABREF(ID))
          CALL STRIP(LABREF(ID),NLAB)
        ENDIF
C
ccc     IFCOL(ID) = NCOLOR - ID + 1
        IFCOL(ID) = 2 + ID
        IFSYM(ID) = MOD(ID,10)
 25   CONTINUE
 27   CONTINUE
      GO TO 5
C
C=============================================
C---- Make the CD(CL) Plot
 30   IF (NPOL.EQ.0 .AND. NDAT.EQ.0) GO TO 5
C
C---- sort each polar by increasing alpha
      DO IP=1, NPOL
        CALL PLRSRT(IP,IAL)
      ENDDO
C
C---- set modified polars
      DO IP = 1, NPOL
        DO IA = 1, NA(IP)
          DO I = 1, IPTOT
            CPOLO(IA,I,IP) = CPOL(IA,I,IP)
          ENDDO
          CPOLO(IA,ICM,IP) = CPOL(IA,ICM,IP)
     &                     + DXMREF(IP)*CPOL(IA,ICL,IP)
C
          CPOLO(IA,ICD,IP) = CPOL(IA,ICD,IP)
     &                     + CDLMOD(1,IP)
     &                     + CDLMOD(2,IP)*CPOL(IA,ICL,IP)
     &                     + CDLMOD(3,IP)*CPOL(IA,ICL,IP)**2
          IF(CDLMOD(4,IP) .NE. 1.0) THEN
           CPOLO(IA,ICL,IP) = ABS(CPOL(IA,ICL,IP))**CDLMOD(4,IP)
          ENDIF
          IF(CDLMOD(5,IP) .NE. 0.0) THEN
           CPOLO(IA,ICD,IP) = CPOLO(IA,ICD,IP)
     &                      * ABS(CPOL(IA,ICL,IP))**CDLMOD(5,IP)
          ENDIF
        ENDDO
      ENDDO

      IF (LAUTO) THEN 
        CALL MINMAX(NAX,NPOL,NA,CPOLO,CPOLPLF)
        CALL SETINC
      ENDIF
C
      IF (LPLOT) CALL PLEND
      CALL PLOPEN(SCRNFR,IPSLU,IDEV)
      LPLOT = .TRUE.
C
C---- set 0.3" left,bottom margins
      CALL PLOTABS(0.3,0.3,-3)
      CALL NEWFACTOR(SIZE)
      CALL PLOT(6.0*CH,6.0*CH,-3)
C

c      WRITE(*,*) CPOLPLF(1,ICL),CPOLPLF(2,ICL),CPOLPLF(3,ICL)
c      write(*,*)

      CALL POLPLT(NAX,NPOL,NA,CPOLO,
     &            REYN,MACH,ACRIT,PTRAT,ETAP,
     &            NAME ,ICOL,ILIN,
     &            NFX,NDAT,NF,XYREF,LABREF,IFCOL,IFSYM,
     &            ISX,NBL,CPOLSD, IMATYP,IRETYP,
     &            TITLE,CODE,VERSION,
     &            PLOTAR, XCD,XAL,XOC, CH,CH2, CDLMOD(4,1),
     &            LGRID,LCDW,LLIST,LEGND,LAECEN,LCDH,LCMDOT,
     &            CPOLPLF, CCLEN,NCLEN )
C
c      CALL POLFIT(NAX,NPOL,NA,CPOLO,
c     &            REYN,MACH,ACRIT, NAME ,ICOL,ILIN,
c     &            IMATYP,IRETYP,
c     &            PLOTAR, XCD,XAL,XOC, CH,CH2, CDLMOD(4,1),
c     &            CPOLPLF, CCLEN,NCLEN )
C
      GO TO 5
C
C=============================================
C---- hardcopy output
 40   IF(LPLOT) CALL PLEND
      LPLOT = .FALSE.
      CALL REPLOT(IDEVRP)
      GO TO 5
C
C=============================================
C---- change settings
 50   CALL GETSET
      GO TO 5
C
C=============================================
C---- zoom
 60   CALL USETZOOM(.FALSE.,.TRUE.)
      CALL REPLOT(IDEV)
      GO TO 5
C
C=============================================
C---- unzoom
 70   CALL CLRZOOM
      CALL REPLOT(IDEV)
      GO TO 5
C
C=============================================
C---- annotate plot
 80   IF(.NOT.LPLOT) THEN
       WRITE(*,*) 'No active plot to annotate'
       GO TO 5
      ENDIF
      CALL ANNOT(CH)
      GO TO 5
C=============================================
C---- get modifiers
 90   CONTINUE
      WRITE(*,4900)
 4900 FORMAT(/' CD_plotted  = (CD  +  CD0 + CD1*CL + CD2*CL^2)*CL^expD'
     &       /' CL_plotted  =  CL^exp')
      DO IP = 1, NPOL
 91     WRITE(*,4910) IP, (CDLMOD(K,IP), K=1, 5)
 4910   FORMAT(/' Polar', I3,'...'
     &         /' Currently CD0,CD1,CD2,exp,expD = ', 3F10.6, 2F10.4,
     &         /' Input new CD0,CD1,CD2,exp,expD:    ', $)
        CALL READR(5,CDLMOD(1,IP),ERROR)
        IF(ERROR) GO TO 91
      ENDDO
      GO TO 5
C
C=============================================
C---- Make the Vz(V) Plot
 130  IF (NPOL.EQ.0 .AND. NDAT.EQ.0) GO TO 5
C
C---- sort each polar by increasing alpha
      DO IP=1, NPOL
        CALL PLRSRT(IP,IAL)
      ENDDO
C
C---- set V and Vz for plotting
      DO IP = 1, NPOL
        WOS = VPPARS(1,IP)
        RHO = VPPARS(2,IP)
        AR  = VPPARS(3,IP)
        CD0 = VPPARS(4,IP)
        REF = VPPARS(5,IP)
        REX = VPPARS(6,IP)
C
        IF(WOS .EQ. 0.0) THEN
         WRITE(*,*) 'Wing loading W/S not defined.  Using 1.0'
         WOS = 1.0
        ENDIF
        IF(RHO .EQ. 0.0) THEN
         WRITE(*,*) 'Air density RHO not defined.  Using 1.0'
         RHO = 1.0
        ENDIF
        IF(AR .EQ. 0.0) THEN
         WRITE(*,*) 'Aspect ratio AR not defined.  Using 1.0'
         AR = 1.0
        ENDIF
        IF(REF .EQ. 0.0) THEN
         WRITE(*,*) 'Reference REref not defined.  Using 10^6'
         REF = 1.0E6
        ENDIF
C
        DO IA = 1, NA(IP)
          CDP = CPOL(IA,ICD,IP)
          CL  = CPOL(IA,ICL,IP)
          RE  = CPOL(IA,IRE,IP)
C
          CLM = MAX( CL , 0.001 )
          VEL = SQRT( 2.0*WOS/(RHO*CLM) )
C
          CD = CDP
     &       + CL*CL/(PI*AR)
     &       + CD0*(RE/REF)**REX
C
          VZ = -VEL * CD/CL
C
          VPOLO(IA,1,IP) = VEL
          VPOLO(IA,2,IP) = VZ
        ENDDO
      ENDDO

      IF (LAUTO) THEN 
        CALL MINMAX(NAX,NPOL,NA,VPOLO,VPOLPLF)
        CALL SETINCV
      ENDIF
C
      IF (LPLOT) CALL PLEND
      CALL PLOPEN(SCRNFR,IPSLU,IDEV)
      LPLOT = .TRUE.
C
C---- set 0.3" left,bottom margins
      CALL PLOTABS(0.3,0.3,-3)
      CALL NEWFACTOR(SIZE)
      CALL PLOT(6.0*CH,6.0*CH,-3)
C
      CALL VEPPLT(NAX,NPOL,NA,VPOLO,
     &            REYN,MACH,ACRIT,PTRAT,ETAP,
     &            NAME ,ICOL,ILIN,
     &            IMATYP,IRETYP,
     &            TITLE,CODE,VERSION,
     &            PLOTAR, CH,CH2, 
     &            LGRID,LLIST,LEGND,
     &            VPOLPLF)
      GO TO 5
C
C=============================================
C---- get velocity-polar parameters
 190  CONTINUE
      DO IP = 1, NPOL
 191    WRITE(*,5910) IP, (VPPARS(K,IP), K=1, 6)
 5910   FORMAT(
     &  /' Polar', I3,'...'
     &  /' Currently W/S,rho,AR,CDo,REref,REexp = ', 
     &              G12.4,G12.4,F7.2,F10.6,G12.4,F6.2
     &  /' Input new W/S,rho,AR,CDo,REref,REexp:    ', $)
        CALL READR(6,VPPARS(1,IP),ERROR)
        IF(ERROR) GO TO 191
      ENDDO
      GO TO 5
C
C=============================================
  900 CALL PLCLOSE
      STOP
      END ! PPLOT


      SUBROUTINE GETCLEN(NAME,CLEN,NCLEN)
      CHARACTER*(*) NAME, CLEN
C--------------------------------------------------
C     Looks for substring  "(c=01234***)"
C     in the NAME string.  If found, then
C     the "***" string is returned in CLEN.
C     If not found, then CLEN is returned blank.
C--------------------------------------------------
C
      CLEN = ' '
C
      K1 = INDEX( NAME , '(c=' )
      IF(K1.EQ.0) RETURN
C
      NNAME = LEN(NAME)
      K2 = INDEX( NAME(K1:NNAME) , ')' ) + K1 - 2
      IF(K2-K1.LT.3) RETURN
C
      DO K = K1+3, K2
        IF(INDEX( '0123456789.,)' , NAME(K:K) ) .EQ. 0) THEN
         CLEN = NAME(K:K2)
         NCLEN = K2-K+1
         RETURN
        ENDIF
      ENDDO
C
      RETURN
      END

 

      SUBROUTINE MINMAX(NAX,NPOL,NA,CPOL,CPOLPLF)
      INCLUDE 'PINDEX.INC'
      DIMENSION NA(NPOL)
      DIMENSION CPOL(NAX,IPTOT,NPOL), CPOLPLF(3,*)
C--------------------------------------------
C     Determines max and min limits of polar
C     quantities among all polars passed in.
C--------------------------------------------
C
      IF(NPOL.LT.1) RETURN
C
      DO K = 1, 4
        CPOLPLF(1,K) = CPOL(1,K,1)
        CPOLPLF(2,K) = CPOL(1,K,1)
      END DO
C
      DO IP=1, NPOL
        DO K=1, 4
          DO I=1, NA(IP)
            CPOLPLF(1,K) = MIN( CPOL(I,K,IP) , CPOLPLF(1,K) )
            CPOLPLF(2,K) = MAX( CPOL(I,K,IP) , CPOLPLF(2,K) )
          END DO
        END DO
      END DO
C
      RETURN
      END ! MINMAX


 
      SUBROUTINE GETDEF
      INCLUDE 'PPLOT.INC'
      LOGICAL LERR
C
C---- Plotting flag
      IDEV = 1   ! X11 window only
c     IDEV = 2   ! B&W PostScript output file only (no color)
c     IDEV = 3   ! both X11 and B&W PostScript file
c     IDEV = 4   ! Color PostScript output file only 
c     IDEV = 5   ! both X11 and Color PostScript file 
C
C---- Re-plotting flag (for hardcopy)
c      IDEVRP = 2   ! B&W PostScript
      IDEVRP = 4   ! Color PostScript
C
C---- PostScript output logical unit and file specification
      IPSLU = 0  ! output to file  plot.ps   on LU 4    (default case)
c     IPSLU = ?  ! output to file  plot?.ps  on LU 80+?
C
C---- screen fraction taken up by plot window upon opening
      SCRNFR = 0.70
C
C---- Default plot size in inches
C-    (Default plot window is 11.0 x 8.5)
      SIZE = 10.0
C
C---- plot aspect ratio V/H
      PLOTAR = 0.60
C
C---- character height
      CH  = 0.014
      CH2 = 0.012
C
C---- set default color table and get number of colors
      CALL COLORMAPDEFAULT
      CALL GETNUMCOLOR(NCOLOR)
C
C---- default polar line types and colors
C
C     1  *****************************  SOLID
C     2  **** **** **** **** **** ****  LONG DASHED
C     3  ** ** ** ** ** ** ** ** ** **  SHORT DASHED
C     4  * * * * * * * * * * * * * * *  DOTTED
C     5  ***** * ***** * ***** * *****  DASH-DOT
C     6  ***** * * ***** * * ***** * *  DASH-DOT-DOT
C     7  ***** * * * ***** * * * *****  DASH-DOT-DOT-DOT
C     8  **** **** * * **** **** * *    DASH-DASH-DOT-DOT
C
C     3  red
C     4  orange
C     5  yellow
C     6  green
C     7  cyan
C     8  blue
C     9  violet
C    10  magenta
C
      DO IP=1, NPX
ccc       ILIN(IP) = 1 + MOD(IP-1,8
ccc       ICOL(IP) = 3 + MOD(IP-1,8)
C
C------ normally solid, going to dashed after IP=7
        ILIN(IP) = 1 + (IP-1)/7
C
C------ skip yellow (hard to see on white background)
        ICOL(IP) = 3 + MOD(IP-1,7)
        IF(ICOL(IP) .GE. 5) ICOL(IP) = ICOL(IP) + 1
      ENDDO
C
      LGRID = .TRUE.
      LCDW  = .FALSE.
      LLIST = .TRUE.
      LEGND = .TRUE.
      LCLEN = .FALSE.
      LAECEN = .FALSE.
      LCDH = .FALSE.
      LCMDOT = .FALSE.
C
C---- automatic scaling for axes
      LAUTO  = .TRUE.
C
      CPOLPLF(1,ICL) = 0.0   ! CLmax
      CPOLPLF(2,ICL) = 1.5   ! CLmin
      CPOLPLF(3,ICL) = 0.5   ! Axis CL increment
C         
      CPOLPLF(1,ICD) = 0.0   ! CDmax
      CPOLPLF(2,ICD) = 0.02  ! CDmin
      CPOLPLF(3,ICD) = 0.01  ! Axis CD increment
C         
      CPOLPLF(1,ICM) =  0.0  ! CMmax
      CPOLPLF(2,ICM) = -0.25 ! CMmin
      CPOLPLF(3,ICM) =  0.05 ! Axis CM increment
C         
      CPOLPLF(1,IAL) = -4.0  ! ALmax
      CPOLPLF(2,IAL) = 10.0  ! ALmin
      CPOLPLF(3,IAL) =  2.0  ! Axis AL increment
C
C---- Plot layout (relative X size to CL-CD, CL-alfa, transition plots)
      XCD = 0.45
      XAL = 0.25
      XOC = 0.20
C
C---- Set CL,CD modifiers
      DO IP = 1, NPX
        CDLMOD(1,IP) = 0.
        CDLMOD(2,IP) = 0.
        CDLMOD(3,IP) = 0.
        CDLMOD(4,IP) = 1.0
        CDLMOD(5,IP) = 0.
      ENDDO
C
cC---- Set CL,CD quadratic-fit polar parameters
c      DO IP = 1, NPX
c        CDLFIT(1,IP) = 0.
c        CDLFIT(2,IP) = 0.
c        CDLFIT(3,IP) = 0.
c        CDLFIT(4,IP) = 1.0
c        CDLFIT(5,IP) = 0.
c      ENDDO
C
C---- velocity polar plot axis parameters
      VPOLPLF(1,1) =  0.0  ! Vmin
      VPOLPLF(2,1) = 20.0  ! Vmax
      VPOLPLF(3,1) =  2.0  ! Vdel
C
      VPOLPLF(1,2) = -5.0  ! Vzmin
      VPOLPLF(2,2) =  1.0  ! Vzmax
      VPOLPLF(3,2) =  0.5  ! Vzdel
C
C---- Set Vz(V) parameters
      DO IP = 1, NPX
        VPPARS(1,IP) = 0.
        VPPARS(2,IP) = 0.
        VPPARS(3,IP) = 0.
        VPPARS(4,IP) = 0.
        VPPARS(5,IP) = 0.
        VPPARS(6,IP) = 0.
      ENDDO
C
C---- no CM location shift by default
      DO IP = 1, NPX
        DXMREF(IP) = 0.0
      ENDDO
C
      TITLE = '                                '
CCC            12345678901234567890123456789012
C
      RETURN
      END ! GETDEF


 
 
      SUBROUTINE RDDEF(LU,LERR)
C--- Read PPLOT plot parameters from save file
      INCLUDE 'PPLOT.INC'
      LOGICAL LERR
C
      CHARACTER*256 LINE
      LOGICAL LCOLH
C
      LCOLH = IDEVRP .EQ. 4
      SIZE0 = SIZE
C
 1000 FORMAT(A)
C
      READ(LU,*,ERR=90,END=80)
     &     CPOLPLF(1,ICL), CPOLPLF(2,ICL), CPOLPLF(3,ICL)
      READ(LU,*,ERR=90,END=80)
     &     CPOLPLF(1,ICD), CPOLPLF(2,ICD), CPOLPLF(3,ICD)
      READ(LU,*,ERR=90,END=80)
     &     CPOLPLF(1,ICM), CPOLPLF(2,ICM), CPOLPLF(3,ICM)
      READ(LU,*,ERR=90,END=80)
     &     CPOLPLF(1,IAL), CPOLPLF(2,IAL), CPOLPLF(3,IAL)
      READ(LU,*,ERR=90,END=80) XCD, XAL, XOC
      READ(LU,*,ERR=90,END=80) SIZE, PLOTAR
      READ(LU,*,ERR=90,END=80) CH, CH2
C
      READ(LU,*,ERR=90,END=80) LAUTO , LCDW 
      READ(LU,*,ERR=90,END=80) LLIST , LEGND
      READ(LU,*,ERR=90,END=80) LAECEN       
      READ(LU,*,ERR=90,END=80) LCMDOT, LCDH 
      READ(LU,*,ERR=90,END=80) LGRID , LCOLH
C
      READ(LU,1000,ERR=90,END=80) LINE
      KBAR = INDEX(LINE,'|') - 1
      IF(KBAR.LE.0) KBAR = LEN(LINE)
      READ(LINE(1:KBAR),*,ERR=90,END=80) (DXMREF(IP), IP=1, NPX)
C
      READ(LU,1000,ERR=90,END=80) LINE
      KBAR = INDEX(LINE,'|') - 1
      IF(KBAR.LE.0) KBAR = LEN(LINE)
      READ(LINE(1:KBAR),*,ERR=90,END=80) (ICOL(IP), IP=1, NPX)
C
      READ(LU,1000,ERR=90,END=80) LINE
      KBAR = INDEX(LINE,'|') - 1
      IF(KBAR.LE.0) KBAR = LEN(LINE)
      READ(LINE(1:KBAR),*,ERR=90,END=80) (ILIN(IP), IP=1, NPX)
C
      READ(LU,*,ERR=90,END=80) (VPOLPLF(K,1), K=1, 3)
      READ(LU,*,ERR=90,END=80) (VPOLPLF(K,2), K=1, 3)
C
C
      IF(LCOLH) THEN
       IDEVRP = 4
      ELSE
       IDEVRP = 2
      ENDIF
      IF(SIZE.LE.0.0) SIZE = SIZE0
C
      LERR = .FALSE.
      RETURN
C
 80   CONTINUE
 90   CONTINUE
      LERR = .TRUE.
      RETURN
      END ! RDDEF

 
      SUBROUTINE WRTDEF(LU)
C--- Write PPLOT plot parameters to save file
      INCLUDE 'PPLOT.INC'
      CHARACTER*256 LINE
      LOGICAL LCOLH
C
      LCOLH = IDEVRP .EQ. 4
C
 1000 FORMAT(A)
C
      WRITE(LU,1030) CPOLPLF(1,ICL), CPOLPLF(2,ICL), CPOLPLF(3,ICL),
     &               'CLmin   CLmax    dCL'
      WRITE(LU,1030) CPOLPLF(1,ICD), CPOLPLF(2,ICD), CPOLPLF(3,ICD),
     &               'CDmin   CDmax    dCD'
      WRITE(LU,1030) CPOLPLF(1,ICM), CPOLPLF(2,ICM), CPOLPLF(3,ICM),
     &               'CMmin   CMmax    dCM'
      WRITE(LU,1030) CPOLPLF(1,IAL), CPOLPLF(2,IAL), CPOLPLF(3,IAL),
     &               'ALmin   ALmax    dAL'
      WRITE(LU,1030) XCD, XAL, XOC,
     &               'CL-CD   CL-alpha  CL-Xtr  (widths)'
      WRITE(LU,1020) SIZE, PLOTAR,
     &               'width    height/width'
      WRITE(LU,1020) CH, CH2,
     &               'char_ht1 char_ht2'
 1010 FORMAT(1X, F9.4,9X,9X,' | ', A)
 1020 FORMAT(1X,2F9.4,9X   ,' | ', A)
 1030 FORMAT(1X,3F9.4      ,' | ', A)
C
      WRITE(LU,1120) LAUTO , LCDW  , 'auto_scale?  CDp_plot?'
      WRITE(LU,1120) LLIST , LEGND , 'airf_list?   legend_box?'
      WRITE(LU,1110) LAECEN,         'x_AC_plot?'
      WRITE(LU,1120) LCMDOT, LCDH  , 'HX_mass?     HX_CD?'
      WRITE(LU,1120) LGRID , LCOLH , 'grid_plot?   color_PS?'
 1110 FORMAT(1X,  L4,1X ,5X,5X,' | ', A)
 1120 FORMAT(1X,2(L4,1X),5X,   ' | ', A)
 1130 FORMAT(1X,3(L4,1X),      ' | ', A)
C
      WRITE(LINE,1300) (DXMREF(IP), IP=1, NPX)
 1300 FORMAT(1X,80(F7.3))
      CALL STRIP(LINE,NLINE)
      LINE = LINE(1:NLINE) // ' | dXmom_ref'
      CALL STRIP(LINE,NLINE)
      WRITE(LU,1000) LINE(1:NLINE)
C
      WRITE(LINE,1400) (ICOL(IP), IP=1, NPX)
      CALL STRIP(LINE,NLINE)
      LINE = LINE(1:NLINE) // ' | line_color'
      CALL STRIP(LINE,NLINE)
      WRITE(LU,1000) LINE(1:NLINE)
C
      WRITE(LINE,1400) (ILIN(IP), IP=1, NPX)
      CALL STRIP(LINE,NLINE)
      LINE = LINE(1:NLINE) // ' | line_type'
      CALL STRIP(LINE,NLINE)
      WRITE(LU,1000) LINE(1:NLINE)
C
 1400 FORMAT(1X,80I4)
C
      WRITE(LU,1030) (VPOLPLF(K,1), K=1, 3), 'V_scale'
      WRITE(LU,1030) (VPOLPLF(K,2), K=1, 3), 'Vz_scale'
C
      RETURN
      END ! WRTDEF
 


      SUBROUTINE GETSET
      INCLUDE 'PPLOT.INC'
      LOGICAL OK, ERROR
      LOGICAL LCOLH
      CHARACTER*1 ANS
      CHARACTER*2 OPTION
      CHARACTER*80 LINE
      REAL RINP(10)
C
C---- Change plotting parameters
C
    1 CONTINUE
      LCOLH = IDEVRP .EQ. 4
C
      WRITE(*,1000)
     &  LAUTO, LCDW, LLIST, LEGND, LAECEN, LCMDOT, LCDH, LGRID, LCOLH
C
 1000 FORMAT(/ '  1   Change CL scaling'
     &       / '  2   Change CD scaling'
     &       / '  3   Change CM scaling'
     &       / '  4   Change ALPHA scaling'
     &      // '  5   Plot Layout'
     &       / '  6   Plot Title'
     &       / '  7   Plot Size'
     &      // ' 10',L3,' autoscaling?'
     &       / ' 11',L3,' plot pressure-CD?'
     &       / ' 12',L3,' plot airfoil list?'
     &       / ' 13',L3,' plot CL-CD legend box?'
     &       / ' 14',L3,' plot aero. center?'
     &       / ' 15',L3,' plot streamtube mass coeff.?'
     &       / ' 16',L3,' plot streamtube thrust?'
     &       / ' 18',L3,' plot grid overlay?'
     &       / ' 19',L3,' color hardcopy?'
     &      // ' 20   Rescale forces by chord factor'
     &       / ' 21   Change reference-length unit'
     &       / ' 22   Change moment-reference x/c'
     &       / ' 23   Change polar colors'
     &       / ' 24   Change polar line styles'
     &      // ' 26   Change V  scaling'
     &       / ' 27   Change Vz scaling'
     &      // ' 30   Read  settings from defaults file'
     &       / ' 31   Write settings to   defaults file'
     &      // '    Select option:  ',$)
C
      READ(*,1005) OPTION
 1005 FORMAT(A)
C
      IF(OPTION .EQ. ' ' .OR. OPTION.EQ.'0 ') THEN
C
        RETURN
C
      ELSE IF(OPTION.EQ.'1 ') THEN
C--- Get CL min,max,delta
        WRITE(*,1100) (CPOLPLF(K,ICL), K=1, 3)
 20     READ(*,1005)  LINE
        NINP = 3
        CALL GETFLT(LINE,CPOLPLF(1,ICL),NINP,ERROR)
        IF(ERROR) GO TO 20
        IF(NINP.EQ.0) GO TO 1
        LAUTO = .FALSE.
C
      ELSE IF(OPTION.EQ.'2 ') THEN
C--- Get CD min,max,delta
        WRITE(*,1200) (CPOLPLF(K,ICD), K=1, 3)
 30     READ(*,1005)  LINE
        NINP = 3
        CALL GETFLT(LINE,CPOLPLF(1,ICD),NINP,ERROR)
        IF(ERROR) GO TO 30
        IF(NINP.EQ.0) GO TO 1
        LAUTO = .FALSE.
C
      ELSE IF(OPTION.EQ.'3 ') THEN
C--- Get CM min,max,delta
        WRITE(*,1300) (CPOLPLF(K,ICM), K=1, 3)
 40     READ(*,1005)  LINE
        NINP = 3
        CALL GETFLT(LINE,CPOLPLF(1,ICM),NINP,ERROR)
        IF(ERROR) GO TO 40
        IF(NINP.EQ.0) GO TO 1
        LAUTO = .FALSE.
C
      ELSE IF(OPTION.EQ.'4 ') THEN
C--- Get ALFA min,max,delta
        WRITE(*,1400) (CPOLPLF(K,IAL), K=1, 3)
 50     READ(*,1005)  LINE
        NINP = 3
        CALL GETFLT(LINE,CPOLPLF(1,IAL),NINP,ERROR)
        IF(ERROR) GO TO 50
        IF(NINP.EQ.0) GO TO 1
        LAUTO = .FALSE.
C
      ELSE IF(OPTION.EQ.'5 ') THEN
C--- Get Layout offsets for CL-CD,CL-alfa,transition plot sections
 80     WRITE(*,1700) XCD,XAL,XOC
        READ(*,1005)  LINE
        RINP(1) = XCD
        RINP(2) = XAL
        RINP(3) = XOC
        NINP = 3
        CALL GETFLT(LINE,RINP,NINP,ERROR)
        IF(ERROR) GO TO 80
        IF(NINP.EQ.0) GO TO 1
        XCD = RINP(1)
        XAL = RINP(2)
        XOC = RINP(3)
C
      ELSE IF(OPTION.EQ.'6 ') THEN
C--- Get plot title
        TITLE = ' '
        CALL ASKS('Enter plot title (80 chars)^',TITLE)
        CALL STRIP(TITLE,NTITLE)
C
      ELSE IF(OPTION.EQ.'7 ') THEN
C--- Get plot size
 60     WRITE(*,1500) SIZE
        READ(*,1005)  LINE
        IF(LINE.EQ.' ') GO TO 1
        READ(LINE,*,ERR=60) SIZE
C
      ELSE IF(OPTION.EQ.'10') THEN
        LAUTO = .NOT. LAUTO
C
      ELSE IF(OPTION.EQ.'11') THEN
        LCDW = .NOT. LCDW
C
      ELSE IF(OPTION.EQ.'12') THEN
        LLIST = .NOT. LLIST
C
      ELSE IF(OPTION.EQ.'13') THEN
        LEGND = .NOT. LEGND
C
      ELSE IF(OPTION.EQ.'14') THEN
        LAECEN = .NOT. LAECEN
C
      ELSE IF(OPTION.EQ.'15') THEN
        LCMDOT = .NOT. LCMDOT
C
      ELSE IF(OPTION.EQ.'16') THEN
        LCDH = .NOT. LCDH
C
      ELSE IF(OPTION.EQ.'18') THEN
        LGRID = .NOT. LGRID
C
      ELSE IF(OPTION.EQ.'19') THEN
C--- Color hardcopy toggle
        IF(IDEVRP.EQ.2) THEN
          IDEVRP = 4
         ELSE
          IDEVRP = 2
        ENDIF
C
      ELSE IF(OPTION.EQ.'20') THEN
C--- rescale forces and moments
      WRITE(*,1900)
      SCAL = 1.0
      READ(*,1005) LINE
      IF(LINE.EQ.' ') GO TO 1
      READ(LINE,*,ERR=1,END=1) CSCAL
      IF(SCAL.NE.0.0) CALL RESCAL(1.0/SCAL)
C
      ELSE IF(OPTION.EQ.'21') THEN
C--- change reference length unit
        WRITE(*,2000)
        CALL ASKS(
     &   'Enter new reference length unit (<return> if none)^',CCLEN)
        CALL STRIP(CCLEN,NCLEN)
C
      ELSE IF(OPTION.EQ.'22') THEN
C--- change moment reference locations
        IF(NPOL.EQ.0) THEN
         WRITE(*,*) 'No current polars'
         GO TO 1
        ELSE
         WRITE(*,*)
         WRITE(*,*) 'Enter new moment-reference location shifts...'
         DO IP = 1, NPOL
           WRITE(*,8010) IP, DXMREF(IP)
 8010      FORMAT('  New dXref for polar', I3,' [',F9.4,' ] : ', $)
           CALL READR(1,DXMREF(IP),ERROR)
         ENDDO
        ENDIF
C
      ELSE IF(OPTION.EQ.'23') THEN
C------ change polar colors
        IF(NPOL.EQ.0) THEN
         WRITE(*,*) 'No current polars to change'
         GO TO 1
        ELSE
         WRITE(*,5020)
 5020    FORMAT(
     &   / '   1  black (white in revVideo)'
     &   / '   2  white (invisible)'
     &   / '   3  red'
     &   / '   4  orange'
     &   / '   5  yellow'
     &   / '   6  green'
     &   / '   7  cyan'
     &   / '   8  blue'
     &   / '   9  violet'
     &   / '  10  magenta' )
C
 820     WRITE(LINE,3100) 'polar colors',
     &                    (ICOL(IP), IP=1, NPOL)
         WRITE(*,1005) LINE
         WRITE(*,3105)    'polar colors'
         READ(*,1005) LINE
         NINP = NPOL
         CALL GETINT(LINE,ICOL,NINP,ERROR)
         IF(ERROR) GO TO 820
        ENDIF
C
      ELSE IF(OPTION.EQ.'24') THEN
C------ change polar line styles
        IF(NPOL.EQ.0) THEN
         WRITE(*,*) 'No current polars to change'
         GO TO 1
        ELSE
         WRITE(*,5030)
 5030    FORMAT(
     &   / '   1  -----------------------------  solid'
     &   / '   2  ---- ---- ---- ---- ---- ----  long dashed'
     &   / '   3  -- -- -- -- -- -- -- -- -- --  short dashed'
     &   / '   4  - - - - - - - - - - - - - - -  dotted'
     &   / '   5  ----- - ----- - ----- - -----  dash-dot'
     &   / '   6  ----- - - ----- - - ----- - -  dash-dot-dot'
     &   / '   7  ----- - - - ----- - - - -----  dash-dot-dot-dot'
     &   / '   8  ---- ---- - - ---- ---- - -    dash-dash-dot-dot')
C
 830     WRITE(LINE,3100) 'current polar line styles', 
     &                     (ILIN(IP), IP=1, NPOL)
         WRITE(*,1005) LINE
         WRITE(*,3105)    ' select polar line styles'
         READ(*,1005) LINE
         NINP = NPOL
         CALL GETINT(LINE,ILIN,NINP,ERROR)
         IF(ERROR) GO TO 830
        ENDIF
C
      ELSE IF(OPTION.EQ.'26') THEN
C--- Get V min,max,delta
        WRITE(*,2100) (VPOLPLF(K,1), K=1, 3)
 210    READ(*,1005)  LINE
        NINP = 3
        CALL GETFLT(LINE,VPOLPLF(1,1),NINP,ERROR)
        IF(ERROR) GO TO 210
        IF(NINP.EQ.0) GO TO 1
        LAUTO = .FALSE.
C
      ELSE IF(OPTION.EQ.'27') THEN
C--- Get Vz min,max,delta
        WRITE(*,2200) (VPOLPLF(K,2), K=1, 3)
 220    READ(*,1005)  LINE
        NINP = 3
        CALL GETFLT(LINE,VPOLPLF(1,2),NINP,ERROR)
        IF(ERROR) GO TO 220
        IF(NINP.EQ.0) GO TO 1
        LAUTO = .FALSE.
C
      ELSE IF(OPTION.EQ.'30') THEN
C--- Read defaults from pplot.def file
        LINE = 'Enter settings filename  [pplot.def] ^'
        CALL ASKS(LINE,FNAME)
        IF(FNAME.EQ.' ') FNAME = 'pplot.def'
        LU = 10
        OPEN(LU,FILE=FNAME,STATUS='OLD',ERR=703)
        CALL RDDEF(LU,ERROR)
        CLOSE(LU)
        GO TO 1
 703    WRITE(*,*) 
        WRITE(*,*) 'Open error on pplot defaults file'
        GO TO 1
C
      ELSE IF(OPTION.EQ.'31') THEN
C--- Save defaults to parameter file
        LU = 10
        LINE = 'Enter settings filename  [ pplot.def ] ^'
        CALL ASKS(LINE,FNAME)
        IF(FNAME.EQ.' ') FNAME = 'pplot.def'
        OPEN(LU,FILE=FNAME,STATUS='OLD',ERR=803)
        WRITE(*,*)
        WRITE(*,*) 'File exists.  Overwrite?  Y'
        READ(*,1001) ANS
        IF(INDEX('Nn',ANS) .EQ. 0) GO TO 806
        WRITE(*,*)
        WRITE(*,*) 'No action taken'
        CLOSE(LU)
        GO TO 1
C
 803    OPEN(LU,FILE=FNAME,STATUS='UNKNOWN')
 806    REWIND(LU)
        CALL WRTDEF(LU)
        WRITE(*,*)
        WRITE(*,*) 'PPLOT plot settings written to file'
        CLOSE(LU)
C
      ENDIF
      GO TO 1
C
 1001 FORMAT(A)
 1100 FORMAT(/' Current   CLmin, CLmax, dCL = ',3F10.5
     &       /' Enter new CLmin, CLmax, dCL:  ',$)
 1200 FORMAT(/' Current   CDmin, CDmax, dCD = ',3F10.5
     &       /' Enter new CDmin, CDmax, dCD:  ',$)
 1300 FORMAT(/' Current   CMmin, CMmax, dCM = ',3F10.5
     &       /' Enter new CMmin, CMmax, dCM:  ',$)
 1400 FORMAT(/' Current   ALmin, ALmax, dAL = ',3F10.5
     &       /' Enter new ALmin, ALmax, dAL:  ',$)
 1500 FORMAT(/' Current   plot size = ', F10.5
     &       /' Enter new plot size:  ',$)
 1700 FORMAT(/'  Current layout offsets  xCD =',F8.4,
     &        '  xALPHA = ',F8.4,'  xTR = ',F8.4/
     &        ' Enter new xCD, xALPHA, xTR:  ',$)
 1800 FORMAT(/' Default settings file: ',A)
 1900 FORMAT(/'Enter chord scale factor for forces: ',$)
 1910 FORMAT(/'Enter moment reference x/c [', F8.3, ' ]: ',$)
 2000 FORMAT(/'Current reference length unit: ', A)

 2100 FORMAT(/' Current   Vmin, Vmax, dV = ',3F10.5
     &       /' Enter new Vmin, Vmax, dV:  ',$)
 2200 FORMAT(/' Current   Vzmin, Vzmax, dVz = ',3F10.5
     &       /' Enter new Vzmin, Vzmax, dVz:  ',$)
C
 3000 FORMAT(' Currently ',A,' =', 20F8.4)
 3100 FORMAT(' Currently ',A,' =', 20I3)
 3105 FORMAT(' Enter new ',A,':  ',$)
C
      END ! GETSET



      SUBROUTINE PLRSRT(IP,IDSORT)
      INCLUDE 'PPLOT.INC'
      DIMENSION INDX(NAX), ATMP(NAX)
C
C---- sort polar in increasing variable IDSORT
      CALL HSORT(NA(IP),CPOL(1,IDSORT,IP),INDX)
C
C---- do the actual reordering
      DO ID = 1, IPTOT
        CALL ASORT(NA(IP),CPOL(1,ID,IP),INDX,ATMP)
      ENDDO
      DO ID = 1, JPTOT
        DO IS = 1, 2
          CALL ASORT(NA(IP),CPOLSD(1,IS,ID,IP),INDX,ATMP)
        ENDDO
      ENDDO
C
      RETURN
      END ! PLRSRT
 


      SUBROUTINE GETTYP(NAX,NA,CPOL, IMATYP,IRETYP )
C
C---- Determines type of Ma(CL) and Re(CL) dependence
C
      INCLUDE 'PINDEX.INC'
C
      DIMENSION CPOL(NAX,IPTOT)
C
      IF(CPOL(NA,ICL)*CPOL(1,ICL) .LE. 0.0) THEN
        IMATYP = 1
        IRETYP = 1
        RETURN
      ENDIF
C
      IF(CPOL(NA,IMA)*CPOL(1,IMA) .LE. 0.0) THEN
        IMATYP = 1
      ELSE
        EX = LOG( CPOL(NA,IMA)/CPOL(1,IMA) )
     &     / LOG( CPOL(NA,ICL)/CPOL(1,ICL) )
        IF     (ABS(EX) .LT. 0.25) THEN
          IMATYP = 1
        ELSEIF (ABS(EX) .LT. 0.75) THEN
          IMATYP = 2
        ELSE
          IMATYP = 3
        ENDIF
      ENDIF
C
      IF(CPOL(NA,IRE)*CPOL(1,IRE) .LE. 0.0) THEN
        IRETYP = 1
      ELSE
        EX = LOG( CPOL(NA,IRE)/CPOL(1,IRE) )
     &     / LOG( CPOL(NA,ICL)/CPOL(1,ICL) )
        IF     (ABS(EX) .LT. 0.25) THEN
          IRETYP = 1
        ELSEIF (ABS(EX) .LT. 0.75) THEN
          IRETYP = 2
        ELSE
          IRETYP = 3
        ENDIF
      ENDIF
C
      RETURN
      END ! GETTYP


      SUBROUTINE RESCAL(SCAL)
      INCLUDE 'PPLOT.INC'
C--------------------------------------------
C     Rescales forces and moments
C--------------------------------------------
C---- rescale polar forces by SCAL, moments by SCAL**2
      DO IP=1, NPOL
        DO I=1, NA(IP)
          CPOL(I,ICL,IP) = CPOL(I,ICL,IP)*SCAL
          CPOL(I,ICD,IP) = CPOL(I,ICD,IP)*SCAL
          CPOL(I,ICW,IP) = CPOL(I,ICW,IP)*SCAL
          CPOL(I,ICM,IP) = CPOL(I,ICM,IP)*SCAL*SCAL
        END DO
        DXMREF(IP) = DXMREF(IP)*SCAL
      END DO
C
      RETURN
      END

 
      SUBROUTINE SETINC
      INCLUDE 'PPLOT.INC'
C--------------------------------------------
C     Determines axes increments for polars
C     from quantities for all polars read in.
C--------------------------------------------
C
      CLMAX = CPOLPLF(2,ICL)
      CLMIN = CPOLPLF(1,ICL)
      CDMAX = CPOLPLF(2,ICD)
      CDMIN = CPOLPLF(1,ICD)
      CMMAX = CPOLPLF(2,ICM)
      CMMIN = CPOLPLF(1,ICM)
      ALMAX = CPOLPLF(2,IAL)
      ALMIN = CPOLPLF(1,IAL)
C
C--- CL axes
      CALL AXISADJ2(CLMIN,CLMAX,CLSPAN,DCL,NCLTICS)
C--- CD axes
      CDMIN = 0.0
      CALL AXISADJ2(CDMIN,CDMAX,CDSPAN,DCD,NCDTICS)
C--- CM axes
      IF(ABS(CMMAX).GT.ABS(CMMIN)) THEN
        CMMIN = 0.0
       ELSE
        CMMAX = 0.0
      ENDIF
      CALL AXISADJ2(CMMIN,CMMAX,CMSPAN,DCM,NCMTICS)
c      write(*,*) 'cmmin,cmmax ',cmmin,cmmax
c      write(*,*) 'dcm,ncmtics ',dcm,ncmtics
C--- ALFA axes
      ALMIN = MIN(0.0,ALMIN)
      CALL AXISADJ2(ALmin,ALmax,ALspan,dAL,nALtics)
      IF(ALMIN.EQ.0.0) ALMIN = -DAL
C
      CPOLPLF(2,ICL) = CLMAX
      CPOLPLF(1,ICL) = CLMIN
      CPOLPLF(3,ICL) = DCL
      CPOLPLF(2,ICD) = CDMAX
      CPOLPLF(1,ICD) = CDMIN
      CPOLPLF(3,ICD) = DCD
      CPOLPLF(2,ICM) = CMMAX
      CPOLPLF(1,ICM) = CMMIN
      CPOLPLF(3,ICM) = DCM
      CPOLPLF(2,IAL) = ALMAX
      CPOLPLF(1,IAL) = ALMIN
      CPOLPLF(3,IAL) = DAL
C
      RETURN
      END ! SETINC


      SUBROUTINE SETINCV
      INCLUDE 'PPLOT.INC'
C--------------------------------------------
C     Determines axes increments for polars
C     from quantities for all polars read in.
C--------------------------------------------
C
      VHMAX = VPOLPLF(2,1)
      VHMIN = VPOLPLF(1,1)
      VZMAX = VPOLPLF(2,2)
      VZMIN = VPOLPLF(1,2)
C
C---- V axes
      CALL AXISADJ2(VHMIN,VHMAX,VHSPAN,DVH,NVHTICS)
C
C---- Vz axes
      VZMIN = 0.0
      CALL AXISADJ2(VZMIN,VZMAX,VZSPAN,DVZ,NVZTICS)
C
      VPOLPLF(2,1) = VHMAX
      VPOLPLF(1,1) = VHMIN
      VPOLPLF(3,1) = DVH
      VPOLPLF(2,2) = VZMAX
      VPOLPLF(1,2) = VZMIN
      VPOLPLF(3,2) = DVZ
C
      RETURN
      END ! SETINCV


      subroutine AXISADJ2(xmin,xmax,xspan,deltax,ntics)
C...Make scaled axes with engineering increments between tics
C
C   Input:    xmin, xmax - input range for which scaled axis is desired
C
C   Output:   xmin, xmax - adjusted range for scaled axis
C             xspan      - adjusted span of scaled axis
C             deltax     - increment to be used for scaled axis
C             nincr      - number of tics to be used on axis
C                          note that ntics=1+(xspan/deltax)
C
      real    xmin,xmax,xspan,deltax,xinc,xinctbl(4)
      integer ntics,i
      data    xinctbl / 0.1, 0.2, 0.5, 1. /
c
      xspan1 = xmax-xmin
      if (xspan1.eq.0.) xspan1 = 1.
c
      xpon = ifix(log10(xspan1))
      xspan = xspan1 / 10.**xpon
c
      do i = 1, 4
        xinc = xinctbl(i)
        ntics = 1 + ifix(xspan/xinc + 0.1)
        if (ntics.LE.6) go to 1
      end do
c
   1  deltax = xinc*10.**xpon
      xmin = deltax*  ifloor2(xmin/deltax)
      xmax = deltax*iceiling2(xmax/deltax)
      xspan = xmax - xmin
      ntics = 1 + ifix(xspan/xinc + 0.1)
      return
      end

      function iceiling2(x)
c--- returns next highest integer value if fraction is non-zero 
      integer iceiling2
      real x
      i = ifix(x)
      if(x-i.GT.0.) i = i+1
      iceiling2 = i
      return
      end

      function ifloor2(x)
c--- returns next lowest integer value if fraction is negative, non-zero
      integer ifloor2
      real x
      i = ifix(x)
      if(x-i.LT.0.) i = i-1
      ifloor2 = i
      return
      end

