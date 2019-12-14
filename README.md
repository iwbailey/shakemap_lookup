# ShakeMap Lookup

This is a simple package for working with USGS shakemaps to get the intensity
and damage potential at a given set of locations

## Install locally
```
pip install --user -e .
```

## Example scripts
See scripts folder. To download the example shakemap (Hawaii earthquake) to
your downloads folder:

```
cd scripts
cp example_search_params.yaml search_params.yaml
python script01_get_shakemap.py
```

Running the script should do the following:

1. Search for an earthquake on the USGS server according to the parameters in the `search_params.yaml` file.
2. Prompt you to check which of the candidate earthquakes you want.
3. Search for any ShakeMaps associated with the selected earthquake.
4. Prompt you to check which Shakemap you want to download.
5. Download the intensity grid and associated uncertainty grid in xml.zip format.

You might have issues if accessing the web via proxy.

## Resources
For the lat lon search parameters, the following has a list of bounding box per
country (with some issues highlighted in the comments below).

[https://gist.github.com/graydon/11198540](https://gist.github.com/graydon/11198540)

## Backlog

- TODO
