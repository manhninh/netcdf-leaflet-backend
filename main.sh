#!/bin/bash
usage="$(basename "$0") [-h] [-c -i (-p)] [-d] -- Program to upload a NetCDF File to Geoserver and creating static JavascriptFiles used by netcdf-leaflet-frontend

where:
    -h  show this help text
    -i  the InputFile(s) to be read (Can be a folder or a Single File)
    -p  [optional] the ProjectName to be used (default: FileName)
    -c  the ConfigFile to be used
    -d  [optional] the ProjectName to be deleted"

while getopts 'hdp::i::c::' option; do
  case "$option" in
    h) echo "$usage"
       exit
       ;;
    i) input=$OPTARG
       ;;
    p) projectName=$OPTARG
       ;;
    c) configFile=$OPTARG
       ;;
    d) delete="True"
       ;;
    :) printf "missing argument for -%s\n" "$OPTARG" >&2
       echo "$usage" >&2
       exit 1
       ;;
   \?) printf "illegal option: -%s\n" "$OPTARG" >&2
       echo "$usage" >&2
       exit 1
       ;;
  esac
done

if [ -n "$delete" ]; then
    echo "test2"
    echo "Delete not implemented"
    exit
elif [ -f "$input" ] && [ -f "$configFile" ]; then
    if [ -n "$projectName" ]; then
        export PROJECTNAME=$projectName
    else
        echo "Without -p Parameter Not implemented"
        exit 1
        export PROJECTNAME=$input
    fi
    export INPUTFILE=$input
    export CONFIGFILE=$configFile
else
  echo "test22"
    echo "$usage" >&2
    exit 1
fi

if [ -d "/usr/src/backend" ]; then #Check if running in container
path="/usr/src/backend"
else
path="."
fi

python $path/scripts/prepare_netcdf.py
ret=$?
if [ $ret -ne 0 ]; then
     exit
fi  
python $path/scripts/upload_netcdf.py   
