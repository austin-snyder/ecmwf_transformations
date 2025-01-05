# Standard libraries
import os
import pathlib

# Third-party libraries
import xarray as xr


def calculate_anomaly(variables, periods, months):
    """
    Calculate the percentage difference from the long-term norm for a given month.

    Parameters:
        variables (list): List of variables to calculate the percentage difference for.
        periods (list): List of periods to process.
        months (list): List of months to process.

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

        anomaly_path = anomaly_directory / f"anomaly_{period}.nc"
        monthly_path = monthly_directory / f"mean_{period}.nc"
        longterm_path = longterm_directory / f"lt_average_{month}.nc"

        if month == "":
            longterm_path = os.path.join(longterm_directory, "lt_average.nc")
            output_file_path = os.path.join(anomaly_directory, f"anomaly_year_{period}.nc")
        else:
            longterm_path = os.path.join(longterm_directory, f"lt_average_{month}.nc")
            output_file_path = os.path.join(anomaly_directory, f"anomaly_month{month}_{period}.nc")

        # Open the NetCDF files using xarray and calculate anomaly
        longterm_avg = xr.open_dataset(longterm_path)
        monthly_mean = xr.open_dataset(monthly_path)
        longterm_avg_data = longterm_avg['ssrd']
        monthly_mean_data = monthly_mean['ssrd'] 
        anomaly = ((monthly_mean_data - longterm_avg_data) / longterm_avg_data) * 100 # calculate the percentage difference

        # Create the output NetCDF file
        anomaly.to_netcdf(output_file_path)
        print(f"Percentage difference saved to {output_file_path}")