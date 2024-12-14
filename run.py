import download
import process
import convert
import qgis_transform

# Importing the required modules

# Define parameters for the API request
years = ["2022"]
months = ["01"]
#months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
variables = ["ssrd"]

# download, process, and convert data to GeoTIFF for the specified variables and time periods
periods = download.batch_download(variables,years,months)
process.average_netcdfs_in_dir(variables, periods)
convert.netcdf_to_geotiff(variables, periods)

# Initialize QGIS and resample the raster
for period in periods:
    qgis_transform.init_qgis(variables, period)
    


# Running the dummy functions from each module
#download.dummy()
#process.dummy()
#convert.dummy()
#qgis_transform.dummy()