""" Class for importing and looking up our locations"""

import pandas as pd


class Locations:
    """Classs for importing and looking up locations. The class holds a pandas
    dataframe self.df with fields defined by the input csv file

    """
    def __init__(self, ifile_locns, xyBox=[-180.0, 180.0, -90.0, 90.0]):
        """Constructor for location store read locations from a csv file and find those
        within a lat/lon limits

        """
        # Read locations
        print("Reading locations from %s" % ifile_locns)
        locns = pd.read_csv(ifile_locns)

        # Keep those in bounds
        inLocns = locns[((locns['lon'] >= xyBox[0]) &
                         (locns['lon'] < xyBox[1]) &
                         (locns['lat'] >= xyBox[2]) &
                         (locns['lat'] < xyBox[3]))]

        self.df = inLocns

        return

    def add_intensities(self, shakemap):
        """ Add shakemap intensities to each of the locations"""

        # TODO: Check input is a dataframe
        # TODO: Check required fields are there in locns

        # Get the mean/median and std deviation from the shakemap.
        median, stddev = shakemap.lookup(self.df.lon.values,
                                         self.df.lat.values)

        # TODO: Warning if no intensities returned

        # New field name depends on which intensity measure it is.
        intensName = shakemap.intensMeasure
        self.df[intensName + '_med'] = median
        self.df[intensName + '_std'] = stddev

        return

    def add_damageprobs(self, intensName, fragilityCurve, useMedian=True):
        """ Add damage probabilities based on the intensities"""

        # TODO: Check input is a dataframe
        # TODO: Check required fields are there in locns
        # TODO: Check match of intensity names

        if not useMedian:
            print("WARNING: option not available yet. " +
                  "Damage probabilities only based on median intensities")

        intensities = self.df[intensName + '_med'].values

        # Loop through all damage states in the fragility curve
        for c in fragilityCurve.damagestates():
            # Fieldname for the probabilities at these locations
            fnm = 'prob_' + c

            # Get the result of the interpolation, allow values over the max by
            # setting them equal to the max
            self.df[fnm] = fragilityCurve.interp_damagestate(intensities, c)

        return
