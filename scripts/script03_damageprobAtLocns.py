"""Script...

Reads a USGS shakemap grid.

Loads coordinate locations and looks up the hazard values at those locations.

Loads a fragility curve based on the same intensity measure and calcs the
probability of different damage states

Saves results

"""
# Libraries ------------------------------------------------------------------
import os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import pylab

from shakemap_lookup import USGSshakemapGrid
from shakemap_lookup import Locations
from shakemap_lookup import FragilityCurve

# Parameters ------------------------------------------------------------------

# Shakemap and uncertainty files
idir = os.path.join(os.path.expanduser('~'), 'Downloads', 'usgs_shakemap')
eventid = '70116556_v01.0'
ifile_sm = os.path.join(idir, ('grid_%s.xml.zip' % eventid))
ifile_unc = os.path.join(idir, ('uncertainty_%s.xml.zip' % eventid))

# Which intensity measure to use
intensMeasure = 'MMI'

# File containing locations
ifile_locns = '../inputs/Hawaii_Mile_Markers_v2.csv'

# File containing fragility curve
ifile_frag = '../inputs/my_fragility.csv'

# Output file name
ofile_locns = "Hawaii_lookup_results_withdamage.csv"

# Flag to keep only those with some damage prob
isKeepOnlyDamaged = True

# Inline functions ------------------------------------------------------------


def checkplot_interpolatedamage(frag, locns):
    """Read in fragility function, compare to the interpolated results we've output
    to file

    Plot the fragility curves as read in
    IN: Pandas data frame
          column 1 is named 'MMI'
          columns 2+ are named the damage states
    OUT: pyplot figure handle
    """

    fig, ax = plt.subplots(1, 1, facecolor='white')

    # Plot underlying fragility curve
    for c in frag.damagestates():
        ax.plot(frag.intensities, frag.exceedprob[c].values, label=c)

    # Plot result of the location lookup
    fnmIntens = frag.intensitymeasure + '_med'
    for c in frag.damagestates():
        # Fieldname for the probabilities at these locations
        fnmDamage = 'prob_' + c
        ax.plot(locns.df[fnmIntens].values, locns.df[fnmDamage].values, '+',
                label='locations')

    ax.set_xlabel(frag.intensitymeasure)
    ax.set_ylabel('ProbExceedance')
    ax.grid('on')
    ax.legend(loc=2, frameon=False, framealpha=0.5)

    plt.title('Check fragility calculation')

    # Show the plot
    print('Pausing while plot is shown...')
    pylab.show(block=True)

    return


# Script ----------------------------------------------------------------------


def main():

    """
    MAIN SCRIPT:

    """

    # Read Shakemap into class object
    print("Reading shakemap from file...")
    shakemap = USGSshakemapGrid(ifile_sm, intensMeasure, ifile_unc)

    # Read locations into pandas array
    print("Reading locations from file...")
    locns = Locations(ifile_locns)
    print("\t...%i locations" % len(locns.df))

    # Look up the intensities at the locations
    locns.add_intensities(shakemap)
    print("\t...%i locations with an intensity" %
          locns.df[intensMeasure + '_med'].count())

    # Remove locations where no intensity is found
    print("Removing %i locations without any intensity" %
          sum(np.isnan(locns.df[intensMeasure + '_med'])))
    locns.df = locns.df[~np.isnan(locns.df[intensMeasure + '_med'])]

    # Read fragility file into class object
    print("Reading fragility curves from file...")
    frag = FragilityCurve(ifile_frag)

    # Convert intensities to probability of damage at each state
    print("Getting damage at locations...")
    locns.add_damageprobs(intensMeasure, frag, useMedian=True)

    print(frag.mindamagestate())
    print("\t...%i locations with a chance of damage" %
          sum(locns.df['prob_' + frag.mindamagestate()] > 0.0))
    if(isKeepOnlyDamaged):
        print("\t...Keeping only locations with chance of damage")
        locns.df = locns.df[locns.df['prob_' + frag.mindamagestate()] > 0.0]

    # Write the output file
    locns.df.to_csv(ofile_locns, index=False)
    print("Written location details to %s" % ofile_locns)

    # Generate check plots
    checkplot_interpolatedamage(frag, locns)

    print("Finished")

    return


if __name__ == '__main__':
    main()

# END -----
