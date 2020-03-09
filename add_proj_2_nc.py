from netCDF4 import Dataset
import argparse
import os.path
from urllib.request import urlopen
import re


def strip_chars(edit_str, bad_chars='[(){}<>,"_]=\nns'):
    result = ''.join([s for s in edit_str if s not in bad_chars])

    return result
def gather_utm_meta(epsg_str,epsg):
    map_meta = {}
    map_meta['grid_mapping_name'] = "transverse_mercator"
    map_meta['longitude_of_central_meridian'] = 9.0
    map_meta['latitude_of_projection_origin'] = 50.0 
    map_meta['scale_factor_at_central_meridian'] = 0.9330127018922193 
    map_meta['false_easting'] = 0.0
    map_meta['false_northing'] = 0.0
    map_meta['semi_major_axis'] =  6378.137
    map_meta['semi_minor_axis'] =  6356.752
    map_meta['inverse_flattening'] =   298.257
    map_meta['_CoordinateTransformType'] = "Projection"
    map_meta['_CoordinateAxisTypes'] = "GeoX GeoY"
    map_meta['spatial_ref'] = 'FITTED_CS["BPAF", PARAM_MT["Affine", PARAMETER["num_row", 3], PARAMETER["num_col", 3], PARAMETER["elt_0_0", -0.5], PARAMETER["elt_0_1", -0.8660254037844386], PARAMETER["elt_0_2", 1487816.0], PARAMETER["elt_1_0", 0.8660254037844386], PARAMETER["elt_1_1", -0.5], PARAMETER["elt_1_2", 6886579.0]], PROJCS["WGS84 / Google Mercator", GEOGCS["WGS 84", DATUM["World Geodetic System 1984", SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]], AUTHORITY["EPSG","6326"]], PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]], UNIT["degree", 0.017453292519943295], AXIS["Longitude", EAST], AXIS["Latitude", NORTH], AUTHORITY["EPSG","4326"]], PROJECTION["Mercator_1SP"], PARAMETER["semi_minor", 6378137.0], PARAMETER["latitude_of_origin", 0.0], PARAMETER["central_meridian", 0.0], PARAMETER["scale_factor", 1.0], PARAMETER["false_easting", 0.0], PARAMETER["false_northing", 0.0], UNIT["m", 1.0], AXIS["x", EAST], AXIS["y", NORTH], AUTHORITY["EPSG","900913"]], AUTHORITY["EPSG","8011113"]]'
    return map_meta
def gather_utm_meta2(epsg_str,epsg):
    """
    Use if the EPSG data is associated to UTM
    Gathers the data and returns a dictionary of data and attributes that need
    to be added to the netcdf based on
    https://www.unidata.ucar.edu/software/thredds/current/netcdf-java/reference/StandardCoordinateTransforms.html

    """
    meta = epsg_str.lower()

    map_meta = {
                    "grid_mapping_name": "universal_transverse_mercator",
                    "utm_zone_number": None,
                    "semi_major_axis": None,
                    "inverse_flattening": None,
                    'spatial_ref': epsg_str,
                    "_CoordinateTransformType": "projection",
                    "_CoordinateAxisTypes": "GeoX GeoY"}

    # Assign the zone number
    zone_str = meta.split('zone')[1]
    map_meta['utm_zone_number'] = float((strip_chars(zone_str.split(',')[0])).strip()[-2:])

    # Assign the semi_major_axis
    axis_string = meta.split('spheroid')[1]
    map_meta['semi_major_axis'] = float(axis_string.split(',')[1])

    # Assing the flattening
    map_meta["inverse_flattening"] = float(strip_chars(axis_string.split(',')[2]))

    return map_meta


def copy_nc(infile, outfile, exclude=None):
    """
    Copies a netcdf from one to another exactly.

    Args:
        infile: filename you want to copy
        outfile: output filename
        toexclude: variables to exclude

    Returns the output netcdf dataset object for modifying
    """
    if type(exclude) != list:
        exclude = [exclude]

    dst = Dataset(outfile, "w")

    with Dataset(infile) as src:

        # copy global attributes all at once via dictionary
        dst.setncatts(src.__dict__)

        # copy dimensions
        for name, dimension in src.dimensions.items():
            dst.createDimension(
                name, (len(dimension) if not dimension.isunlimited() else None))

        # copy all file data except for the excluded
        for name, variable in src.variables.items():
            if name not in exclude:
                dst.createVariable(name, variable.datatype, variable.dimensions)
                dst[name][:] = src[name][:]

                # copy variable attributes all at once via dictionary
                dst[name].setncatts(src[name].__dict__)
    return dst


def add_proj(nc_obj,epsg):
    """
        Adds the appropriate attributes to the netcdf for managing projection info

        Args:
        nc_obj: netCDF4 dataset object needing the projection information
        epsg:   projection information to be added
        Returns:
        nc_obj: the netcdf object modified
    """
    # function to generate .prj file information using spatialreference.org
    # access projection information
    try:
        if epsg=='3857':
            wkt =urlopen("https://spatialreference.org/ref/sr-org/epsg3857-wgs84-web-mercator-auxiliary-sphere/prettywkt/".format(epsg))
            print(wkt)
        else:
            wkt = urlopen("http://spatialreference.org/ref/epsg/{0}/prettywkt/".format(epsg))
    except:
        wkt = urlopen("http://spatialreference.org/ref/sr-org/{0}/prettywkt/".format(epsg))

    # remove spaces between charachters
    remove_spaces = ((wkt.read()).decode('utf-8')).replace(" ","")
    # Add in the variable for holding coordinate system info
    map_meta = parse_wkt(remove_spaces,epsg)

    nc_obj.createVariable("projection","S1")
    nc_obj["projection"].setncatts(map_meta)

    for name,var in nc_obj.variables.items():

        # Assume all 2D+ vars are the same projection
        if 'x' in var.dimensions and 'y' in var.dimensions:
            #print("Adding Coordinate System info to {0}".format(name))
            nc_obj[name].setncatts({"grid_mapping":"projection"})

        elif name.lower() in ['x','y']:
            # Set a standard name, which is required for recognizing projections
            nc_obj[name].setncatts({"standard_name":"projection_{}_coordinate"
            "".format(name.lower())})
            # Set the units
            nc_obj[name].setncatts({"units":"meters"
            "".format(name.lower())})


    return nc_obj


def parse_wkt(epsg_string,epsg):
    """
    """
    map_meta = {}
    wkt_data = (epsg_string.lower()).split(',')

    if 'utm' in epsg_string.lower():
        map_meta = gather_utm_meta(epsg_string,epsg)
    print(" Meta information to be added...\n")
    for k,v in map_meta.items():
        print(k,repr(v))
    return map_meta


def main():
    p = argparse.ArgumentParser(description= "Add projection information to a"
                                             " netcdf based on filename and "
                                             " epsg code. Makes it readable for"
                                             " geoserver")

    p.add_argument('-f','--netcdf', dest='netcdf',
                        required=True,
                        help="Path to a netcdf you want to add projection "
                        "information to")

    p.add_argument('-o','--output', dest='output',
                        required=False,
                        default='output.nc',
                        help="Path to output your netcdf containing projection info"
                        "")

    p.add_argument('-e','--epsg', dest='epsg',
                        required=True,
                        type=str,
                        help="EPSG value representing the projection information to"
                        "add to the netcdf")

    args = p.parse_args()


    infile = os.path.abspath(args.netcdf)
    outfile = os.path.abspath(args.output)
    outds = copy_nc(infile, outfile)
    outds = add_proj(outds,args.epsg)
    outds.sync()
    outds.close()

if __name__ =='__main__':
    main()
