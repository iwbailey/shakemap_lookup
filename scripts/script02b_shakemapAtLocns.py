"""
Script reads and plots the USGS shakemap grid. Loads coordinate locations and
looks up the hazard values at those locations and saves results

"""
# * Libraries
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

from ShakeMapGrid import USGSshakemap
from checkplot_functions import plot_mmiprob
from checkplot_functions import plot_subregbox
from checkplot_functions import plot_inlocations
from checkplot_functions import plot_shakemapwithlocns

# * Parameters -----
ifile_sm = 'shakemap/grid.xml.zip'
intensMeasure = 'MMI'
ifile_unc = 'shakemap/uncertainty.xml.zip'
# ifile_locns = 'locations/test_input_locations.csv'
ifile_locns = 'locations/Hawaii_Mile_Markers_v2.csv'
minInt = 5.0
ifile_frag = './fragility/my_fragility.csv'
ofile_locns = "locations/hazard_lookup_results.csv"


# Functions ------

def read_locns(ifile_locns, xyBox=[-180.0, 180.0, -90.0, 90.0]):
    """Read locations from a csv file and find those within a lat/lon limits"""

    # Read locations
    print("Reading locations from %s" % ifile_locns)
    locns = pd.read_csv(ifile_locns)
    print "\t...%i locations" % len(locns)

    # Keep those in bounds
    inLocns = locns[((locns['lon'] >= xyBox[0]) &
                     (locns['lon'] < xyBox[1]) &
                     (locns['lat'] >= xyBox[2]) &
                     (locns['lat'] < xyBox[3]))]

    return inLocns


def get_xylims(smGrid, minInt):
    """ Get the grid extents of intensities greater than the minimum

    """
    # Find values above the grid limits
    isOver = smGrid.grid >= minInt

    # Get x and y coordinates
    xi = smGrid.xcoords(np.any(isOver, axis=0))  # use axis=0 since y is axis=1
    yi = smGrid.ycoords(np.any(isOver, axis=1))

    # Get half of x and y spacing
    halfdx, halfdy = 0.5*smGrid.dx, 0.5*smGrid.dy

    # Get the min max of xi and yi
    return np.array([xi[0]-halfdx, xi[-1]+halfdx, yi[0]-halfdy, yi[-1]+halfdy])


# Script ---------

def main():

    """
    MAIN SCRIPT:

    ifile_sm: (str) input file shakemap, xml or xml.zip
    intensityMeasure: (str) which field extracted from the shakemap file
    ifile_locns: (str) csv file of input locations
    minInt: (float) minimum intensity measure to consider as damaging
    ifile_frag: (str) input file containing the fragility function, csv file
    ofile_locns: (str) output file where to write the location details
    """

    # Clean plots
    plt.close('all')

    # ** Look up the intensities at the locations ----

    # Read the shakemap into a class
    print 'Reading shakemap %s from %s' % (intensMeasure, ifile_sm)
    smGrid = USGSshakemap(ifile_sm, intensMeasure)

    print "\t...nx=%s x ny=%s" % (smGrid.nx(), smGrid.ny())

    # Merge uncertainty into class
    print "Adding uncertainty from %s" % ifile_unc
    smGrid.adduncertainty(ifile_unc)

    # Find the bounds that include all grid points above a minimum intensity
    # threshold
    print "Finding grid limits for intensity >= %.1f..." % minInt
    xySubReg = get_xylims(smGrid, minInt)

    # Clip the shakemap grid the grid limits
    smGrid.clipxy(xySubReg)

    # Find the locations within the shakemap extent
    locns = read_locns(ifile_locns, xySubReg)
    print "\t...%i locations in bounds" % len(locns)

    # Get the shakemap intensities at the locations
    print("Look-up of intensities...")
    locns[intensMeasure], locns['stddev'] = smGrid.lookup(locns.lon.values,
                                                          locns.lat.values)

    print("\t...%i remaining locations have hazard val >=%.2f" %
          (sum(locns[intensMeasure] >= minInt), minInt))

    # Exit if no locations
    if sum(locns[intensMeasure] >= minInt) == 0:
        print "No locations have an intensity higher than %.1f" % minInt
        sys.exit()

    # ** Estimate the damage probability at the locations -----

    print "Reading %s..." % ifile_frag
    dfFrag = pd.read_csv(ifile_frag)

    print "Interpolating to observed intensities..."
    locns = interpolate_damage(locns, dfFrag, intensMeasure)

    # ** Save the ouput to csv file ----
    locns.to_csv(ofile_locns, index=False)
    print("Written location details to %s" % ofile_locns)

    print "Finished"

    return


def checkplot_searchbox():
    """Plot the shakemap with the box including all intensities above the
    threshold

    """
    smGrid = USGSshakemap(ifile_sm, intensMeasure, True)
    xySubReg = get_xylims(smGrid, minInt)

    print "Generating check plot ..."
    fig = plot_subregbox(smGrid, xySubReg)
    fig.show()

    smGrid.clipxy(xySubReg)
    fig = plot_subregbox(smGrid, xySubReg)
    fig.show()
    return


def checkplot_locationsinbox():
    """Plot the locations we read in and check which ones are inside the search
    box

    """
    smGrid = USGSshakemap(ifile_sm, intensMeasure, True)
    xySubReg = get_xylims(smGrid, minInt)
    locns = pd.read_csv(ifile_locns)

    # Keep those in bounds
    inLocns = locns[((locns['lon'] >= xySubReg[0]) &
                     (locns['lon'] < xySubReg[1]) &
                     (locns['lat'] >= xySubReg[2]) &
                     (locns['lat'] < xySubReg[3]))]

    # Plot all the locations, color the ones inside
    fig = plot_inlocations(locns, inLocns, xySubReg)
    fig.show()

    # Plot just the locations within the box
    fig2 = plot_inlocations(inLocns, inLocns, xySubReg)
    fig2.show()

    return


def checkplot_shakemaplookup():
    """Plot the shakemap within the search region. Overlay the locations with their
    intensity values on the same colour scale

    """
    # Read the shakemap and clip as in the code
    smGrid = USGSshakemap(ifile_sm, intensMeasure, True)
    xySubReg = get_xylims(smGrid, minInt)
    smGrid.clipxy(xySubReg)

    # Read in locations and lookup intensities
    locns = read_locns(ifile_locns, xySubReg)
    locns[intensMeasure], locns['stddev'] = smGrid.lookup(locns.lon.values,
                                                          locns.lat.values)

    # Plot the locations
    fig = plot_shakemapwithlocns(smGrid, xySubReg, locns)
    fig.show()
    return




def checkplot_interpolatedamage():
    """Read in fragility function, compare to the interpolated results we've output
    to file

    """
    # Read fragility function
    dfFrag = pd.read_csv(ifile_frag)

    # plot
    fig, ax = plot_mmiprob(dfFrag)

    # Read interpolated values
    locns = pd.read_csv(ofile_locns)

    for c in dfFrag.columns[1:]:
        # Fieldname for the probabilities at these locations
        fnm = 'prob_' + c
        print fnm
        ax.plot(locns[intensMeasure].values, locns[fnm].values, '+')

    fig.show()

    return


def checkplot_fragilitycurve():
    """Read in the fragility function and plot it """
    dfFrag = pd.read_csv(ifile_frag)
    fig, _ = plot_mmiprob(dfFrag)
    fig.show()
    return


if __name__ == '__main__':
    main()

# END -----
