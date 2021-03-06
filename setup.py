"""
Installation of package
"""
import setuptools

# Get the long description from the readme
with open("README.md", "r") as fh:
    long_description = fh.read()

# All details
setuptools.setup(
    name='shakemap_utils',
    version='0.1.0',
    url='',
    author='Iain Bailey',
    author_email='iainbailey@gmail.com',
    description='Lookup USGS shakemap values at specified locations',
    long_description=long_description,
    long_description_content_type="text/markdown",
    scripts=['scripts/find_and_download_shakemap.py',
             'scripts/shakemap_lookup.py',
             'scripts/shakemap_estimate_damage.py'],
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT ",
        "Operating System :: OS Independent",
    ),
)
