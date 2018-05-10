# coding : utf-8

"""This file contains all code necessary for interfacing with XFOIL.

The Xfoil class circumvents blocking problems (caused by the interactive nature
of XFOIL) by using the NonBlockingStreamReader class, that runs the blocking
some_xfoil_subprocess.stdout.readline() call in a separate thread,
exchanging information with it using a queue.

This enables the Xfoil class to interact with XFOIL, and to read polars from
stdout instead of having to write a file to disk, eliminating latency there.
(Airfoil data still needs to be read from a file by XFOIL.)

Multiple XFOIL subprocesses can be run simultaneously, simply by constructing
the Xfoil class multiple times.

As such, this is probably the fastest and most versatile XFOIL automation
script out there.
(I've seen a good MATLAB implementation, but it still relied on files for 
output, and was not interactive.)

"""

from __future__ import print_function, division

from time import sleep
import subprocess as subp
import os.path
import re
import logging
from threading import Thread


try:
    import queue
except ImportError:
    import Queue as queue

import numpy as np

logger = logging.getLogger(__name__)


def oper_visc_alpha(*args, **kwargs):
    r"""Wrapper for _oper_visc to iterate over a range of angles of attack.

    Parameters
    ----------
    args : positional parameters
        airfoil : Airfoil file or NACA xxxx(x) if gen_naca flag set.
        operating_point : Single value or list of [start, stop, interval].
        Re : Reynolds number
    kwargs : keyword parameters
        Mach : Mach number
        normalize : Normalize airfoil through NORM command
        show_seconds
        iterlim : Set a new iteration limit (XFOIL standard is 10)
        n_crit : set Ncrit (turbulence level) to the specified value

    """
    # logging
    logger.debug("Call to oper_visc_alpha")
    for arg in args:
        logger.debug("oper_visc_alpha arg param : %s" % str(arg))
    for key, value in kwargs.items():
        logger.debug("oper_visc_alpha kwarg param : %s : %s" % (str(key),
                                                                str(value)))

    return _oper_visc(["ALFA", "ASEQ"], *args, **kwargs)


def oper_visc_cl(*args, **kwargs):
    r"""Wrapper for _oper_visc to iterate over a range of Cl

    Parameters
    ----------
    args : positional parameters
        airfoil : Airfoil file or NACA xxxx(x) if gen_naca flag set.
        operating_point : Single value or list of [start, stop, interval].
        Re : Reynolds number
    kwargs : keyword parameters
        Mach : Mach number
        normalize : Normalize airfoil through NORM command
        show_seconds
        iterlim : Set a new iteration limit (XFOIL standard is 10)
        n_crit : set Ncrit (turbulence level) to the specified value

    """
    # logging
    logger.debug("Call to oper_visc_cl")
    for arg in args:
        logger.debug("oper_visc_cl arg param : %s" % str(arg))
    for key, value in kwargs.items():
        logger.debug("oper_visc_cl kwarg param : %s : %s" % (str(key),
                                                             str(value)))

    return _oper_visc(["Cl", "CSEQ"], *args, **kwargs)


