# Standard libraries
import os
import pathlib

# Third-party libraries
import xarray as xr
import rioxarray


def netcdf_to_geotiff(variables, periods, input_dir):
    """
    Convert NetCDF file to GeoTIFF format.

    Parameters:
        variables (list): List of variables to be converted from NetCDF to GeoTIFF.
        periods (list): List of periods to process.
        input_dir (str): Input directory.

    Returns:
        None
    """
    # Open NetCDF files and average them
    variable_list = '-'.join(map(str, variables))
    directory_path = pathlib.Path(f'./era5_data/{variable_list}')
    input_directory = pathlib.Path(f'{directory_path}/{input_dir}/')
    output_directory = pathlib.Path(f'{directory_path}/{input_dir}/geotiffs/')

    for period in periods:
        month = period[4:6]
        # Month Check
        if month == "" or input_dir == "monthly_means":
            input_path_suffix = f"{period}"
        else:
            input_path_suffix = f"month{month}_{period}"

        # Anomaly Check
        if input_dir == "monthly_anomalies":
            input_path_name = f"anomaly_{input_path_suffix}"
        elif input_dir == "monthly_means":
            input_path_name = f"mean_{input_path_suffix}"

        input_path = input_directory / input_path_name

        data = xr.open_dataset(str(input_path) + ".nc")

        # Shift the longitude values
        data.coords['longitude'] = (data.coords['longitude'] + 180) % 360 - 180
        data = data.sortby(data.longitude)

        # Select the variable to export
        variable = data["ssrd"]

        # Set spatial reference
        variable = variable.rio.write_crs("EPSG:4326")  # Replace with your CRS if known

        os.makedirs(output_directory, exist_ok=True)
        output_path = output_directory / f"{input_path_name}.tif"
        # Check if output file exists
        if output_path.exists():
            print(f"Data for the period {period} has already been converted.")
            continue

        # Export to GeoTIFF
        variable.rio.to_raster(output_path)
        print("GeoTIFF file created successfully!")