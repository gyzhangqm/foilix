http://web.mit.edu/drela/Public/web/xfoil/

XFOIL is an interactive program for the design and analysis of subsonic isolated airfoils.
It consists of a collection of menu-driven routines which perform various useful functions such as:

    Viscous (or inviscid) analysis of an existing airfoil, allowing
        forced or free transition
        transitional separation bubbles
        limited trailing edge separation
        lift and drag predictions just beyond CLmax
        Karman-Tsien compressibility correction
        fixed or varying Reynolds and/or Mach numbers 
    Airfoil design and redesign by interactive modification of surface speed distributions, in two methods:
        Full-Inverse method, based on a complex-mapping formulation
        Mixed-Inverse method, an extension of XFOIL's basic panel method 
    Airfoil redesign by interactive modification of geometric parameters such as
        max thickness and camber, highpoint position
        LE radius, TE thickness
        camber line via geometry specification
        camber line via loading change specification
        flap deflection
        explicit contour geometry (via screen cursor) 
    Blending of airfoils
    Writing and reading of airfoil coordinates and polar save files
    Plotting of geometry, pressure distributions, and multiple polars

Release Conditions

    XFOIL is released under the GNU General Public License.
    By downloading the software you agree to abide by the GPL conditions. 

The most important conditions are:

    You may copy, modify and redistribute XFOIL or its modifications freely.
    Any such redistributions must be done under the terms of the GPL, else the permission is withdrawn. 

Announcements

    An Xfoil electronic bulletin board has been created at YahooGroups.
    The intent is to exchange information on Xfoil and other aero software.
    A Belorussian translation of this webpage has been created by Bohdan Zograf.
    A German translation of this webpage has been created by Alexey Gnatuk.
    A French translation of this webpage has been created by Kate Bondareva.
    A Polish translation of this webpage has been created by Alice Slaba. 

Software

    xfoil6.97.tar.gz (3972497 bytes)
    Xfoil 6.97 for Unix and Win32.
    Xfoil for Mac-OSX
    An independent 3rd-party build. Also at http://xfoil4mac.altervista.org/
    xfoil6.99.tgz (4515991 bytes)
    Xfoil 6.99 for Unix and Win32. Gzipped directory tar image.
    All source code, Orr-Sommerfeld database, plain text version of User Guide, sample Xfoil session inputs.
    Requires Fortran 77, C compilers, windowing support.
    XFOIL6.99.zip (3813300 bytes)
    Xfoil 6.99 for Windows.
    xfoilP3.zip (508267 bytes)
    Xfoil 6.94 executable for Win32, optimized for Pentium 3.
    xfoilP4.zip (531947 bytes)
    Xfoil 6.94 executable for Win32, optimized for Pentium 4.
    Pplot.zip (289812 bytes)
    Pplot executable for Win32 (optional separate polar save-file plotter).
    Pxplot.zip (281493 bytes)
    Pxplot executable for Win32 (optional separate polar dump-file plotter). 

Note: The source code for Xfoil itself is the same for Unix and Win32. The plot library directory (plotlib) has a separate win32 subdirectory. See all the README files for more info. Win32 Notes: Interaction with Win32 XFOIL is through a DOS-type text console window. Some of Microsoft's Win32 OS'es (Win95/98/ME) have limitations on # of lines in a console window and cannot fully display XFOIL menus or output. Win95/98/ME also have other shortcomings with regard to resource usage and stability although XFOIL runs under these OS'es. Windows NT, Win2000 and Windows XP are the recommended Win32 platforms.
Win32 Exe Notes: The executables for Win32 were compiled using the Intel Fortran Compiler 5.01-15 and Visual C++6.0. The Intel compiler (thanks to Tom Clarkson at Intel) was used to optimize executables for P3 and P4 Pentium architectures. The XFOIL executables should run on any Win32 Pentium-class machine as compiler options were used to include both optimized code and generic Pentium or AMD processor code for portability.
Documents

    xfoil_doc.txt (78602 bytes).
    User Guide in plain text.
    dataflow.pdf (11261 bytes).
    Data flow diagram.
    sessions.txt
    Sample Xfoil session inputs.
    version_notes.txt
    Summary of changes made for recent Xfoil versions. 


Author:
- Mark Drela drela (AT) mit (DOT) edu, (also Harold Youngren guppy (AT) maine (DOT) rr (DOT) com)

----------------
Page Revisions

December 11, 2000
- Page created
- Xfoil 6.91 (Unix)

January 11, 2001
- Xfoil 6.92 (Unix and Win32)
- Added this revision list
- Added Xfoil version changes text link
January 16, 2001
- Fixed incorrect xfoil.zip link (it was to an older 6.8 version)
- Added note on text color problem with 32-bit display depth

January 26, 2001
- Added link to Xfoil discussion Egroup

April 30, 2001
- Xfoil 6.93 (Unix and Win32)
- Changed link to Egroup, which got gobbled up by Yahoo

December 18, 2001
- Xfoil 6.94 (Unix and Win32)

November 22, 2005
- Xfoil 6.96 (Unix)

December 8, 2005
- Xfoil 6.96 (Unix) -- Added missing /osrc directory

May 3, 2006
- Xfoil 6.96 (Win32)

July 20, 2006
- Removed links to PS and PDF versions of User Guide (not up to date). Added link to data flow diagram.

February 28, 2007
- Modified the GPL summary above. Previously this wasn't a correct GPL interpretation, as discussed here .

June 26, 2007
- Added a description of the INTE command operations to the xfoil_doc.txt file.

Feb 17, 2008
- Added link to Mac-OSX version of Xfoil.

April 7, 2008
- Xfoil 6.97 (Unix)

Dec 23, 2013
- Xfoil 6.99 (Unix, Windows) 