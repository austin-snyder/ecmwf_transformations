import xarray as xr
import re
import pathlib
import os

def average_netcdfs(variables, periods):
    """
    Calculate the monthly mean for specified variables in NetCDF files.

    Parameters:
        variables (list): List of variables to average.

    Returns:
        None
    """

    # Directory path
    variable_list = '-'.join(map(str, variables))
    directory_path = pathlib.Path(f'./era5_data/{variable_list}/')
    input_directory = pathlib.Path(f'./era5_data/{variable_list}/downloads/')
    output_directory = pathlib.Path(f'./era5_data/{variable_list}/monthly_means/')

    # Loop through all files in the directory
    for file in input_directory.iterdir():
        if not file.is_file():  # Check if it is a file
            continue
        
        in_path = input_directory / file.name
        in_path_stem = str(in_path.stem)
        in_path_stem_period = in_path_stem.split("download_")[1]

        if in_path_stem_period in periods:
            # Regex pattern to match "########_to_########"
            pattern = r"\d{8}_to_\d{8}"
            match = re.search(pattern, file.name)
            period = match.group()

            # Deriving output filename from input filename
            out_filename = f"mean_{period}.nc"
            output_path = output_directory / out_filename
            os.makedirs(output_directory, exist_ok=True)

            # Check if output file exists
            if output_path.exists():
                print(f"Data for the period {period} has already been processed.")
                continue

            # Open the downloaded NetCDF file
            data = xr.open_dataset(in_path)
            monthly_mean = data[variables].mean(dim="valid_time")
            monthly_mean.to_netcdf(output_path)
            print(f"Data for the period {period} has been averaged.")