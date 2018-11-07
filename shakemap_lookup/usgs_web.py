"""Functions that get stuff from USGS webservices """

# * Libraries ----
import requests
import json
import os
import sys

# * Functions ----


def search_usgsevents(searchParams,
                      urlEndpt='https://earthquake.usgs.gov/fdsnws/event/1/query',
                      maxNprint=30,
                      isQuiet=False):
    """Search the USGS for events satisfying the criteria and return a list of
    events

    IN:
    searchParams is a dict containing the search parameters used for the query
    urlEndpt [string] is the web address used for the search.

    API doc here... https://earthquake.usgs.gov/fdsnws/event/1/

    OUT:
    A list of events satisfying the conditions in a json structure
    """

    # Make a copy of the search params so we can modify here
    mySearch = searchParams
    mySearch['format'] = 'geojson'
    mySearch['jsonerror'] = 'true'

    # Check max number of events returned
    if 'limit' not in mySearch:
        mySearch['limit'] = 2e4
    elif mySearch['limit'] > 2e4:
        print('WARNING: Based on USGS doc, limit should not be over 20,000')

    # Send the query and get the response
    if ~isQuiet:
        print("Sending query to get events...")
    resp = requests.get(urlEndpt, params=mySearch)

    # Parse the json
    if ~isQuiet:
        print("Parsing...")
    evList = json.loads(resp.content)

    # Check for errors
    if evList['metadata']['status'] == 400:
        print('ERROR in catalog search request: %s' %
              (evList['metadata']['error']))

        # TODO: if we are running this in a loop we may not want to exit, just jump to next
        sys.exit()

    # Count number of events
    nEv = len(evList['features'])

    # List events to terminal
    if ~isQuiet:
        print('\t...%i events returned (limit of %i)' %
              (nEv, mySearch['limit']))

        for ev in evList['features'][:maxNprint]:
            prop = ev['properties']
            print("\t\t", prop['code'], ":", prop['title'])

        if nEv > maxNprint:
            print("\t[Truncated after max print limit of %i exceeded]" %
                  maxNprint)

    # TODO: if we got the same number back as our limit, should do a query on
    # the count

    return evList


def count_usgsevents(searchParams,
                     urlEndpt='https://earthquake.usgs.gov/fdsnws/event/1/count'):
    """Search the USGS for events satisfying the criteria and return a count of
    events

    IN:
    searchParams is a dict containing the search parameters used for the query
    urlEndpt [string] is the web address used for the search.

    API doc here... https://earthquake.usgs.gov/fdsnws/event/1/

    OUT:
    Number of events

    """

    # Make a copy of search parameters we can modify
    mySearch = searchParams

    # We can only deal with text output here
    mySearch['format'] = 'text'

    # TODO: There is probably other stuff that can't be handled by the count
    # option

    # Send the query and get the response
    print("Sending query to get events...")
    resp = requests.get(urlEndpt, params=mySearch)

    # TODO check if we received anything back

    # Return the number
    return float(resp.content)


def choose_event(evList, maxNchoice=20):
    """Choose which event from the event list for which we want to get the
    shakemap

    """
    # Restrict to the maximum number of display items
    choices = evList['features'][:maxNchoice]

    # Extract a list of event names
    print("\nUSER SELECTION OF EVENT:")
    print("========================")
    for idx, n in enumerate(choices):
        print('%4i: %s (%s)' % (idx,
                                n['properties']['title'],
                                n['properties']['code']))
        print('None: First on list\n  -1: Exit')

    # Ask user to select from the list, default is first item
    iEv = int(input("\nChoice: ") or 0)

    # If the user selected exit, then exit
    if iEv < 0 or iEv >= len(choices):
        print("\t...Exit")
        sys.exit()

    print("\t... selected %s (%s)\n" % (choices[iEv]['properties']['title'],
                                        choices[iEv]['properties']['code']))

    return evList['features'][iEv]


def choose_shakemap(smDetail):
    """When there are multiple shakemaps for the same event, allow the user to
    choose one

    IN: output from the query for detailed event info
    """

    # Default is the first and only option
    iEv = 0

    # Check if there is more than one shakemap available
    if len(smDetail) > 1:
        print("\nUSER SELECTION OF SHAKEMAP:")
        print("===========================")
        # Loop through shakemaps in the detail
        for idx, smd in enumerate(smDetail):
            # Print the number
            print("Option %i:" % idx)

            # Print the shakemap details
            for prop in ['eventsourcecode', 'version', 'process-timestamp']:
                print('\t%18s: %s' % (prop, smd['properties'][prop]))
        iEv = int(input("\nChoice [default 0]: ") or 0)
        print("\t... selected %i\n" % iEv)

        # Check for valid option
        if iEv < 0 or iEv >= len(smDetail):
            print("\t...Exit")
            sys.exit()

    return iEv


