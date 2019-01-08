# -*- coding: utf-8 -*-
# Python code to interpolate NetCDF4 data to height - given hgt and vars
# Code also produces plot of weather forecast 

import numpy as np, os, pandas as pd, matplotlib.pyplot as plt, datetime, sys, smtplib
from email.mime.text import MIMEText
from netCDF4 import Dataset, num2date
from scipy import interpolate
import GeneralFunctions as GF
#======================================================#
# E-mail params
gmail_user = 'lboroweather@gmail.com'  
gmail_password = '83w9bWtU'
to=["climatom86@gmail.com","t.matthews@lboro.ac.uk","perrylb@appstate.edu",\
"heather.guy@ncas.ac.uk"]
#======================================================#
#======================================================#
# Functions
#======================================================#
# Function to send e-mail 
def send_mail(msgtxt,to):
    msg=MIMEText(msgtxt)
    msg['From'] = 'AutoForecast'
    msg['To'] = ",".join(to)
    msg.as_string()
    try:  
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user,to,msg.as_string())
        server.close()
	print 'Email sent!'
    except:  
        print 'Something went wrong...'
   

#======================================================#    

#======================================================#
# Process forecasts
#======================================================#
# Get location elevation and directory from the command line (fed-in by Download.sh)
elev=np.float(sys.argv[1])
outdir=sys.argv[2]

## Define input
fin=Dataset("%sGFS_press_int.nc"%outdir,"r")
nctime=fin.variables["time"]
fin_precip=Dataset("%sGFS_surface_int.nc"%outdir,"r")
nctime_precip=fin_precip.variables["time"]

# Define variables and levels
vs=["t","u","v","r"]
nt=len(nctime)
out={}

# Setup ref x-coordinates - the levels (dimensions: ntime, nlevels)
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

# Add precip
out["precip"]=np.squeeze(fin_precip.variables["prate"][:,:,:])*3600. # Hourly total
# Create time index and put everything in Pandas DataFrame (for easy date-handling)
dates=num2date(nctime[:],units = nctime.units,calendar = nctime.calendar)
df=pd.DataFrame(data=out,index=dates)
df.set_index(df.index+pd.Timedelta(hours=6),inplace=True) # Nepali time (almost!)

# Create date vars for entry to e-mail text
df["year"]=df.index.year
df["month"]=df.index.month
df["day"]=df.index.day
df["hour"]=df.index.hour

# Set "Nepali today" (just ~6 hours later)
today=date=datetime.datetime.now()+datetime.timedelta(hours=6)

# Accumulate precip
cumsum=np.cumsum(df["precip"])

# Extract the next 36 hours' data at 6-hourly resolution (06,12,18,24,06,12,18), and accumulate the precip over these intervals 
idx=np.logical_or(np.logical_or(np.logical_or(df["hour"]==06,df["hour"]==12),df["hour"]==18),df["hour"]==00)
df["cum_precip"]=np.cumsum(df["precip"])
df_sub=df.loc[idx]*1

# Difference cumulative precip from previous 6-hourly total 
sub_precip=np.zeros(np.sum(idx))
sub_precip[1:]=df_sub["cum_precip"].values[1:]-df_sub["cum_precip"].values[:-1]
sub_precip[0]=df_sub["cum_precip"].values[0]
df_sub["qpf"]=sub_precip[:]
df_sub["wdir"]=GF.calc_wdir(df_sub["u"].values[:],df_sub["v"].values[:])
#df_sub.to_csv(outdir+"KCC_forecast.csv",columns=["t","r","wdir","wind","qpf"])


# Create forecast string
string=[]
for ii in range(np.sum(idx)):
	string.append("%02d/%02d/%.0f/%.0f/%.1f/%.0f/%.0f\n" % (df_sub["day"][ii],df_sub["hour"][ii],\
	np.round(df_sub["t"][ii]),np.round(df_sub["r"][ii]),np.round(df_sub["qpf"][ii],decimals=1),\
	np.round(df_sub["wdir"][ii]),np.round(df_sub["wind"][ii])))

msg="%s%s%s%s%s%s%s" % (string[0],string[1],string[2],string[3],string[4],string[5],string[6])
     
# Send message!
send_mail(msg,to)


    












