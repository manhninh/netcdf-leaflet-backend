# netcdf-leaflet-backend
Backend for Displaying NetCDF Data in Leaflet

## Current Features:
- displaying Heightlevels dynamically
- custom styling:
    - Define Default ColorPalette
    - Define Custom ColorPalette for each Climate Element
    - Define Custom Min Max Value used for Styling (lower contrast,comparison with other projects

## Working Steps
### Prepare Custom NetCDF
- creation of custom NetCDF from Input NetCDF File
    - read defined Vars from Config
    - add grid_mapping
    - write to new .nc File

### Frontend
- creation of Javascript Files from Templates

### Geoserver
- creation of custom SLD Styles with custom Min Max Values and Colors
    -Default: https://colorbrewer2.org/#type=diverging&scheme=RdBu&n=5
- workspace Creation
- uploading NetCDF Data
- layer Creation
    - style Creation and Assigning

## Used Technology
- Geoserver for Serving Tiles
- Jinja2 for Templatecreation