def _oper_visc(pcmd,
               airfoil,
               operating_point,
               reynolds,
               mach=None,
               normalize=True,
               show_seconds=None,
               iterlim=None,
               gen_naca=False,
               n_crit=9.0):
    r"""Convenience function that returns polar for specified airfoil and 
    Reynolds number for (range of) alpha or cl.
    Waits on XFOIL to finish so is blocking.

    Parameters
    ----------
    pcmd : list[str]
        xfoil commands sequence
    airfoil : str
        Airfoil file or NACA xxxx(x) if gen_naca flag set.
    alpha/Cl : float or list[float]
        Single value or list of [start, stop, interval].
    reynolds : float
        Reynolds number

    mach : float or None, optional (default is None)
        Mach number
    normalize : bool (optional, default is True)
        Normalize airfoil through NORM command
        From XFoil documentation:
        XFOIL will normally perform all operations on an airfoil with the
        same shape and location in cartesian space as the input airfoil.
        However, if the normalization flag is set (toggled with the NORM
        command), the airfoil coordinates will be immediately normalized
        to unit chord and the leading edge will be placed at the origin.
        A message is printed to remind the user.
    show_seconds : int or None (optional, default is None)
        If None, do not show graphics
        If int, show graphic for show_seconds seconds
    iterlim : int or None (optional, default is None)
        Set a new iteration limit (XFOIL standard is 10)
    gen_naca : bool (optional, default is False)
        Generate airfoil='NACA xxxx(x)' within XFOIL
    n_crit : float (optional, default is 9.0)
        set Ncrit (turbulence level) to the specified value

    Returns
    -------
    (data_array, data_header, infodict)
        data_array, numpy.ndarray
            [[ 0.       0.0073   0.05392  0.04414 -0.0012   0.929    0.9309 ]]
        data_header, list
            ['alpha', 'CL', 'CD', 'CDp', 'CM', 'Top_Xtr', 'Bot_Xtr']
        infodict, dict
            {'Ncrit': 9.0, 'Mach': 0.0, 'xtrf_bottom': 1.0,
             'Re': 59000.0, 'xtrf_top': 1.0}

    """
    # Circumvent different current working directory problems using __file__ dir
    # xf = Xfoil(os.path.dirname(os.path.realpath(__file__)))
    with Xfoil(os.path.dirname(os.path.realpath(__file__))) as xf:
        # Disable the xfoil 'popup'
        xf.cmd("PLOP\nG\n\n", autonewline=False)

        if normalize:  # True by default
            xf.cmd("NORM")

        if gen_naca:  # False by default
            xf.cmd(airfoil)  # Generate NACA
        else:
            # load from file
            xf.cmd('LOAD {}\n\n'.format(airfoil), autonewline=False)

        if not show_seconds:
            # Disable G(raphics) flag in Plotting options
            xf.cmd("PLOP\nG\n\n", autonewline=False)

        xf.cmd("OPER")  # Enter OPER menu

        xf.cmd("VPAR")  # VPAR is in the OPER menu
        xf.cmd("N {:.3f}".format(n_crit))  # Set Ncrit
        xf.cmd("")  # back to the OPER menu

        if iterlim:
            xf.cmd("ITER {:.0f}".format(iterlim))
        xf.cmd("VISC {}".format(reynolds))

        if mach:
            xf.cmd("MACH {:.3f}".format(mach))

        # Turn polar accumulation on, double enter for no savefile or dumpfile
        xf.cmd("PACC\n\n\n", autonewline=False)

        # Calculate polar
        try:
            if len(operating_point) != 3:
                raise Warning("oper pt is single value or "
                              "[start, stop, interval]")
            # * unpacks, same as (alpha[0], alpha[1],...)
            xf.cmd("{:s} {:.3f} {:.3f} {:.3f}".format(pcmd[1], *operating_point))
        except TypeError:
            # If iterating doesn't work, assume it's a single digit
            xf.cmd("{:s} {:.3f}".format(pcmd[0], operating_point))

        # List polar and send recognizable end marker
        xf.cmd("PLIS\nENDD\n\n", autonewline=False)

        logger.info("Xfoil module starting read")

        # Keep reading until end marker is encountered
        output = ['']

        while not re.search(b'ENDD', output[-1].encode()):
            line = xf.readline()
            if line:
                print(line.decode('ASCII'))
                output.append(line.decode('ASCII'))

        logger.info("Xfoil module ending read")
        if show_seconds:
            sleep(show_seconds)
        # xf.__exit__()
        return parse_stdout_polar(output)


