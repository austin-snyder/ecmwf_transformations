# Local Scripts
import download
import process
import convert
import qgis_transform
import longterm_averaging
import anomaly_calc

# Define parameters for the API request
years = ["2016"]
#months = ["01"]
months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
variables = ["ssrd"]

# download, process, and convert data to GeoTIFF for the specified variables and time periods
periods = download.batch_download(variables,years,months)

# monthly averaging
process.average_netcdfs(variables, periods)
convert.netcdf_to_geotiff(variables, periods, "monthly_means")
qgis_transform.init_qgis(variables, periods, "monthly_means")

# longterm averaging
# longterm_averaging.create_longterm_average(variables, months)
# anomaly_calc.calculate_anomaly(variables, periods, months)
# convert.netcdf_to_geotiff(variables, periods, "monthly_anomalies")
# qgis_transform.init_qgis(variables, periods, "monthly_anomalies")

