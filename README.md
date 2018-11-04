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

This should work as long as you don't access the web via a proxy

## Backlog

- TODO