def query_shakemapdetail(evproperties, isChoose=True, isQuiet=False):
    """From the event properties for the event, get the URL for the json with
    detailed event data. Download the json and extract the shakemap parts

    TODO: description a
    """

    # Get detailed info for top event
    eventId = evproperties['code']

    # Find the URL for the detailed data of this event.
    urlEvDetail = evproperties['detail']

    # Query the detailed json from the web
    if ~isQuiet:
        print("Querying detailed event info for eventId=%s..." % eventId)
    resp2 = requests.get(urlEvDetail)
    detail = json.loads(resp2.content)

    # Extract only the shakemap detail
    smDetail = detail['properties']['products']['shakemap']
    if ~isQuiet:
        print("\t...%i shakemaps found" % len(smDetail))

    if isChoose:
        # If there's more than one shakemap, choose one
        iSM = choose_shakemap(smDetail)
    else:
        iSM = 0

    return smDetail[iSM]


def get_shakemapgrid_urls(smDetail, filetype='xml.zip'):
    """Get the detailed json, including the webstring for the most recent shakemap,
    for a specified event

    """
    if filetype == 'xml.zip':
        # Get the URLs for downloading the shakemap grid
        gridURL = smDetail['contents']['download/grid.xml.zip']['url']

        # ...And the corresponding uncertainty grid
        uncURL = smDetail['contents']['download/uncertainty.xml.zip']['url']
    elif filetype == 'xml':
        gridURL = smDetail['contents']['download/grid.xml']['url']
        uncURL = smDetail['contents']['download/uncertainty.xml']['url']

    return gridURL, uncURL


def download_xmlzip(gridURL, ofilename, eventId, version):
    """Write the xml zip file and also create a backup """

    # Check if file already exists
    if os.path.exists(ofilename):
        print("File %s exists... skipping download" % ofilename)
        # TODO: user prompt here in case we want to overwrite
        return

    print("Downloading shakemap from %s" % gridURL)
    resp3 = requests.get(gridURL)
    xmlZip = resp3.content

    # TODO: case where we didn't get anything back

    # Open the output file as a binary
    with open(ofilename, "wb") as zfile:

        # Write the downloaded zip straight to file. This overwrites anything
        # there already
        zfile.write(xmlZip)
        print("Written to %s" % ofilename)

    return


def download_shakemapgrid(searchParams, odir='.', isQuiet=False):
    """Find an earthquake record on the USGS website and download its shakemap and
    uncertainty grid.

    """
    # TODO: Default behavior if search doesn't exist

    if ~isQuiet:
        print('Enforcing API search to require producttype=shakemap')
    searchParams['producttype'] = 'shakemap'

    # TODO: input option should ask if we want the zip file

    # TODO: more explicit in options about backup file names

    # Check the output folders exist
    if odir != '' and not os.path.exists(odir):
        if ~isQuiet:
            print('Making output folder %s' % odir)
        os.makedirs(odir)

    # Get list of events
    evList = search_usgsevents(searchParams)

    # Exit if nothing found
    if evList['metadata']['count'] == 0:
        print("Nothing found")
        return None, None

    # Choose the event if multiple
    thisEvent = choose_event(evList)

    # Get the shakemap detail for the event
    smDetail = query_shakemapdetail(thisEvent['properties'])

    # Get the event Id & shakemap version for record keeping
    eventId = smDetail['properties']['eventsourcecode']
    version = float(smDetail['properties']['version'])
    print("shakemap_version %.1f" % version)

    # Extract the shakemap grid urls and version from the detail
    gridURL, uncGridURL = get_shakemapgrid_urls(smDetail, filetype='xml.zip')

    # Define the filenames
    ofilename = os.path.join(odir, ('%s_%s_v%04.1f.xml.zip' %
                                    ('grid', eventId, version)))
    ofilename_unc = os.path.join(odir, ('%s_%s_v%04.1f.xml.zip' %
                                        ('uncertainty', eventId, version)))

    # Download and write to file
    download_xmlzip(gridURL, ofilename, eventId, version)

    # Write the uncertainty grid to file
    download_xmlzip(uncGridURL, ofilename_unc, eventId, version)

    # Print final output
    print("DONE. Files as follows:")
    print(ofilename)
    print(ofilename_unc)
    print("")

    return ofilename, ofilename_unc


def test_searchanddownload():
    """Test search and download the May 2018 Hawaii earthquake"""

    searchParams = {  # Parameters for Hawaiian earthquake
        'starttime':  "2018-05-01",
        'endtime':  "2018-05-17",
        'minmagnitude':  6.8,
        'maxmagnitude': 10.0,
        'mindepth': 0.0,
        'maxdepth': 50.0,
        'minlongitude': -180.0,
        'maxlongitude': -97.0,
        'minlatitude':  0.0,
        'maxlatitude': 45.0,
        'limit': 50,
        'producttype': 'shakemap'}
    print("Search Parameters:")
    print(searchParams)

    # Store in sub-folder of Downloads
    outdir = os.path.join(os.path.expanduser('~'), 'Downloads',
                          'usgs_shakemap')

    print("\nOutput folder:")
    print(outdir)

    # Run
    download_shakemapgrid(searchParams, outdir)

    return
