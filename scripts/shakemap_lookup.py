"""
Script reads and plots the USGS shakemap grid. Loads coordinate locations and
looks up the hazard values at those locations and saves results

"""
import argparse as ap
import pandas as pd

from shakemap_utils import USGSshakemapGrid

def get_args():
    """Get script arguments"""

    parser = ap.ArgumentParser(description='Lookup shakemap values at a set of locations',
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
                        help='ShakeMap uncertainty grid stored in xml or xml.zip format')

    parser.add_argument('--intensity_measure',
                        metavar='code',
                        type=str,
                        nargs='?',
                        default='MMI',
                        help='Which intensity measure to lookup')

    parser.add_argument('-o', '--ofile',
                        metavar='lookup_results.csv',
                        type=str,
                        nargs='?',
                        default='locations_with_intensity.csv',
                        help='Output filename for locations with their shakemap intensity.')

    args = parser.parse_args()

    return args


def main(args=get_args()):
    """Main script."""

    # Read Shakemap into class object
    print("Reading shakemap from file...")
    if args.shakemap_unc is not None:
        shakemap = USGSshakemapGrid(args.shakemap, args.intensity_measure, args.shakemap_unc)
    else:
        shakemap = USGSshakemapGrid(args.shakemap, args.intensity_measure)

    # Read locations into pandas array
    locns = pd.read_csv(args.ifile)
    print("\t...%i locations" % len(locns))

    # Get the mean/median and std deviation from the shakemap.
    median, stddev = shakemap.lookup(locns['lon'].values, locns['lat'].values)
    locns[args.intensity_measure] = median
    print(f"\t...{locns[args.intensity_measure].count():d} locations with an intensity")

    # Write the output file
    locns.to_csv(args.ofile, index=False)
    print(f"Written location details to {args.ofile:s}")

    print("DONE")


if __name__ == '__main__':
    main()
