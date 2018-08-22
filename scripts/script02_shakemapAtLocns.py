"""
Script reads and plots the USGS shakemap grid. Loads coordinate locations and
looks up the hazard values at those locations and saves results

"""
# Libraries ------------------------------------------------------------------
import os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import pylab

from shakemap_lookup import USGSshakemapGrid
from shakemap_lookup import read_locations_csv
from shakemap_lookup import add_intensities


# Parameters ------------------------------------------------------------------

# Shakemap and uncertainty files
idir = os.path.join(os.path.expanduser('~'), 'Downloads', 'usgs_shakemap')
eventid = '1000dyad_v11.0'
ifile_sm = os.path.join(idir, ('grid_%s.xml.zip' % eventid))
ifile_unc = os.path.join(idir, ('uncertainty_%s.xml.zip' % eventid))

# Which intensity measure to use
intensMeasure = 'MMI'

# File containing locations
ifile_locns = '../inputs/Hawaii_Mile_Markers_v2.csv'

# Output file name
ofile_locns = "Hawaii_lookup_results.csv"


# Inline functions ------------------------------------------------------------

def checkplot_inlocns(locns, thisSM):
    """Plot the locations and highlight the ones that are in the bounds"""
    print("Generating plot...")
    fig, ax = plt.subplots(1, 1, facecolor='white')

    # Plot locations
    ax.plot(locns['lon'].values, locns['lat'].values, 'xk')

    # Plot the ones that got a shakemap intensity
    inlocns = locns[~locns[intensMeasure + '_med'].isna()]
    plt.plot(inlocns['lon'].values, inlocns['lat'].values, '+r')

    # Plot the bounding box of the shakemap
    xyBox = thisSM.xylims(isCenters=False)
    plt.plot(xyBox[np.array([0, 0, 1, 1, 0])],
             xyBox[np.array([2, 3, 3, 2, 2])], '-r')

    ax.set_aspect('equal')
    ax.autoscale(tight=True)
    plt.title('Check locations in box')

    # Show the plot
    print('Pausing while plot is shown...')
    pylab.show(block=True)


def checkplot_shakemaplookup(thisSM, locns, clims=(2.0, 10.0), dc=1.0):
    """Plot the shakemap within the search region. Overlay the locations with their
    intensity values on the same colour scale

    """
    print("Generating plot...")
    fig, ax = plt.subplots(1, 1, facecolor='white')

    # Plot the shakemap
    cax = ax.imshow(thisSM.grid, aspect='equal', interpolation='none',
                    vmin=clims[0], vmax=clims[1], origin='lower',
                    extent=(thisSM.x0, thisSM.x1, thisSM.y0, thisSM.y1))

    # Add the locations
    ax.scatter(locns['lon'].values, locns['lat'].values,
               c=locns[thisSM.intensMeasure + '_med'].values, s=60.0,
               cmap=cax.cmap, vmin=clims[0], vmax=clims[1], marker='v',
               edgecolors='k')

    # Formatting
    ax.set_aspect('equal')
    ax.autoscale(tight=True)
    ax.grid()

    # Add a color bar
    plt.colorbar(cax, orientation='vertical',
                 ticks=np.arange(clims[0], clims[1]+dc, dc),
                 label=thisSM.intensMeasure)

    # Show the plot
    print('Pausing while plot is shown...')
    pylab.show(block=True)


# Script ----------------------------------------------------------------------


def main():

    """
    MAIN SCRIPT:

    """

    # Read Shakemap into class object
    print("Reading shakemap from file...")
    shakemap = USGSshakemapGrid(ifile_sm, intensMeasure, ifile_unc)

    # Read locations into pandas array
    locns = read_locations_csv(ifile_locns)
    print "\t...%i locations" % len(locns)

    # Look up the intensities at the locations
    add_intensities(locns, shakemap)
    print("\t...%i locations with an intensity" %
          locns[intensMeasure + '_med'].count())

    # Write the output file
    locns.to_csv(ofile_locns, index=False)
    print("Written location details to %s" % ofile_locns)

    # Generate check plots
    checkplot_inlocns(locns, shakemap)
    checkplot_shakemaplookup(shakemap, locns)

    print "Finished"

    return


if __name__ == '__main__':
    main()

# END -----
