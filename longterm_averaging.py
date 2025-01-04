import xarray as xr
import pathlib
import os

def create_longterm_average(variables):
    """
    Calculate the monthly mean for specified variables in NetCDF files.

    Parameters:
        variables (list): List of variables to average.

    Returns:
        None
    """

    # Directory path
    variable_list = '-'.join(map(str, variables)) 
    input_directory = pathlib.Path(f'./era5_data/{variable_list}/downloads/')
    output_directory = pathlib.Path(f'./era5_data/{variable_list}/long-term_averages/')
    output_filename_prefix = "lt_average"

    # Directory containing the NetCDF files
    output_file = os.path.join(output_directory,output_filename_prefix + ".nc")

    # Open multiple NetCDF files and combine along the time dimension
    file_pattern = os.path.join(input_directory, "*.nc")  # Adjust the pattern as needed
    dataset = xr.open_mfdataset(file_pattern, combine="by_coords")

    # Calculate the long-term average along the time dimension
    long_term_avg = dataset.mean(dim="valid_time", skipna=True)

    # Save the resulting dataset to a new NetCDF file
    long_term_avg.to_netcdf(output_file)

    print(f"Long-term average saved to {output_file}")

    long_term_avg.coords['longitude'] = (long_term_avg.coords['longitude'] + 180) % 360 - 180
    # Select the variable to export
    variable = long_term_avg["ssrd"]

    # Set spatial reference
    variable = variable.rio.write_crs("EPSG:4326")  # Replace with your CRS if known

    os.makedirs(output_directory, exist_ok=True)
    output_geotiff_path = output_directory / f"{output_filename_prefix}.tif"

    # Export to GeoTIFF
    variable.rio.to_raster(output_geotiff_path)
    print("GeoTIFF file created successfully!")