#!/bin/bash
read_password()
{
    echo -n "Geoserver Password:" 
    read -s geoserver_password
    echo ""
    export GEOSERVER_PASSWORD=$geoserver_password
}


list() {
    read_password
    python $path/scripts/list_projects.py $projects
}
create() {
    read_password
    if [ ! -z $projects ]; then
        dynamicProjects=1
    fi

    nInputFiles=$(ls -1 ./inputFiles/*.nc |  wc -l)
    if [ $nInputFiles -eq 0 ]; then
        echo "Error: inputFiles Directory is empty"
        exit 1
    fi
    files=./inputFiles/*.nc
    if [ -n $removeOutputFiles ]; then
        export REMOVEOUTPUTFILES=1
    else
        unset REMOVEOUTPUTFILES
    fi
    i=0
    for f in $files; do
        export INPUTFILE=$f
        if [ -z $dynamicProjects ]; then
            f=${f##*/}
            f="${f%.*}"
            export PROJECTNAME="$f"
        else
            export PROJECTNAME=${projects[0]}$((i+1))
        fi
        ((i++))
        python $path/scripts/prepare_netcdf.py
        ret=$?
        if [ $ret -ne 0 ]; then
            continue
        fi
        python $path/scripts/upload_netcdf.py
    done
}

delete() {
    if [ ! -z $projects ]; then
        read_password
        python $path/scripts/delete_projects.py ${projects[@]}
    else
        echo 'ERROR: Projects to be deleted must be specified with -p option'
        exit 1
    fi
}

#########################
# The command line help #
#########################
display_help() {
    echo "Program to Handle Geoserver Projects based on NetCDF Files; Used by netcdf-leaflet-frontend"
    echo "Usage: $0 [option...] {list|create|delete}" >&2
    echo
    echo "   -p, --projects [optional]              projectNames to be created/deleted"
    echo "   -c, --config [optional]                Config File to be used  (default: ./config.yml)"
    echo "   -r  --remove [optional] (create only)  Remove used OutputFiles"
    exit 1
}



################################
# Check if parameters options  #
# are given on the commandline #
################################
while :
do
    case "$1" in
        
      -p | --projects)
          if [ $# -ne 0 ]; then
            projects+=("$2")  
          fi
          shift 2
          ;;
      -h | --help)
          display_help 
          exit 0
          ;;
      -r | --remove)
          removeOutputFiles=1  
          shift 1
          ;;
      -c | --config)
        if [ $# -ne 0 ]; then
        config="$2"
        fi
        shift 2
        ;;

      --) # End of all options
          shift
          break
          ;;
      -*)
          echo "Error: Unknown option: $1" >&2
          exit 1 
          ;;
      *)  # No more options
          break
          ;;
    esac
done


# Check if running in container
if [ -d "/usr/src/backend" ]; then 
path="/usr/src/backend"
else
path="."
fi

# Check ConfigFile
if  [ -f "$config" ]; then
    export CONFIGFILE=$config
elif [ -f "./config.yml" ]; then
    export CONFIGFILE="./config.yml"
else 
    echo "Error: Could not load Configfile (default: ./config.yml)"
    echo ""
    display_help
    exit 1
fi


###################### 
# Check if parameter #
# is set too execute #
######################
case "$1" in
  list)
    list # calling function to list projects
    ;;
  create)
    create # calling function to create projects
    ;;
  delete)
    delete # calling function to delete projects
    ;;
  *)
    display_help
    exit 1
    ;;
esac


