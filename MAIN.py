# Coordinating Python script to run GFS download
# -*- coding: utf-8 -*-
import sys,datetime, os, numpy as np

### Parameters
# Out directory
outdir=sys.argv[1]
# Get number of hour to extract data for. Kept as command-line parameter for now. 
nhrs=sys.argv[2]
###

# Start by purging output directory of GFS.nc files 
fs = [ii for ii in os.listdir(outdir) if "GFS" in ii and ".nc" in ii]
if len(fs)>0:
	for ii in fs: os.remove(outdir+ii)


# Current datetime
date=datetime.datetime.now()

# Convert date to nearest 6 hours just gone
const=date.year*1e6+date.month*1e4+date.day*1e2 # base date 
thresh=date.year*1e6+date.month*1e4+date.day*1e2+date.hour - 5.5 # cant be later than this!
# - the GFS forecst seems to be posted ~ 4-5 hours after initialization time; subtracting 
# 5.5 hours ensures we don't ask for a forecast that's not yet been posted!

# find previous times
poss=np.array([const+ii for ii in range(0,24,6)],dtype=np.int); idx=poss<=thresh 
sel=poss[idx][-1] # get the latest from the previous times

# Pull out the hour
sel_hour=("%02d"%sel)[-2:]

# Call bash script to actually get the data. Note that, in turn, 
# Download.sh also calls Process.py to interpolate to locations. 
os.system("bash %sDownload.sh %s %s %s %s" %(outdir,outdir,sel,sel_hour,nhrs))
