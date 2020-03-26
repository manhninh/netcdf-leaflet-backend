helpString="Usage: $0 config.yml"
if [ -z "$1" ]; then
    echo $helpString
    exit
fi
export CONFIGFILE=$1

if [ -d "usr/src/backend" ]; then #Check if running in container
path="usr/src/backend"
else
path="."
fi

python $path/scripts/create_netcdf.py
ret=$?
if [ $ret -ne 0 ]; then
     exit
fi  
python $path/scripts/upload_netcdf.py   