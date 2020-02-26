import numpy as np
import matplotlib.pyplot as plt


def plot_shakemap(smGrid):
    """ Plot the shakemap. Takes ShakeMap class as input
    """
    m = Basemap(llcrnrlon=smGrid.x0, llcrnrlat=smGrid.y0,
                urcrnrlon=smGrid.x1, urcrnrlat=smGrid.y1,
                projection='merc', resolution='i')

    # Plot the shakemap as colours
    cax = m.imshow(smGrid.grid, vmin=2, vmax=10)

    m.drawcoastlines()
    m.drawstates()
    # m.drawcounties()
    m.drawparallels(range(-90, 90, 1), labels=[1, 0, 0, 0], fontsize=10)
    m.drawmeridians(range(-180, 180, 1), labels=[0, 0, 0, 1], fontsize=10)

    m.colorbar(cax, ticks=range(0, 10, 1), label=smGrid.intensMeasure)

    return m, cax


def plot_shakemap_unc(smGrid):
    """ Plot the shakemap. Takes ShakeMap class as input
    """
    m = Basemap(llcrnrlon=smGrid.x0, llcrnrlat=smGrid.y0,
                urcrnrlon=smGrid.x1, urcrnrlat=smGrid.y1,
                projection='merc', resolution='i')

    # Plot the shakemap as colours
    cax = m.imshow(smGrid.grid_std, vmin=0, vmax=1.5)

    m.drawcoastlines()
    m.drawstates()
    # m.drawcounties()
    m.drawparallels(range(-90, 90, 1), labels=[1, 0, 0, 0], fontsize=10)
    m.drawmeridians(range(-180, 180, 1), labels=[0, 0, 0, 1], fontsize=10)

    m.colorbar(cax, ticks=np.arange(0, 1.5, 0.2), label="STD")

    return m, cax


def plot_mmiprob(fragTable):
    """ Plot the fragility curves as read in
    IN: Pandas data frame
          column 1 is named 'MMI'
          columns 2+ are named the damage states
    OUT: pyplot figure handle
    """
    # fig = plt.figure()
    fig, ax = plt.subplots(1, 1, facecolor='white')

    for column in fragTable.columns[1:]:
        ax.plot(fragTable.MMI, fragTable[column].values, label=column)

    ax.set_xlabel('MMI')
    ax.set_ylabel('ProbExceedance')
    ax.grid('on')
    ax.legend(loc=2, frameon=False, framealpha=0.5)

    return fig, ax


def plot_subregbox(smGrid, xySubReg):
    """ Plot the shakemap with a box outlining the search region on it
    """
    fig = plt.figure()
    m, cax = plot_shakemap(smGrid)

    # Add the search box that includes all min intensities
    m.plot(xySubReg[np.array([0, 0, 1, 1, 0])],
           xySubReg[np.array([2, 3, 3, 2, 2])], '-r', latlon=True)

    return fig


def plot_inlocations(locns, inLocns, xyBox):
    """Plot the locations and highlight the ones that are in the bounds"""
    fig = plt.figure()
    plt.plot(np.array(locns['lon']), np.array(locns['lat']), 'xk')
    plt.plot(np.array(inLocns['lon']), np.array(inLocns['lat']), '+r')
    plt.plot(xyBox[np.array([0, 0, 1, 1, 0])],
             xyBox[np.array([2, 3, 3, 2, 2])], '-r')

    plt.axis('equal')
    plt.title('Check locations in box')

    return fig
