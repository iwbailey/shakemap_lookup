"""
Search the USGS for an earthquake and interactively choose the ShakeMap to download.

"""
import argparse as ap
import yaml
import sys
import os

# From this project
from shakemap_utils import download_shakemapgrid


def get_args():

    # Get the input arguments
    parser = ap.ArgumentParser(description='Download a USGS ShakeMap',
                               formatter_class=ap.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i', '--ifile',
                        metavar='search_params.yaml',
                        type=str,
                        nargs='?',
                        default='search_params.yaml',
                        help='.yaml file with the event search parameters')

    parser.add_argument('-o', '--odir',
                        metavar='path/to/save/output/',
                        type=str,
                        nargs='?',
                        default=os.path.join(os.path.expanduser('~'),
                                             'Downloads',
                                             'usgs_shakemap'),
                        help='Path to store downloaded ShakeMap files')

    parser.add_argument('--proxy',
                        metavar='http://proxy.com:8008',
                        type=str,
                        nargs='?',
                        default=None,
                        help='')

    args = parser.parse_args()

    return args


def main(args=get_args()):
    """ Script """

    # Set the proxy for all traffic
    if args.proxy is not None:
        os.environ['http_proxy'] = args.proxy
        os.environ['HTTP_PROXY'] = args.proxy
        os.environ['https_proxy'] = args.proxy
        os.environ['HTTPS_PROXY'] = args.proxy

    # Read the search parameters from the file
    with open(args.ifile, 'r') as stream:
        try:
            # Expect the yaml file to contain fields that go into a dict
            searchParams = yaml.load(stream, Loader=yaml.Loader)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit()

    # Get the shakemaps and save to a file
    ofilename, ofilename_unc = download_shakemapgrid(searchParams, args.odir)

    if ofilename is None:
        sys.exit()

    print("DONE")

    return


if __name__ == '__main__':
    main()
