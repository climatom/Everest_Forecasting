#!/bin/bash

# This script does the downloading of GFS data. 
# Look out for **** for things that need edting if
# cdo was not built with grib compatibility (in which 
# case you'll need to use wgrib2)


# All aguments fed in by MAIN.py
outdir=$1
date=$2
init_hour=$3
nhrs=$4
freq=6 

# Define textfile with names | lat | lon | elevation
fin="${outdir}Locations.txt"

# Remove all _GFS_grb files (in target directory) before starting
find /${outdir} -type f -name '_GFS_*.grb' -delete

# Loop over all forecast hours
for ((ii=1; ii<=$nhrs; ii++)); do

	hr=$(printf "%03d" $ii)


	# Define surface url (for precip)
	URL="http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t${init_hour}z.pgrb2.0p25.f${hr}\
&lev_surface=on&var_PRATE=on&var_HGT=on&subregion=&leftlon=85&rightlon=89&toplat=30&bottomlat=26&dir=%2Fgfs.${date}"

	# Define pressure-level url (for temp and wind)
	URL2="http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t${init_hour}\
z.pgrb2.0p25.f${hr}&lev_500_mb=on&lev_550_mb=on&lev_600_mb=on&lev_650_mb=on&lev_700_mb=on&var_HGT=on&var_TMP=on&var_UGRD=on&var_VGRD=on&var_RH=on&subregion=&leftlon=85&rightlon=89&toplat=30&bottomlat=26&dir=%2Fgfs.${date}"

	# Download surface file
	curl "$URL" -o ${outdir}_GFS_surface${hr}.grb #> /dev/null 2>&1

	# Download pressure (temp, wind)
	curl "$URL2" -o ${outdir}_GFS_press${hr}.grb #> /dev/null 2>&1	


	# add a sleep to prevent a denial of service in case of missing file
	sleep 1
	
	echo "Downloaded forecast hour: ${ii}"
done

# Merge all the time steps - first removing any existing merged files...
if [ -f "${outdir}GFS_surface_merged.nc" ]; then
	rm "${outdir}GFS_surface_merged.nc"
fi

# Merge all the time steps - first removing any existing merged files...
if [ -f "${outdir}GFS_press_merged.nc" ]; then
	rm "${outdir}GFS_press_merged.nc"
fi

#---------------------------------------------------------------------#
# Merge surface 
cmd="cdo -s -f nc mergetime ${outdir}_GFS_surface*.grb ${outdir}GFS_surface_merged.nc"
${cmd} # execute merge command! 
# Merge 2m 
cmd="cdo -s -f nc mergetime ${outdir}_GFS_press*.grb ${outdir}GFS_press_merged.nc"
${cmd} # execute merge command! 
#---------------------------------------------------------------------#

# Remove any lingering files
find /${outdir} -type f -name '_GFS_*.grb' -delete

## Begin interpolation to KCC (27.8456 86.7489)


# Delete output file if it exists
if [ -f "${outdir}GFS_surface_int.nc" ]; then
	rm "${outdir}GFS_surface_int.nc"
fi
if [ -f "${outdir}GFS_press_int.nc" ]; then
	rm "${outdir}GFS_press_int.nc"
fi

# Perform a bilinear interpolation to the lon/lat 
cdo -s -O remapbil,lon=86.7489_lat=27.8456 ${outdir}GFS_surface_merged.nc ${outdir}GFS_surface_int.nc 
cdo -s -O remapbil,lon=86.7489_lat=27.8456 ${outdir}GFS_press_merged.nc ${outdir}GFS_press_int.nc 

# Interpolate height here - using  
/home/lunet/gytm3/anaconda2/bin/python ${outdir}Process_KCC.py 3787 ${outdir}



