helpString="Usage: $0 config.yml"
if [ -z "$1"]; then
    echo $helpString
    exit
fi
export CONFIGFILE=$1
python scripts/create_netcdf.py
ret=$?
if [ $ret -ne 0 ]; then
     exit
fi  
python scripts/upload_netcdf.py   