import netCDF4 as nc
import numpy as np
import os

def calculate_percentage_difference(long_term_avg_file, monthly_mean_file, output_file):
    """
    Calculate the percentage difference from the long-term norm for a given month.

    Parameters:
        long_term_avg_file (str): Path to the long-term average NetCDF file.
        monthly_mean_file (str): Path to the monthly mean NetCDF file.
        output_file (str): Path to save the output NetCDF file with percentage differences.

    Returns:
        None
    """
    # Open the NetCDF files
    with nc.Dataset(long_term_avg_file, 'r') as long_term_avg, nc.Dataset(monthly_mean_file, 'r') as monthly_mean:
        # Read the data variables
        long_term_avg_data = long_term_avg.variables['data'][:]
        monthly_mean_data = monthly_mean.variables['data'][:]

        # Calculate the percentage difference
        percentage_difference = ((monthly_mean_data - long_term_avg_data) / long_term_avg_data) * 100

        # Create the output NetCDF file
        with nc.Dataset(output_file, 'w', format='NETCDF4') as output:
            # Copy dimensions from the long-term average file
            for name, dimension in long_term_avg.dimensions.items():
                output.createDimension(name, len(dimension) if not dimension.isunlimited() else None)

            # Copy variables from the long-term average file
            for name, variable in long_term_avg.variables.items():
                out_var = output.createVariable(name, variable.datatype, variable.dimensions)
                out_var.setncatts({k: variable.getncattr(k) for k in variable.ncattrs()})
                if name == 'data':
                    out_var[:] = percentage_difference
                else:
                    out_var[:] = variable[:]

            # Add a new attribute to indicate the data represents percentage differences
            output.setncattr('description', 'Percentage difference from long-term average')

if __name__ == "__main__":
    long_term_avg_file = 'path/to/long_term_avg.nc'
    monthly_mean_file = 'path/to/monthly_mean.nc'
    output_file = 'path/to/output_percentage_difference.nc'

    calculate_percentage_difference(long_term_avg_file, monthly_mean_file, output_file)
    print(f"Percentage difference calculated and saved to {output_file}")
