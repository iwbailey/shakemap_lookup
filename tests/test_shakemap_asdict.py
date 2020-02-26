"""Test that we can get the shakemap into a table as expected """


# Libraries ------------------------------------------------------------------
import os
import pandas as pd

from shakemap_utils import USGSshakemapGrid


# Parameters ------------------------------------------------------------------
idir = os.path.join(os.path.expanduser('~'), 'Downloads', 'usgs_shakemap')
eventid = '1000dyad_v11.0'
ifile_sm = os.path.join(idir, ('grid_%s.xml.zip' % eventid))
ifile_unc = os.path.join(idir, ('uncertainty_%s.xml.zip' % eventid))


# Script ----------------------------------------------------------------------


print('Reading the shakemap from file with MMI...')
thisSM = USGSshakemapGrid(ifile_sm, 'MMI', ifile_unc=ifile_unc)

# Export as datatable
sm = pd.DataFrame.from_dict(thisSM.as_dict())
print("Event info:\n", thisSM.eventInfo)

# Display
print(sm[(sm['lon'] < -158.849) & (sm['lat'] == 22)])

# Check grid dimensions consistent with header
print("\nFrom input xml file:")
os.system(('zcat %s | gawk \'{if(substr($0,0,1)!="<")print($0)}\' | head' %
           ifile_sm))
print('...')

# Display
print(sm[(sm['lon'] > -154.651) & (sm['lat'] == 18.5)])

print("\nFrom input xml file:")
os.system(('zcat %s | gawk \'{if(substr($0,0,1)!="<")print($0)}\' | tail' %
           ifile_sm))
