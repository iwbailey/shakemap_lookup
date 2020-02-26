"""
Script reads and plots the USGS shakemap grid. Loads coordinate locations and
looks up the hazard values at those locations and saves results

"""
# Libraries ------------------------------------------------------------------
import os
import yaml
import sys
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import pylab

from shakemap_lookup import USGSshakemapGrid
from shakemap_lookup import Locations


# Parameters ------------------------------------------------------------------
ifile_params = "lookup_params.yaml"


# Inline functions ------------------------------------------------------------

def checkplot_inlocns(locns, thisSM, intensMeasure):
    """Plot the locations and highlight the ones that are in the bounds"""
    print("Generating plot...")
    fig, ax = plt.subplots(1, 1, facecolor='white')

    # Plot locations
    ax.plot(locns.df['lon'].values, locns.df['lat'].values, 'xk')

    # Plot the ones that got a shakemap intensity
    inlocns = locns.df[locns.df[intensMeasure + '_med'].notnull()]
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
    ax.scatter(locns.df['lon'].values, locns.df['lat'].values,
               c=locns.df[thisSM.intensMeasure + '_med'].values, s=60.0,
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
    """Main script
    """

    # Read the parameters from the file
    with open(ifile_params, 'r') as stream:
        try:
            # Expect the yaml file to contain fields that go into a dict
            lookupParams = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit()

    # Name of the shakemap file
    ifile_sm = os.path.join(lookupParams['idir'],
                            ('grid_%s.xml.zip' %
                             lookupParams['eventid']))

    # Which intensity measure to get
    intensMeasure = lookupParams['intensMeasure']

    # Read Shakemap into class object
    print("Reading shakemap from file...")
    if lookupParams['includeUncertainty'] is True:
        ifile_unc = os.path.join(lookupParams['idir'],
                                 ('uncertainty_%s.xml.zip' %
                                  lookupParams['eventid']))
        shakemap = USGSshakemapGrid(ifile_sm, intensMeasure, ifile_unc)
    else:
        shakemap = USGSshakemapGrid(ifile_sm, intensMeasure)

    # Read locations into pandas array
    locns = Locations(lookupParams['ifile_locns'])
    print("\t...%i locations" % len(locns.df))

    # Look up the intensities at the locations
    locns.add_intensities(shakemap)
    print("\t...%i locations with an intensity" %
          locns.df[intensMeasure + '_med'].count())

    # Write the output file
    locns.df.to_csv(lookupParams['ofile_locns'], index=False)
    print("Written location details to %s" %
          lookupParams['ofile_locns'])

    # Generate check plots
    checkplot_inlocns(locns, shakemap, intensMeasure)
    checkplot_shakemaplookup(shakemap, locns)

    print("Finished")

    return


if __name__ == '__main__':
    main()

# END -----
