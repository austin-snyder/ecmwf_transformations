# Standard libraries
import os
import pathlib

# Third-party libraries
import xarray as xr

def create_longterm_average(variables, months):
    """
    Calculate the monthly mean for specified variables in NetCDF files.

    Parameters:
        variables (list): List of variables to average.
        months (list): List of months to process.

    Returns:
        None
    """
    # Directory path
    variable_list = '-'.join(map(str, variables))
    input_directory = pathlib.Path(f'./era5_data/{variable_list}/downloads/')
    output_directory = pathlib.Path(f'./era5_data/{variable_list}/long-term_averages/')
    output_filename_prefix = "lt_average"
    # months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

    # Directory containing the NetCDF files
    output_file = os.path.join(output_directory, output_filename_prefix + ".nc")

    # Loop through all files in the directory
    print("Calculating the long-term average for each month...")
    # multi_average("", input_directory, output_directory, output_filename_prefix)
    for month in months:
        print(f"\tCalculating the long-term average for the month {month}...")
        multi_average(month, input_directory, output_directory, output_filename_prefix)


def multi_average(month, input_directory, output_directory, output_filename_prefix):
    """
    Calculate the monthly mean for specified variables in NetCDF files.

    Parameters:
        month (str): Month to process.
        input_directory (str): Directory containing the NetCDF files.
        output_directory (str): Directory to save the output NetCDF file.
        output_filename_prefix (str): Prefix for the output NetCDF file.

    Returns:
        None
    """
    if month == "":
        file_pattern = os.path.join(input_directory, "*_to_*")
        output_filepath = os.path.join(output_directory, f"{output_filename_prefix}")
    else:
        file_pattern = os.path.join(input_directory, f"download_????{month}??_to_*")
        output_filepath = os.path.join(output_directory, f"{output_filename_prefix}_{month}")

    # Open multiple NetCDF files and combine along the time dimension
    dataset = xr.open_mfdataset(file_pattern + ".nc", combine="by_coords")

    # Calculate the monthly mean along the time dimension
    monthly_mean = dataset.mean(dim="valid_time", skipna=True)

    # Save the resulting dataset to a new NetCDF file
    if pathlib.Path(output_filepath + ".nc").exists() and pathlib.Path(output_filepath + ".tif").exists():
        print(f"\t\tData for the month {month} has already been averaged in the long-term.")
        return
    else:
        os.makedirs(output_directory, exist_ok=True)
        monthly_mean.to_netcdf(output_filepath + ".nc")
        print(f"\t\tData for the month {month} has been averaged in the long-term.")

    monthly_mean.coords['longitude'] = (monthly_mean.coords['longitude'] + 180) % 360 - 180
    monthly_mean = monthly_mean.sortby(monthly_mean.longitude)
    # Select the variable to export
    variable = monthly_mean["ssrd"]

    # Set spatial reference
    variable = variable.rio.write_crs("EPSG:4326")  # Replace with your CRS if known

    os.makedirs(output_directory, exist_ok=True)
    # output_geotiff_path = output_directory / f"{output_filename_prefix}.tif"

    # Export to GeoTIFF
    variable.rio.to_raster(output_filepath + ".tif")
    print(f"\t\tData for the month {month} has been converted to GeoTIFF format!")