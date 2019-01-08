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

# *********************************
# Subtract one day (for testing!)
#date=date-datetime.timedelta(days=1)
# *********************************

# Define the hour
sel_hour=18

# Set the date string
sel="%02d%02d%02d%02d"%(date.year,date.month,date.day,sel_hour)

print sel,sel_hour,nhrs

# Call bash script to actually get the data. Note that, in turn, 
# Download.sh also calls Process.py to interpolate to locations. 
os.system("bash %sDownload_KCC_EXTENDED.sh %s %s %s %s" %(outdir,outdir,sel,sel_hour,nhrs))
