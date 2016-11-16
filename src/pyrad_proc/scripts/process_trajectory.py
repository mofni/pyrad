#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Create PYRAD products using a plane trajectory.
"""

# Author: Andreas Leuenberger
# License: BSD 3 clause

# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------
from __future__ import print_function
import sys
import argparse
from datetime import datetime

from pyrad.flow import main_trajectory as pyrad_main_trajectory


def main():
    """
    """

    # Parse the arguments
    parser = argparse.ArgumentParser(
        description="Create PYRAD products using a plane trajectory",
        epilog="Example:\n"
        "  process_trajectory.py -c $HOME/pyrad/config/processing/mals_emm_rw22_traj.txt\n"
        "     -i TS011 /data/mals_plane_traj/EMM/gnv_20161026_ts011_seat_emmen_flt01_ADS.txt",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    # Input arguments:
    parser.add_argument("-c", "--cfgfile", type=str,
                        help="Main configuration file. Defines the ",
                        default="")
    parser.add_argument("trajfile", type=str,
                        help="Definition file of plane trajectory. "
                        "Configuration of scan sector, products, ...")

    parser.add_argument("starttime", nargs='?', type=str,
                        help="Starting time of the data to be processed. "
                        "Format: YYYYMMDDhhmm[ss]. If not given, the time "
                        "of the first sample is used.",
                        default="")
    parser.add_argument('endtime', nargs='?', type=str,
                        help="End time of the data to be processed. "
                        "Format: YYYYMMDDhhmm[ss]. If not given, the time "
                        "of the last sample is used.",
                        default="")

    parser.add_argument("-i", "--infostr",
                        help="Information string about the actual data "
                        "processing (e.g. 'RUN57'). This sting is added "
                        "to the filenames of the product files.",
                        default="")

    args = parser.parse_args()
    dt_starttime = None
    dt_endtime = None

    if (len(args.starttime) > 0):
        try:
            if (len(args.starttime) == 14):
                dt_starttime = datetime.strptime(args.starttime,
                                                 '%Y%m%d%H%M%S')
            elif (len(args.starttime) == 12):
                dt_starttime = datetime.strptime(args.starttime, '%Y%m%d%H%M')
            else:
                raise
        except:
            print("process_trajectory.py: Format error: Argument 'starttime' "
                  "must be in format 'YYYYMMDDhhmm[ss]' (is '%s')" %
                  args.starttime,
                  file=sys.stderr)
            sys.exit(1)

    if (len(args.endtime) > 0):
        try:
            if (len(args.endtime) == 14):
                dt_endtime = datetime.strptime(args.endtime, '%Y%m%d%H%M%S')
            elif (len(args.endtime) == 12):
                dt_endtime = datetime.strptime(args.endtime, '%Y%m%d%H%M')
            else:
                raise
        except:
            print("process_trajectory.py: Format error: Argument 'endtime' "
                  "must be in format 'YYYYMMDDhhmm[ss]' (is '%s')" %
                  args.endtime,
                  file=sys.stderr)
            sys.exit(1)

    print('Trajectory file: '+args.trajfile)
    if (len(args.infostr) > 0):
        print('Info string    : '+args.infostr)
    if (len(args.starttime) > 0):
        print('Start time     : '+args.starttime)
    if (len(args.endtime) > 0):
        print('End time       : '+args.endtime)

    pyrad_main_trajectory(args.cfgfile, args.trajfile, args.infostr,
                          dt_starttime, dt_endtime)


# ---------------------------------------------------------
# Start main:
# ---------------------------------------------------------
if __name__ == "__main__":
    main()
