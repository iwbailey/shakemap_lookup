"""
Search the USGS for an earthquake and download its ShakeMap

"""

# * Libraries ----
from numpy import arange
import argparse as ap
import yaml
import sys
import os

from matplotlib import pyplot as plt
from matplotlib import pylab

# From this project
from shakemap_lookup import download_shakemapgrid
from shakemap_lookup import USGSshakemapGrid


# * Functions -----


def get_args():

    # Get the input arguments
    parser = ap.ArgumentParser(description='Download a USGS ShakeMap',
                               formatter_class=ap.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i', '--ifile',
                        metavar='search_params.yaml',
                        type=str,
                        nargs='?',
                        default='search_params.yaml',
                        help='.yaml file with the event search parameters')

    parser.add_argument('-o', '--odir',
                        metavar='path/to/save/output/',
                        type=str,
                        nargs='?',
                        default=os.path.join(os.path.expanduser('~'),
                                             'Downloads',
                                             'usgs_shakemap'),
                        help='Path to store downloaded ShakeMap files')

    parser.add_argument('--proxy',
                        metavar='http://proxy.com:8008',
                        type=str,
                        nargs='?',
                        default=None,
                        help='')

    args = parser.parse_args()

    return args


def check_plot(ifile, ifile_unc):
    """ Plot the shakemap and uncertainty grid that were downloaded"""

    print('Reading the shakemap from file with MMI...')
    thisSM = USGSshakemapGrid(ifile, 'MMI', ifile_unc=ifile_unc)

    print("Generating plot...")
    fig, ax = plt.subplots(1, 2, facecolor='white')

    # Plot the shakemap as colours
    cax = ax[0].imshow(thisSM.grid, aspect='equal', interpolation='none',
                       vmin=2, vmax=10, origin='lower',
                       extent=thisSM.xylims(False))

    # Plot uncertainty
    cax2 = ax[1].imshow(thisSM.grid_std, aspect='equal', interpolation='none',
                        vmin=0, vmax=1.5, origin='lower',
                        extent=thisSM.xylims(False))

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


def main(args=get_args()):
    """ Script """

    # Set the proxy for all traffic
    if args.proxy is not None:
        os.environ['http_proxy'] = args.proxy
        os.environ['HTTP_PROXY'] = args.proxy
        os.environ['https_proxy'] = args.proxy
        os.environ['HTTPS_PROXY'] = args.proxy

    # Read the search parameters from the file
    with open(args.ifile, 'r') as stream:
        try:
            # Expect the yaml file to contain fields that go into a dict
            searchParams = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit()

    # Get the shakemaps and save to a file
    ofilename, ofilename_unc = download_shakemapgrid(searchParams, args.odir)

    if ofilename is None:
        sys.exit()

    # Check what we have downloaded
    check_plot(ofilename, ofilename_unc)

    print("DONE")

    return


if __name__ == '__main__':
    main()
