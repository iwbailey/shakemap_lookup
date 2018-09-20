"""
Search the USGS for an earthquake and download its ShakeMap

"""

# * Libraries ----
from numpy import arange
import argparse
import yaml
import sys
import os

from matplotlib import pyplot as plt
from matplotlib import pylab

# From this project
from shakemap_lookup import download_shakemapgrid
from shakemap_lookup import USGSshakemapGrid


# * Functions -----


def check_plot(ifile, ifile_unc):
    """ Plot the shakemap and uncertainty grid that were downloaded"""

    print('Reading the shakemap from file with MMI...')
    thisSM = USGSshakemapGrid(ifile, 'MMI', ifile_unc=ifile_unc)

    print("Generating plot...")
    fig, ax = plt.subplots(1, 2, facecolor='white')

    # Plot the shakemap as colours
    cax = ax[0].imshow(thisSM.grid, aspect='equal', interpolation='none',
                       vmin=2, vmax=10, origin='lower',
                       extent=(thisSM.x0, thisSM.x1, thisSM.y0, thisSM.y1))

    # Plot uncertainty
    cax2 = ax[1].imshow(thisSM.grid_std, aspect='equal', interpolation='none',
                        vmin=0, vmax=1.5, origin='lower',
                        extent=(thisSM.x0, thisSM.x1, thisSM.y0, thisSM.y1))

    # Turn grid on
    for a in ax:
        a.grid()

    # Add a colorbar
    plt.colorbar(cax, ax=ax[0], orientation='horizontal',
                 ticks=range(0, 10, 1),
                 label=thisSM.intensMeasure)
    plt.colorbar(cax2, ax=ax[1], orientation='horizontal',
                 ticks=arange(0, 1.5, 0.25),
                 label=('Std(%s)' % thisSM.intensMeasure))

    print('Pausing while plot is shown...')

    # Show the plot
    pylab.show(block=True)


def main(ifile_dflt='example_search_params.yaml',
         odir_dflt=os.path.join(os.path.expanduser('~'), 'Downloads',
                                'usgs_shakemap')):
    """ Script """

    # Get the input arguments
    parser = argparse.ArgumentParser(description='Download a USGS ShakeMap',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i', '--ifile',
                        metavar='search_params.yaml',
                        type=str,
                        nargs='?', default=ifile_dflt,
                        help='.yaml file with the event search parameters')

    parser.add_argument('-o', '--odir',
                        metavar='path/to/save/output/',
                        type=str,
                        nargs='?', default=odir_dflt,
                        help='Path to store downloaded ShakeMap files')

    args = parser.parse_args()

    # Read the search parameters from the file
    with open(args.ifile, 'r') as stream:
        try:
            # Expect the yaml file to contain fields that go into a dict
            searchParams = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit()

    # Get the shakemaps and save to a file
    ofilename, ofilename_unc = download_shakemapgrid(searchParams,
                                                     args.odir)

    # Check what we have downloaded
    check_plot(ofilename, ofilename_unc)

    print("DONE")

    return


if __name__ == '__main__':
    main()
