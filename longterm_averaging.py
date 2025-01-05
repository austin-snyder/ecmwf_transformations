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
    # Set the IO directories and filenames
    variable_list = '-'.join(map(str, variables)) # join the variables into a string
    input_directory = pathlib.Path(f'./era5_data/{variable_list}/downloads/') # define the input directory
    output_directory = pathlib.Path(f'./era5_data/{variable_list}/long-term_averages/') # define the output directory
    output_filename_prefix = "lt_average" # define the output filename prefix

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

    # Define the file pattern and output file path based on the month
    if month == "":
        file_pattern = os.path.join(input_directory, "*_to_*")
        output_filepath = os.path.join(output_directory, f"{output_filename_prefix}")
    else:
        file_pattern = os.path.join(input_directory, f"download_????{month}??_to_*")
        output_filepath = os.path.join(output_directory, f"{output_filename_prefix}_{month}")

    dataset = xr.open_mfdataset(file_pattern + ".nc", combine="by_coords") # open all NetCDF files to be averaged
    monthly_mean = dataset.mean(dim="valid_time", skipna=True) # calculate monthly mean along the time dimension

    # Save the resulting dataset to a new NetCDF file
    if pathlib.Path(output_filepath + ".nc").exists() and pathlib.Path(output_filepath + ".tif").exists():
        print(f"\t\tData for the month {month} has already been averaged in the long-term.")
        return
    else:
        os.makedirs(output_directory, exist_ok=True)
        monthly_mean.to_netcdf(output_filepath + ".nc")
        print(f"\t\tData for the month {month} has been averaged in the long-term.")

    # Conduct necessary conversions to NetCDF file to export to GeoTIFF
    monthly_mean.coords['longitude'] = (monthly_mean.coords['longitude'] + 180) % 360 - 180 # shift the longitude values
    monthly_mean = monthly_mean.sortby(monthly_mean.longitude) # sort the longitude values
    variable = monthly_mean["ssrd"] # select variable to export to GeoTIFF
    variable = variable.rio.write_crs("EPSG:4326")  # set spacial reference to WGS84

    # Export to GeoTIFF
    os.makedirs(output_directory, exist_ok=True)
    variable.rio.to_raster(output_filepath + ".tif")
    print(f"\t\tData for the month {month} has been converted to GeoTIFF format!")