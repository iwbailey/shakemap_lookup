# ShakeMap Utils

This is a simple package for working with USGS shakemaps to download them and get the intensity
and damage potential at a given set of locations

## Install locally
```
pip install --user -e .
```

## Example scripts
### Find and Download
To download the example shakemap (Hawaii earthquake) to your downloads folder:

```
cd tests/example_download
find_and_download_shakemap.py -i example_search_params.yaml -o ./
```

Running the script should do the following:

1. Search for an earthquake on the USGS server according to the parameters in the `search_params.yaml` file.
2. Prompt you to check which of the candidate earthquakes you want.
3. Search for any ShakeMaps associated with the selected earthquake.
4. Prompt you to check which Shakemap you want to download.
5. Download the intensity grid and associated uncertainty grid in xml.zip format.

You might have issues if accessing the web via proxy.

### Shakemap lookup
To lookup the shakemap intensity from a downloaded shakemap for a set of coordinates

```
cd tests/example_lookup
shakemap_lookup.py -i Hawaii_Mile_Markers_v2.csv -s ../example_download/grid_70116556_v01.0.xml --intensity_measure 'MMI'
```


## Resources
For the lat lon search parameters, the following has a list of bounding box per
country (with some issues highlighted in the comments below).

[https://gist.github.com/graydon/11198540](https://gist.github.com/graydon/11198540)

## Backlog

- TODO
