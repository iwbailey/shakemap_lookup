"""Script...

Reads a USGS shakemap grid.

Loads coordinate locations and looks up the hazard values at those locations.

Loads a fragility curve based on the same intensity measure and calcs the
probability of different damage states

Saves results

"""
import argparse as ap
import pandas as pd

import os
import yaml
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import pylab

from shakemap_utils import USGSshakemapGrid
from shakemap_utils import Locations
from shakemap_utils import FragilityCurve


def get_args():
    """Get script arguments"""

    parser = ap.ArgumentParser(description='Lookup shakemap values at a set of locations, get damage estimate',
                               formatter_class=ap.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i', '--ifile',
                        metavar='input_coordinates.csv',
                        type=str,
                        nargs='?',
                        help='.csv file with columns "lon" and "lat"')

    parser.add_argument('-s', '--shakemap',
                        metavar='shakemap_grid.xml',
                        type=str,
                        nargs='?',
                        help='ShakeMap grid stored in xml or xml.zip format')

    parser.add_argument('-u', '--shakemap_unc',
                        metavar='shakemap_unc_grid.xml',
                        type=str,
                        nargs='?',
                        default=None,
                        help='ShakeMap grid stored in xml or xml.zip format')

    parser.add_argument('--fragility_file',
                        metavar='fragility.csv',
                        type='str',
                        nargs='?',
                        help='Fragility file in csv format')

    parser.add_argument('-o', '--ofile',
                        metavar='lookup_results.csv',
                        type=str,
                        nargs='?',
                        default='locations_with_intensity.csv',
                        help='Output filename for locations with their shakemap intensity.')

    args = parser.parse_args()

    return args


def main(args=get_args()):
    """Main Script."""

    # Read fragility file into class object
    print("Reading fragility curves from file...")
    frag = FragilityCurve(args.fragility_file)

    # Read Shakemap into class object
    print("Reading shakemap from file...")
    if args.shakemap_unc is not None:
        shakemap = USGSshakemapGrid(args.shakemap, frag.intensity_measure, args.shakemap_unc)
    else:
        shakemap = USGSshakemapGrid(args.shakemap, frag.intensity_measure)

    # Read locations into pandas array
    locns = pd.read_csv(args.ifile)
    print("\t...%i locations" % len(locns))

    # Get the mean/median and std deviation from the shakemap.
    median, stddev = shakemap.lookup(locns['lon'].values, locns['lat'].values)
    locns[frag.intensity_measure] = median
    print(f"\t...{locns[frag.intensity_measure].count():d} locations with an intensity")

    # Remove locations where no intensity is found
    print("Removing %i locations without any intensity" %
          sum(np.isnan(locns[frag.intensity_measure])))
    locns = locns[~np.isnan(locns[frag.intensity_measure])]

    # Convert intensities to probability of damage at each state
    print("Getting damage at locations...")
    # Loop through all damage states in the fragility curve
    for c in frag.damagestates():
        # Get the result of the interpolation, allow values over the max by setting them equal to the max.
        locns['prob_' + c] = frag.interp_damagestate(locns[frag.intensity_measure], c)

    print(frag.mindamagestate())
    print("\t...%i locations with a chance of damage" %
          sum(locns['prob_' + frag.mindamagestate()] > 0.0))

    # Write the output file
    locns.to_csv(args.ofile, index=False)
    print(f"Written location details to {args.ofile}")

    print("Finished")

    return


if __name__ == '__main__':
    main()

# END -----