def parse_stdout_polar(lines):
    r"""Converts polar 'PLIS' data to array

    Parameters
    ----------
    lines
    ['',
     '\r\n',
     ' ===================================================\r\n',
     '  XFOIL Version 6.96\r\n', '  Copyright (C) 2000   Mark Drela, Harold Youngren\r\n',
     '\r\n',
     '  This software comes with ABSOLUTELY NO WARRANTY,\r\n',
     '    subject to the GNU General Public License.\r\n',
     '\r\n',
     '  Caveat computor\r\n',
     ' ===================================================\r\n',
     '\r\n', ' File  xfoil.def  not found\r\n', '\r\n',
     '   QUIT    Exit program\r\n',
     '\r\n', '  .OPER    Direct operating point(s)\r\n',
     '  .MDES    Complex mapping design routine\r\n',

     ......

    ' Side 1 forced transition at x/c =  1.0000   82\r\n',
    ' Side 2  free  transition at x/c =  0.6326   48\r\n',
    '\r\n',
    '   6   rms: 0.2249E+01   max: -.2520E+02   C at   48  2   RLX: 0.020\r\n',
    '       a =  0.000      CL =  0.1933\r\n',
    '      Cm = -0.1047     CD =  0.00258   =>   CDf =  0.00764    CDp = -0.00505\r\n',
    ' \r\n',
    ' Side 1 forced transition at x/c =  1.0000   82\r\n',
    ' Side 2  free  transition at x/c =  0.5898   46\r\n', '\r\n',
    '   7   rms: 0.7950E+00   max: 0.6842E+01   C at   82  1   RLX: 0.191\r\n',
    '       a =  0.000      CL =  0.1688\r\n',
    '      Cm = -0.0988     CD =  0.00405   =>   CDf =  0.00806    CDp = -0.00401\r\n',
    ' \r\n',
    ' Side 1 forced transition at x/c =  1.0000   82\r\n',
    ' Side 2  free  transition at x/c =  0.8922   64\r\n',
    ' idif Ue xi dudx           1  0.3180503      4.6163797E-03   68.89604    \r\n',
    ' Uenew xinew           2  2.2947257E-02  3.3307076E-04\r\n',
    '\r\n',
    '   8   rms: 0.7379E+00   max: 0.5934E+01   C at   82  1   RLX: 0.253\r\n',
    '       a =  0.000      CL =  0.0651\r\n',
    '      Cm = -0.0567     CD =  0.00539   =>   CDf =  0.00879    CDp = -0.00340\r\n',
    ' \r\n', ' Side 1 forced transition at x/c =  1.0000   81\r\n',
    ' Side 2  free  transition at x/c =  0.8667   63\r\n','\r\n',
    '   9   rms: 0.6662E+00   max: 0.2853E+01   C at   81  1   RLX: 0.196\r\n',
    '       a =  0.000      CL =  0.0213\r\n',
    '      Cm = -0.0414     CD =  0.00767   =>   CDf =  0.00907    CDp = -0.00139\r\n', ' \r\n',

    ....

    ' Point added to stored polar  1\r\n',
    ' Save file unspecified or not available\r\n',
    ' Dump file unspecified or not available\r\n',
    '\r\n', '.OPERva   c>  \r\n',
    ' ==============================================================\r\n',
    ' Polar  1\r\n',
    '  \r\n',
    '       XFOIL         Version 6.96\r\n',
    '  \r\n',
    ' Calculated polar for:                                                 \r\n',
    '  \r\n',
    ' 1 1 Reynolds number fixed          Mach number fixed         \r\n',
    '  \r\n',
    ' xtrf =   1.000 (top)        1.000 (bottom)  \r\n',
    ' Mach =   0.000     Re =     0.051 e 6     Ncrit =   9.000\r\n',
    '  \r\n', '   alpha    CL        CD       CDp       CM     Top_Xtr  Bot_Xtr\r\n',
    '  ------ -------- --------- --------- -------- -------- --------\r\n',
    '   0.000  -0.2952   0.03663   0.02484   0.0530   1.0000   0.3448\r\n',
    '\r\n',
    '.OPERva   c>   ENDD command not recognized.  Type a "?" for list\r\n']

    Returns
    -------
    (data_array, data_header, infodict)
        data_array : numpy.ndarray
            [[ 0.       0.0073   0.05392  0.04414 -0.0012   0.929    0.9309 ]]
        data_header : list
            ['alpha', 'CL', 'CD', 'CDp', 'CM', 'Top_Xtr', 'Bot_Xtr']
        infodict : dict
            {'Ncrit': 9.0, 'Mach': 0.0, 'xtrf_bottom': 1.0, 'Re': 59000.0, 'xtrf_top': 1.0}

    """

    def clean_split(s):
        r"""Split string

        Parameters
        ----------
        s : str
            The string to split

        """
        import platform
        if platform.system() == "Windows":
            return re.split('\s+', s.replace('\r\n', ''))[1:]
        elif platform.system() == "Linux":
            return re.split('\s+', s.replace('\n', ''))[1:]

    warnings = []

    # Find location of data from ---- divider
    for i, line in enumerate(lines):
        if "WARN" in line:
            warnings.append(line)
        if re.match('\s*---', line):
            divider_index = i

    data_array = []
    data_header = []
    infodict = {}

    # What columns mean
    try:
        data_header = clean_split(lines[divider_index - 1])

        # Clean info lines
        info = ''.join(lines[divider_index-4:divider_index-2])
        info = re.sub("[\r\n\s]", "", info)

        def p(s):
            r"""Parse info with regular expressions

            Parameters
            ----------
            s : str
                The string to parse
            """
            return float(re.search(s, info).group(1))

        infodict = {'xtrf_top': p("xtrf=(\d+\.\d+)"),
                    'xtrf_bottom': p("\(top\)(\d+\.\d+)\(bottom\)"),
                    'Mach': p("Mach=(\d+\.\d+)"),
                    'Ncrit': p("Ncrit=(\d+\.\d+)"),
                    'Re': p("Re=(\d+\.\d+e\d+)")}

        # Extract, clean, convert to array

        datalines = lines[divider_index + 1: -2]
        data_array = np.array([clean_split(dataline) for dataline in datalines],
                              dtype='float')
    except UnboundLocalError as e:
        logger.error("UnboundLocalError : %s" % str(e))
        raise UnboundLocalError

    return data_array, data_header, infodict, warnings


