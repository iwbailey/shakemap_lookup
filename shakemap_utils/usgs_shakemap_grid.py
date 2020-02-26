"""Class to read and hold a USGS ShakeMap grid of a single intensity measure
and it's intensity for usgs shakemap

"""
import numpy as np
import numpy.ma as ma
from zipfile import ZipFile, is_zipfile
from xml.etree.ElementTree import parse
# import sys
import pdb

# Functions used to read in the ShakeMap grid ---------------------------------


def zipparse(ifile):
    """Parse the xml file into an element tree object when the xml is in a zip
    file.

    """

    # Open/decompress zip file
    with ZipFile(ifile, 'r') as myzip:

        # Get all files in zip
        fileList = myzip.namelist()

        # Check how many files
        if len(fileList) > 1:
            print("WARNING: Multiple files in zip. Using first file found")

        # Get the xml file within the zip
        xmlFile = myzip.open(fileList[0], 'r')

        # Parse xml
        tree = parse(xmlFile)

    return tree


def read_root(ifile):
    """Read the input xml shakemap file. Can handle the text file or zipped file

    """

    if is_zipfile(ifile):
        obj = zipparse(ifile)
    else:
        # Parse from xml file into an element tree object
        obj = parse(ifile)

    # Return the xml root
    return obj.getroot()


def print_rootitems(root):
    """ Print the attributes of the shakemap, event ID, version, etc """
    print("Shakemap key details:")
    for t, v in root.items():
        print("\t", t, ":", v)
    return


def print_eventinfo(eventInfo):
    """Get the event parameters
    IN:
      eventInfo (dict) which is the attribute of 'event' under the root tree
    """
    print("Event info:")
    for t, v in eventInfo.items():
        print("\t", t, ":", v)
    return


def read_gridlims(root, ns):
    """ Get the lon/lat limits of the grid from the xml header """
    gridSpecs = root.find('shakemap:grid_specification', ns).attrib
    xylims = [float(gridSpecs.get('lon_min')), float(gridSpecs.get('lon_max')),
              float(gridSpecs.get('lat_min')), float(gridSpecs.get('lat_max'))]
    return xylims


def read_griddims(root, ns):
    # Find the grid specifications
    gridSpecs = root.find('shakemap:grid_specification', ns).attrib
    nx, ny = int(gridSpecs.get('nlon')), int(gridSpecs.get('nlat'))

    # for t,v in gridSpecs.items():  print t, ":", v

    return nx, ny


def read_gridvals(root, ns, intensMeasure, ny, nx):

    # Number of columns in the grid
    nF = len(root.findall('shakemap:grid_field', ns))

    # Get all the gridded data as a text string
    t = root.find('shakemap:grid_data', ns).text

    # Convert to number. Previously used np.fromstring(), but this
    # works faster
    t = t.replace('\n', ' ').strip()
    t = t.split(sep=' ')
    a = np.array(t, dtype=float)

    # Get the grid column headers
    fnms = [None]*nF
    for f in root.findall('shakemap:grid_field', ns):
        i = int(f.get('index')) - 1
        fnms[i] = f.get('name')

    # work out which column stores our intensity measure
    if intensMeasure in fnms:
        iCol = fnms.index(intensMeasure)
    else:
        print("Valid fieldnames:\n", fnms)
        raise ValueError('\'%s\' is not in list' % intensMeasure)

    # TODO: check if intensity measure wasn't there

    # Note it is y-ordered array read in upside down at first
    gridVal = np.flipud(a[iCol::nF].reshape([ny, nx]))

    return gridVal


def check_uncgrid(root2, hdr, namespace, xylims):

    isOk = True

    # Check the event id and version are the same
    for fnm in ('event_id', 'shakemap_id', 'shakemap_version'):
        if root2.get(fnm) != hdr[fnm]:
            print("ERROR: mismatch in %s: %s vs %s" %
                  (fnm, root2.get(fnm), hdr[fnm]))
            isOk = False

    # Check the limits and spacing are the same
    theseLims = read_gridlims(root2, namespace)
    if abs(np.sum(np.array(theseLims) - xylims)) > 1e-12:
        print("ERROR: mismatch in grid limits for uncertainty file")
        print(theseLims, "vs", xylims)
        isOk = False

    return isOk


# ------------------------------------------------------------------------------


