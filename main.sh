#!/bin/bash
read_password()
{
    if [ -z $GEOSERVER_PASSWORD ]; then
        read -s -p "Geoserver Password: " geoserver_password
        echo
        export GEOSERVER_PASSWORD=$geoserver_password
    fi
}

list() {
    read_password
    python $path/scripts/list_projects.py
}
create() {
    nInputFiles=$(ls -1q ./inputFiles/*.nc 2> /dev/null |  wc -l )
    if [ $nInputFiles -eq 0 ]; then
        echo "Error: inputFiles Directory does not contain .nc Files"
        exit 1
    fi

    if [ ! -z $projects ]; then
        dynamicProjects=1
    fi
    read_password
    # Read InputFiles
    files=./inputFiles/*.nc
    i=0
    for f in $files; do
        export INPUTFILE=$f
        if [ -z $dynamicProjects ]; then
            f=${f##*/}
            f="${f%.*}"
            export PROJECTNAME="$f"
        else
            if [ $nInputFiles == 1 ]; then 
                export  PROJECTNAME=${projects[0]}
            else
                export PROJECTNAME=${projects[0]}$((i+1))
            fi
        fi
        valid="A-Za-z0-9._-"
        if [[ ! $PROJECTNAME =~ ^[$valid]+$ ]]; then
            echo "Error: Invalid ProjectName $PROJECTNAME , $f will be skipped"
            continue
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
        for project in  ${projects[@]}; do
            export PROJECTNAME=$project
            python $path/scripts/delete_project.py $project
        done
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


