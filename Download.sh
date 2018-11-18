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

# Define textfile with names | lat | lon | elevation
fin="${outdir}Locations.txt"

# Remove all GFS_grb/nc files (in target directory) before starting
find /${outdir} -type f -name '_GFS_*.nc' -delete
find /${outdir} -type f -name '_GFS_*.grb' -delete

# Loop over all forecast hours
for ((ii=1; ii<=$nhrs; ii++)); do

	hr=$(printf "%03d" $ii)

	# Define url
	URL="http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t${init_hour}\
z.pgrb2.0p25.f${hr}&lev_300_mb=on&lev_350_mb=on&lev_400_mb=on&lev_450_mb=on&lev_500_mb=on&\
lev_550_mb=on&lev_600_mb=on&lev_650_mb=on&lev_700_mb=on&lev_750_mb=on&lev_800_mb=on&lev_850_mb=on&lev_900_mb=on&\
var_UGRD=on&var_VGRD=on&var_TMP=on&var_HGT=on&subregion=&leftlon=85&rightlon=89&toplat=30&bottomlat=26&dir=%2Fgfs.${date}"

	# download file
	curl "$URL" -o ${outdir}_GFS_${hr}.grb #> /dev/null 2>&1

	# add a sleep to prevent a denial of service in case of missing file
	sleep 1

	# ****Uncomment below (between "------") if you need wgrib2 conversion

	#-----------------------------------------#
	#if [ -f "${outdir}_GFS_{$hr}.nc" ]; then
	#	rm "${outdir}_GFS_${hr}.nc"
	#fi
	#wgrib2 _GFS_${hr}.grb -netcdf _GFS_${hr}.nc > /dev/null 2>&1
	#-----------------------------------------#


	
	echo "Downloaded forecast hour: ${ii}"
done

# Merge all the time steps - first removing any existing merged files...
if [ -f "${outdir}Forecast_GFS2D.nc" ]; then
	rm "${outdir}Forecast_GFS2D.nc"
fi

# ****Replace command [1] with [2] if you used wgrib2 conversion
#---------------------------------------------------------------------#
# Command [1]
cmd="cdo -s -f nc mergetime ${outdir}_GFS_*.grb ${outdir}Forecast_GFS2D.nc"
# Command [2]
# cmd="cdo -s mergetime ${outdir}_GFS_*.nc ${outdir}Forecast_GFS2D.nc"
#---------------------------------------------------------------------#
${cmd} # execute merge command! 

# Remove any lingering files
find /${outdir} -type f -name '_GFS_*.nc' -delete
find /${outdir} -type f -name '_GFS_*.grb' -delete

## Begin processing 
echo "Processing forecasts..."
# Iterate over lines in the location file
while read f; do

	# Delete output file if it exists
	if [ -f "${outdir}Forecast_GFS1D.nc" ]; then
	rm "${outdir}Forecast_GFS1D.nc"
	fi

	# Extract the name, lat, lon, elevation
	arr=(${f}) # Format: 0=name; 1=lat; 2=lon; 3=ht

  	# Perform a bilinear interpolation to the lon/lat 
	cdo -s -O remapbil,lon=${arr[2]}_lat=${arr[1]} "${outdir}Forecast_GFS2D.nc"  "${outdir}Forecast_GFS1D.nc" 

	# Get python to do the final interpolation and plot...	
	/home/lunet/gytm3/anaconda2/bin/python ${outdir}Process.py ${arr[0]} ${arr[3]} ${outdir} 

done <$fin


