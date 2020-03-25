export CONFIGFILE=$1
python scripts/create_netcdf.py
ret=$?
if [ $ret -ne 0 ]; then
     exit
fi  
python scripts/upload_netcdf.py   