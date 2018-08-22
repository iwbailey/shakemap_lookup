"""Module contains class for a fragility curve."""

# * Libraries


import numpy as np
import pandas as pd
from scipy import interpolate


# * Class definition


class FragilityCurve:
    """Define prob of exceeeding damage states at different intensities.

    Variables:
    intensitymeasure : string identifying the intensity measure used.
    intensities: numpy vector of intensity values where prob exceedence
                 is defined.
    exceedprob: pandas dataframe of exceedance probilities, each column is a
                different damage state

    Initialize keyword:

    ifile : string pointing to a csv file containing intensities in first
            column and exceedance probabilities for different damage states in
            subsequent columns. The damage states are defined by the header of
            each column. For example...

            mmi, negligible, minor, major, destruction
            6.0, 0.2, 0.05, 1e-4, 1e-12
            ...

    """

    def __init__(self, ifile):
        """Constructor for fragility curve
        """

        # Read the whole thing as a pandas data frame from csv
        print "Reading %s..." % ifile
        fragility_in = pd.read_csv(ifile)

        # TODO: error checking on fields

        # First column is the intensity measure
        self.intensitymeasure = fragility_in.columns[0]

        # Sort from smallest to largest intensity
        fragility_in = fragility_in.sort_values(self.intensitymeasure)

        # Keep intensities in a separate array
        self.intensities = fragility_in[self.intensitymeasure].values

        # Second/third columns are the damage states
        self.exceedprob = fragility_in.iloc[:, 1:]

        # TODO: Check that the exceedance prob is monotonically increasing

        return

    def minintensity(self):
        """Return the minimum intensity."""
        return(np.min(self.intensities))

    def maxintensity(self):
        """ Return the maximum intensity. """
        return(np.max(self.intensities))

    def mindamagestate(self):
        """ Return the name of the minimum damage state"""
        return(self.exceedprob.columns[0])

    def damagestates(self):
        """ Return a list of the fragility curve's damage states."""
        return(self.exceedprob.columns)

    def interp_damagestate(self, myintensities, dstate):
        """Interpolate the curve at a list of intensities for one damage state.

        Returns a numpy vector of exceedance probabilities.

        Keyword arguments:
        myintensites = numpy vector of intensities.
        dstate = string of which damage state to interpolate

        Notes:

        * Intensities above the highest intensity of the curve will get the
          probability at the highest intensity of the curve.

        * Intensities below the lowest intensity of the curve will get a
          probability of zero.

        """

        # Build the interpolator
        Pchip = interpolate.PchipInterpolator(self.intensities,
                                              self.exceedprob[dstate].values,
                                              extrapolate=False)

        # Get the result of the interpolation, allow values over the max by
        # setting them equal to the max
        exceedprob_locs = Pchip(np.fmin(myintensities, self.maxintensity()))

        # Values below the lowest intensity value
        # TODO: handling of nan
        exceedprob_locs[myintensities < self.minintensity()] = 0.0

        return exceedprob_locs
