from osgeo import gdal, osr

layer = iface.activeLayer()

provider = layer.dataProvider()

path = provider.dataSourceUri()

fmttypes = {'Byte':'B', 'UInt16':'H', 'Int16':'h', 'UInt32':'I', 'Int32':'i', 'Float32':'f', 'Float64':'d'}

dataset = gdal.Open(path)

#Get projection
prj = dataset.GetProjection()

band = dataset.GetRasterBand(1)

geotransform = dataset.GetGeoTransform()

# Create gtif file with rows and columns from parent raster 
driver = gdal.GetDriverByName("GTiff")

columns, rows = (band.XSize, band.YSize)

BandType = gdal.GetDataTypeName(band.DataType)

output_file = "/home/zeito/pyqgis_data/test_copy_raster.tif"

data = band.ReadAsArray(0, 0, columns, rows)

dst_ds = driver.Create(output_file, 
                       columns, 
                       rows, 
                       1, 
                       band.DataType)

new_geotransform = list(geotransform)

new_geotransform[2] = 30 #x pixel rotation
new_geotransform[4] = 30 #y pixel rotation

dst_ds.GetRasterBand(1).WriteArray( data )

#setting No Data Values
dst_ds.GetRasterBand(1).SetNoDataValue(0)

#setting extension of output raster
# top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution
dst_ds.SetGeoTransform(new_geotransform)

# setting spatial reference of output raster 
srs = osr.SpatialReference(wkt = prj)
dst_ds.SetProjection( srs.ExportToWkt() )

#Close output raster dataset 
dst_ds = None

#Close main raster dataset
dataset = None 