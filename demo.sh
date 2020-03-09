python create_netcdf.py   
python add_proj_2_nc.py -f outputFiles/test.nc -o outputFiles/temp.nc -e '25832'
mv outputFiles/temp.nc outputFiles/test.nc 
python upload_netcdf.py   