# -*- coding: utf-8 -*-
# Python code to interpolate NetCDF4 data to height - given hgt and vars
# Code also produces plot of weather forecast 

import numpy as np, os, pandas as pd, matplotlib.pyplot as plt, datetime, sys
from netCDF4 import Dataset, num2date
from scipy import interpolate
plt.switch_backend('agg')

# Get location name, elevation, and directory from the command line (fed-in by Download.sh)
name=sys.argv[1]
elev=np.float(sys.argv[2])
outdir=sys.argv[3]

## Define input
fin=Dataset("%sForecast_GFS1D.nc"%outdir,"r")
nctime=fin.variables["time"]

# Get location name an elevation from the command line (fed-in by Download.sh)
name=sys.argv[1]
elev=np.float(sys.argv[2])

# Define variables and levels
vs=["t","u","v"]
#lev_st=900
#lev_stp=300-1
#levels=range(lev_st,lev_stp,-100)
nctime=fin.variables["time"]
nt=len(nctime)
out={}

# Setup ref x-coordinates - the levels (dimensions: ntime, nlevels)
#x=np.squeeze(np.column_stack([fin.variables["HGT_%.0fmb"%ii] for ii in levels]))
x=np.squeeze(fin.variables["gh"][:,:,:,:])

# Iterate over vars (vs) and interpolate. Note that each 
# array, when squeezed, has dimensions ntime | nlevels
indata={}
for v in vs:

	# Create input grid (dimensions: ntime, nlevels )
	# y=np.squeeze(fin.variables[v+"_%.0fmb"%ii] for ii in levels]))

	# Interpolate 
	out[v]=np.squeeze([\
		np.interp(elev,x[ii,:],\
		np.squeeze(fin.variables[v][:,:,:,:])[ii,:]) for ii in range(nt)])

# Make adjustments
out["t"]=out["t"]-273.15 # Convert to C
out["wind"]=np.sqrt(np.power(out["u"],2)+np.power(out["v"],2))

# Create time index and put everything in Pandas DataFrame (for easy date-handling)
dates=num2date(nctime[:],units = nctime.units,calendar = nctime.calendar)
df=pd.DataFrame(data=out,index=dates)

# Plot temp
fig,ax=plt.subplots(1,1)
f1=df["t"].plot(ax=ax,color="blue",marker="+")
ax.set_ylabel("Air Temperature ($^{\circ}C)$",color="blue")
ax.set_title(name)
# ax.grid(True)

# Plot wind - second y axis
ax2=ax.twinx()
f2=df["wind"].plot(ax=ax2,color="red",marker="*")
ax2.set_ylabel("Wind Speed (m/s)",color="red")
#ax2.grid(True)
fig.set_size_inches(9,5)
fig.savefig("%s%s.png"%(outdir,name),dpi=300)
ax.set_title(name)
print("Forecast processed: See '%s.png' in %s"%(name,outdir))

# Update GitHub
cd /home/lunet/gytm3/Everest2019/Forecasting && /usr/bin/git commit -a -m "6-hourly Update... `date`"

# Send data to Git server
cd /home/lunet/gytm3/Everest2019/Forecasting && /usr/bin/git push https://climatom:G3j18Rbp@github.com/climatom/Everest_Forecasting.git

