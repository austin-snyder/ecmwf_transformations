import xarray as xr
import rioxarray
import os
import pathlib


def netcdf_to_geotiff(variables, periods):
    """
    Convert NetCDF file to GeoTIFF format.

    Parameters:
        variables (list): List of variables to be converted from NetCDF to GeoTIFF.

    Returns:
        None
    """
    # Open NetCDF files and average them
    variable_list = '-'.join(map(str, variables))
    directory_path = pathlib.Path(f'./era5_data/{variable_list}')
    input_directory = pathlib.Path(f'{directory_path}/means/')
    output_directory = pathlib.Path(f'{directory_path}/means/geotiffs/')
    
    data_list = []
    for file in input_directory.iterdir():
        if file.name.endswith(".nc"):
            input_path = input_directory / file.name
            input_path_stem = str(input_path.stem)
            input_path_stem_period = input_path_stem.split("mean_")[1]

            if input_path_stem_period in periods:
                data = xr.open_dataset(str(input_path))

                # Shift the longitude values
                data.coords['longitude'] = (data.coords['longitude'] + 180) % 360 - 180
                data = data.sortby(data.longitude)

                # Select the variable to export
                variable = data["ssrd"]

                # Set spatial reference
                variable = variable.rio.write_crs("EPSG:4326")  # Replace with your CRS if known

                os.makedirs(output_directory, exist_ok=True)
                output_path = output_directory / f"{input_path_stem}.tif"
                # Check if output file exists
                if output_path.exists():
                    print(f"Data for the period {input_path_stem_period} has already been converted.")
                    continue

                # Export to GeoTIFF
                variable.rio.to_raster(output_path)
                print("GeoTIFF file created successfully!")