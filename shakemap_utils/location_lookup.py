""" Module for importing and looking up our locations"""


import pandas as pd


def read_locations_csv(ifile_locns, xyBox=[-180.0, 180.0, -90.0, 90.0]):
    """Read locations from a csv file and find those within a lat/lon limits"""

    # Read locations
    print("Reading locations from %s" % ifile_locns)
    locns = pd.read_csv(ifile_locns)

    # Keep those in bounds
    inLocns = locns[((locns['lon'] >= xyBox[0]) &
                     (locns['lon'] < xyBox[1]) &
                     (locns['lat'] >= xyloBox[2]) &
                     (locns['lat'] < xyBox[3]))]

    return inLocns


def add_intensities(locns, shakemap):
    """ Add shakemap intensities to each of the locations"""

    # TODO: Check input is a dataframe
    # TODO: Check required fields are there in locns

    # Get the mean/median and std deviation from the shakemap.
    median, stddev = shakemap.lookup(locns.lon.values,
                                     locns.lat.values)

    # TODO: Warning if no intensities returned

    # New field name depends on which intensity measure it is.
    intensName = shakemap.intensMeasure
    locns[intensName + '_med'] = median
    locns[intensName + '_std'] = stddev

    return


def add_damageprobs(locns, intensName, fragilityCurve, useMedian=True):
    """ Add damage probabilities based on the intensities"""

    # TODO: Check input is a dataframe
    # TODO: Check required fields are there in locns
    # TODO: Check match of intensity names

    if not useMedian:
        print("WARNING: option not available yet. " +
              "Damage probabilities only based on median intensities")

    intensities = locns[intensName + '_med'].values

    # Loop through all damage states in the fragility curve
    for c in fragilityCurve.damagestates():
        # Fieldname for the probabilities at these locations
        fnm = 'prob_' + c

        # Get the result of the interpolation, allow values over the max by
        # setting them equal to the max
        locns[fnm] = fragilityCurve.interp_damagestate(intensities, c)

    return


# def lookup_locations(locns, shakemap, fragilityCurve=None, useMedian=True):
#     """Look up shakemap intensities at set of locations.

#     Modifies input pandas dataframe of locations with intensity added on.

#     Keyword arguments:

#     locns : (pandas dataframe) locations with fields 'lon', 'lat'
#     shakemap : (USGSshakemapGrid) instance of shakemap class to lookup
#     fragilityCurve : (FragilityCurve) instance of fragility_curve class that
#       converts intensities into damage probabilities.

#     """

#     # Add the intensities
#     add_intensities(locns, shakemap)

#     # Add the damage probabilities
#     if fragilityCurve is not None:
#         add_damageprobs(locns, intensName, fragilityCurve, useMedian)

#     return