class Xfoil(object):
    r"""This class basically represents an XFOIL child process, and should
    therefore not implement any convenience
    functions, only direct actions on the XFOIL process.

    Much much faster in Python2 than in Python3, why ??

    bufsize=0 in Popen is critical !!

    """

    def __init__(self, path=""):
        r"""Spawn xfoil child process.

        Parameters
        ----------
        path : String
            Path to the xfoil executable folder

        """
        logger.debug("Instantiating Xfoil")
        self.xfoil_instance = subp.Popen([os.path.join(path, 'xfoil')],
                                         shell=False,
                                         bufsize=0,
                                         stdin=subp.PIPE,
                                         stdout=subp.PIPE,
                                         stderr=subp.PIPE)
        self._stdoutnonblock = \
            NonBlockingStreamReader(self.xfoil_instance.stdout)
        self._stdin = self.xfoil_instance.stdin
        self._stderr = self.xfoil_instance.stderr

    def cmd(self, command, autonewline=True):
        r"""Give a command. Set newline=False for manual control with '\n'

        Parameters
        ----------
        command : str
            The command to pass to XFoil
        autonewline : bool (optional, default is True)
            Append a backslash n character to the issued commands

        """
        n = '\n' if autonewline else ''
        # self.xfinst.stdin.write(command + n)
        # logger.debug("Issuing command : %s" % command)
        print(command)
        self.xfoil_instance.stdin.write((command + n).encode())

    def readline(self):
        r"""Read one line, returns None if empty"""
        # self._stdoutnonblock is a NonBlockingStreamReader
        return self._stdoutnonblock.readline()

    def close(self):
        r"""Kill the xfoil instance"""
        logger.info("Xfoil: instance closed through .close()")
        self.xfoil_instance.kill()

    def __enter__(self):
        r"""Gets called when entering 'with ... as ...' block
        (context manager)"""
        logger.info("Xfoil: context manager __enter__")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Called when exiting 'with ... as ...' block (context manager)"""
        if exc_type is not None:
            logger.error("exc_type of XFoil is not None")
            print("%r, %r, %r" % (exc_type, exc_value, traceback))
            raise RuntimeError
        logger.info("Xfoil: instance closed through __exit__")
        self.xfoil_instance.kill()

    def __del__(self):
        r"""Called when deleted with 'del ...' or garbage collected"""
        logger.info("Xfoil: instance closed through __del__ "
                    "(e.g. garbage collection)")
        self.xfoil_instance.kill()


class NonBlockingStreamReader(object):
    r"""XFOIL is interactive, thus readline() blocks.
    The solution is to let another thread handle the XFOIL communication,
    and communicate with that thread using a queue.

    References
    ----------
    http://eyalarubas.com/python-subproc-nonblock.html

    """

    def __init__(self, stream):
        r"""

        Parameters
        ----------
        stream: Usually a process' stdout or stderr.
            The stream to read from.

        """
        self._s = stream
        self._q = queue.Queue()

        def _populate_queue(a_stream, a_queue):
            r"""Collect lines from 'stream' and put them in 'queue'."""
            while True:
                line = a_stream.readline()
                if line:
                    a_queue.put(line)
                else:
                    # print "NonBlockingStreamReader: End of stream"
                    # Make sure to terminate
                    return
                    # raise UnexpectedEndOfStream

        self._t = Thread(target=_populate_queue, args=(self._s, self._q))
        self._t.daemon = True

        self._t.start()  # Start collecting lines from the stream

    def readline(self, timeout=None):
        try:
            return self._q.get(block=timeout is not None, timeout=timeout)
        except queue.Empty:
            return None
