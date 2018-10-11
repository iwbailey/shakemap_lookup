"""Basic test that we import the shakemap into the class as we should """


# Libraries ------------------------------------------------------------------
import os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import pylab

from shakemap_lookup import USGSshakemapGrid


# Parameters ------------------------------------------------------------------
idir = os.path.join(os.path.expanduser('~'), 'Downloads', 'usgs_shakemap')
eventid = '1000dyad_v11.0'
ifile_sm = os.path.join(idir, ('grid_%s.xml.zip' % eventid))
ifile_unc = os.path.join(idir, ('uncertainty_%s.xml.zip' % eventid))


# Functions -------------------------------------------------------------------


def check_plot(thisSM):
    """ Plot the shakemap and uncertainty grid that were downloaded"""

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
                 ticks=np.arange(0, 1.5, 0.25),
                 label=('Std(%s)' % thisSM.intensMeasure))

    print('Pausing while plot is shown...')

    # Show the plot
    pylab.show(block=True)

    return

# Script ----------------------------------------------------------------------


print('Reading the shakemap from file with MMI...')
thisSM = USGSshakemapGrid(ifile_sm, 'MMI', ifile_unc=ifile_unc)

print "Event info:\n", thisSM.eventInfo

# Check grid dimensions consistent with header
print("\nFrom input xml file:")
os.system(('zcat %s | grep "grid_specification"' % ifile_sm))

print("\nRead into class:")
print "\tGrid dimensions:", np.shape(thisSM.grid)
print "\tUncert grid dimensions:", np.shape(thisSM.grid_std)
print "\tnx and ny:", thisSM.nx(), thisSM.ny()
print "\txlims (grid centers):", thisSM.xlims(True)
print "\tdx, dy:", thisSM.dx(), thisSM.dy()
print "\txlims (grid edges):", thisSM.xlims()
print "\tylims (grid centers):", thisSM.ylims(True)

# Check coordinates are correct
check_plot(thisSM)

#
