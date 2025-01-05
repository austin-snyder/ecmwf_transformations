import xarray as xr
import pathlib
import os

def calculate_anomaly(variables, periods, months):
    """
    Calculate the percentage difference from the long-term norm for a given month.

    Parameters:
        variables (list): List of variables to calculate the percentage difference for.
        output_file (str): Path to the output NetCDF file.

    Returns:
        None
    """

    # Directory path
    variable_list = '-'.join(map(str, variables))
    long_term_directory = pathlib.Path(f'./era5_data/{variable_list}/long-term_averages/')
    monthly_directory = pathlib.Path(f'./era5_data/{variable_list}/monthly_means/')
    output_directory = pathlib.Path(f'./era5_data/{variable_list}/monthly_anomalies/')
    
    multi_anomaly(periods, long_term_directory, monthly_directory, output_directory)
         
    

def multi_anomaly(periods, longterm_directory, monthly_directory, anomaly_directory):
    for period in periods:
        month = period[4:6]

        anomaly_path_stem = f"anomaly_{period}"
        anomaly_path = anomaly_directory / f"{anomaly_path_stem}.nc"

        monthly_path_stem = f"mean_{period}"
        monthly_path = monthly_directory / f"{monthly_path_stem}.nc"

        longterm_path_stem = f"lt_average_{month}"
        longterm_path = longterm_directory / f"{longterm_path_stem}.nc"

        if (month == ""):
            longterm_path = os.path.join(longterm_directory, "lt_average.nc")
            output_file_path = os.path.join(anomaly_directory, f"anomaly_year_{period}.nc")
        else:
            longterm_path = os.path.join(longterm_directory, f"lt_average_{month}.nc")
            output_file_path = os.path.join(anomaly_directory, f"anomaly_month{month}_{period}.nc")


        # Open the NetCDF files using xarray
        longterm_avg = xr.open_dataset(longterm_path)
        monthly_mean = xr.open_dataset(monthly_path)

        # Read the data variables
        longterm_avg_data = longterm_avg['ssrd']
        monthly_mean_data = monthly_mean['ssrd']

        # Calculate the percentage difference
        anomaly = ((monthly_mean_data - longterm_avg_data) / longterm_avg_data) * 100

        # Create the output NetCDF file
        anomaly.to_netcdf(output_file_path)

        # Add a new attribute to indicate the data represents percentage differences
        #with xr.open_dataset(output_file, mode='a') as output:
        #    output.attrs['description'] = 'Percentage difference from long-term average'

        print(f"Percentage difference saved to {output_file_path}")