class USGSshakemapGrid:
    """ Class defines a USGS shakemap grid for a single intensity measure

    Properties
     hdr: root attributes
     eventInfo: event attributes
     x0: lon coordinate of west-most grid cell center
     x1: lon coordinate of east most grid cell center
     y0: lat coordinate of south-most grid cell center
     y1: lat coordinate of north-most grid cell center
     intensMeasure: string identifier for which intensity measure is stored
     grid: 2-d numpy array of intensity values
       latitude (y) is the first dimension, longitude (x) is the 2nd dimension
       the first value of the grid, ie grid[0,0] is the SW most point
     grid_std: 2-d numpy array of the standard deviations
    """

    def __init__(self, ifile_xml, intensMeasure, ifile_unc=None,
                 isQuiet=False, ignoreSVEL600=False):
        """Initiate the class based on the grid.xml file.

        Focus on one specific intensity measure.

        Keyword arguments:

        ifile_xml : (string) xml file downloaded from USGS, can be text or zip.
        intensMeasure: (string) which intensity measure to use from the file,
                       corresponding to the name of a grid column/field within
                       the file. e.g. 'mmi', 'pga', 'psa03'

        isQuiet : (logical) True will report details of the import to
                  terminal. Default is False.

        """

        # Namespace for reading the xml files
        namespace = {'shakemap':
                     'http://earthquake.usgs.gov/eqcenter/shakemap'}

        # Parse the XML
        root = read_root(ifile_xml)

        # Get the shakemap details
        self.hdr = root.attrib
        if not isQuiet:
            print_rootitems(root)

        # Display event information
        self.eventInfo = root.find('shakemap:event', namespace).attrib
        # print_eventinfo(self.eventInfo)

        # Get grid limits as vector [x0, x1, y0, y1]; these are the coords of
        # the first and last grid centers
        xylims = read_gridlims(root, namespace)
        self.x0 = xylims[0]
        self.x1 = xylims[1]
        self.y0 = xylims[2]
        self.y1 = xylims[3]

        # Get grid dimensions, x is lon, y is lat
        # Note the precision is worse if we read the grid spacing from the file
        nx, ny = read_griddims(root, namespace)

        # Get grid itself, axis=0 is the y/lat axis
        self.grid = read_gridvals(root, namespace, intensMeasure, ny, nx)
        self.intensMeasure = intensMeasure

        # Check if we want to remove points in the sea
        if ignoreSVEL600:
            t = read_gridvals(root, namespace, 'SVEL', ny, nx)
            t[t == 600] = np.nan
            t[~np.isnan(t)] = 1.0
            self.grid = self.grid*t
        else:
            t = np.ones(self.grid.shape)

        # Add the uncertainty file
        self.grid_std = np.zeros(np.shape(self.grid))
        if ifile_unc is not None:
            # Add from file
            # Parse the XML
            root2 = read_root(ifile_unc)

            if check_uncgrid(root2, self.hdr, namespace, xylims) is True:
                # Import the grid
                self.grid_std = read_gridvals(root2, namespace,
                                              'STD'+self.intensMeasure,
                                              np.size(self.grid, 0),
                                              np.size(self.grid, 1))
                self.grid_std = self.grid_std*t

        return

    # Get the grid spacing
    def dx(self):
        """Return the grid spacing in the lon direction. Won't work if
        crossing the date line

        """
        return (self.x1 - self.x0)/(self.nx()-1)

    def dy(self):
        """Return the grid spacing in the lat direction. Won't work if
        crossing the date line

        """
        return (self.y1 - self.y0)/(self.ny()-1)

    # Get the grid dimensions
    def nx(self):
        return np.size(self.grid, axis=1)

    def ny(self):
        return np.size(self.grid, axis=0)

    # Functions to return the limits of the grid space
    def xlims(self, isCenters=False):

        """Return numpy array of [min, max] of x (lon) coordinates.

        Keyword arguments:
        centers : (logical) Return the grid cell centers if True.
                            Return the grid cell edges if False (default).
        """
        xlims = np.array((self.x0, self.x1))

        if not isCenters:
            # Shift half a grid cell to get the edge
            xlims = xlims + self.dx()*np.array((-0.5, 0.5))

        return xlims

    def ylims(self, isCenters=False):
        """Return numpy array of [min, max] of y (lat) coordinates.

        Keyword arguments:
        centers : (logical) Return the grid cell centers if True.
                            Return the grid cell edges if False (default).
        """
        ylims = np.array((self.y0, self.y1))

        if not isCenters:
            ylims = ylims + self.dy()*np.array((-0.5, 0.5))

        return ylims

    def xylims(self, isCenters=False):
        """Return numpy array min/max of x(lon) and y (lat) coordinates.

        Returns numpy array [Xmin,Xmax,Ymin,yMax]

        Keyword arguments:
        isCenters : (logical) Extent of grid cell centers if True.
                    Full extent grid up to cell edges if False (default)
        """
        return np.r_[self.xlims(isCenters), self.ylims(isCenters)]

    # Get the coordinates of the grid centers
    def xcoords(self, idx=np.array([])):
        """Return the x coordinate of the grid cell centers. Specify which
        indices if only a subset.

        """
        xi = np.linspace(self.x0, self.x1, self.nx())
        if np.size(idx) != 0:
            xi = xi[idx]

        return xi

    def ycoords(self, idx=np.array([])):
        yi = np.linspace(self.y0, self.y1, self.ny())
        if np.size(idx) != 0:
            yi = yi[idx]

        return yi

    # Return the shakemap in a different format
    def as_dict(self):
        """Return the grid coordinates and grid values as a dictionary
        output dict field names are 'lon', 'lat', 'median', 'std'
        """
        return {'lon': np.tile(self.xcoords(), self.ny()),
                'lat': np.repeat(self.ycoords(), self.nx()),
                'm0': self.grid.flatten(order='C'),
                'sd': self.grid_std.flatten(order='C')}

    # Get the grid index for specified coordinates
    def grididx(self, xpts, ypts):
        # Get the indices of the grid for each point
        iLon = np.floor(self.nx()*(xpts - self.x0)/(self.x1 - self.x0))
        iLon = iLon.astype(int)

        iLat = np.floor(self.ny()*(ypts - self.y0)/(self.y1 - self.y0))
        iLat = iLat.astype(int)

        # Set nan where outside of grid
        iLat = ma.masked_outside(iLat, 0, self.ny()-1)
        iLon = ma.masked_outside(iLon, 0, self.nx()-1)

        return iLon, iLat

    # Lookup from grid at specified coordinates
    def lookup(self, xpts, ypts):
        """ Find grid intensities at each of the points """

        # Get the indices of the grid for each point
        iLon, iLat = self.grididx(xpts, ypts)

        # Initialize outputs
        mean = np.empty(xpts.shape)
        std = np.empty(ypts.shape)

        # Lookup
        isIn = ~iLon.mask & ~iLat.mask
        mean[isIn] = self.grid[iLat[isIn], iLon[isIn]]
        std[isIn] = self.grid_std[iLat[isIn], iLon[isIn]]

        # Set nan where outside of grid
        mean[~isIn] = np.nan
        std[~isIn] = np.nan

        return mean, std

    # Adjust the grid extent
    def clipxy(self, xyclip):
        """ Clip the grid according to a [xmin, xmax, ymin, ymax] array.

        Keyword Arguments:
        xyclip : numpy array of four numbers [xmin, xmax, ymin, ymax]
        """
        # Get grid coordinates
        xi = self.xcoords()
        yi = self.ycoords()

        # Find which are within the bounds selected
        # TODO
        isInx = (((xi+0.5*self.dx()) >= xyclip[0]) &
                 ((xi-0.5*self.dx()) <= xyclip[1]))
        isIny = (((yi+0.5*self.dy()) >= xyclip[2]) &
                 ((yi-0.5*self.dy()) <= xyclip[3]))

        # Find x indices within bounds selected. Note where returns a tuple
        idx1 = np.where(isInx)[0]
        j0, j1 = idx1[0], idx1[-1]

        # Find y coords withinn bounds selected
        idx0 = np.where(isIny)[0]
        i0, i1 = idx0[0], idx0[-1]

        # Update the grid
        self.grid = self.grid[i0:i1+1, j0:j1+1]
        self.grid_std = self.grid_std[i0:i1+1, j0:j1+1]
        self.x0 = xi[j0]
        self.x1 = xi[j1]
        self.y0 = yi[i0]
        self.y1 = yi[i1]
        # dx and dy remain the same

        return

    def cliplowvalues(self, minIntensity):
        """Clip the grid to remove border where all intensity is lower than a
        value

        Keyword Arguments:
        minIntensity : (float) the new x/y bounds will include all
                       intensities >= minIntensity.

        """

        # Find values above the grid limits
        isOver = self.grid >= minIntensity

        # Get grid coordinates of these cells
        xi = self.xcoords(np.any(isOver, axis=0))  # use axis=0 since y is axis=1
        yi = self.ycoords(np.any(isOver, axis=1))

        # Get half of x and y spacing
        halfdx, halfdy = 0.5*self.dx, 0.5*self.dy

        # Get the clip bounds
        xyclip = np.array([xi[0]-halfdx, xi[-1]+halfdx,
                           yi[0]-halfdy, yi[-1]+halfdy])

        # Apply the clip
        self.clipxy(xyclip)

        return
