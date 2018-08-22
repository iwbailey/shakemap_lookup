"""
Search the USGS for an earthquake and download its ShakeMap

"""

# * Libraries ----
import os
from numpy import arange
from matplotlib import pyplot as plt
from matplotlib import pylab

# From this project
from shakemap_lookup import download_shakemapgrid
from shakemap_lookup import USGSshakemapGrid


# * Parameters -----

# TODO: Migrate these parameters to a text yaml file that is read in by main()

searchParams = {  # Parameters for Hawaiian earthquake
    'starttime':  "2018-05-01",
    'endtime':  "2018-05-17",
    'minmagnitude':  6.8,
    'maxmagnitude': 10.0,
    'mindepth': 0.0,
    'maxdepth': 50.0,
    'minlongitude': -180.0,
    'maxlongitude': -97.0,
    'minlatitude':  0.0,
    'maxlatitude': 45.0,
    'limit': 50,
    'producttype': 'shakemap'}


# Where to save the downloaded grid
outdir = os.path.join(os.path.expanduser('~'), 'Downloads', 'usgs_shakemap')


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


def main():
    """ Script """

    ofilename, ofilename_unc = download_shakemapgrid(searchParams, outdir)

    check_plot(ofilename, ofilename_unc)

    print("DONE")

    return


if __name__ == '__main__':
    main()
