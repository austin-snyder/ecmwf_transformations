# Standard libraries
import os
import pathlib

# Third-party libraries
from osgeo import gdal

# QGIS-specific libraries
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry, QgsNativeAlgorithms
from qgis.core import (
    QgsApplication,
    QgsRasterLayer,
    QgsRasterFileWriter,
    QgsRasterPipe,
    QgsRasterDataProvider,
    QgsRasterBandStats,
    QgsProcessingFeedback
)


def init_qgis(variables, period):
    """
    Initialize the QGIS application.

    Parameters:
        variables (list): List of variables.
        in_filename (str): Input filename.

    Returns:
        None
    """
    print("Initializing QGIS...")
    qgs = QgsApplication([], False)
    qgs.initQgis()

    # Load the raster
    variable_list = '-'.join(map(str, variables))
    directory_path = pathlib.Path(f'./era5_data/{variable_list}')
    input_directory = pathlib.Path(f'{directory_path}/means/geotiffs/')
    #output_directory = pathlib.Path(f'{directory_path}/means/geotiffs/')

    null_tiff = set_null_in_raster(input_directory, f"mean_{period}.tif")
    res_tiff = resample_raster(input_directory, null_tiff, 0.018)


def set_null_in_raster(in_dir, in_filename):
    """
    Set missing values in a raster to NULL.

    Parameters:
        in_dir (str): The input directory containing the raster file.
        in_filename (str): The input filename of the raster file.

    Returns:
        str: Path to the new raster file with NULL values set.
    """
    print("Setting missing values to NULL...")

    print("\nLoading raster...")
    input_tiff = os.path.join(in_dir, f"{in_filename}.tif")
    null_tiff = os.path.join(in_dir, f"{in_filename}_NULL.tif")

    # Open the raster file
    dataset = gdal.Open(input_tiff, gdal.GA_Update)  # Open in update mode

    if dataset is None:
        print("Failed to open the raster file.")
        exit()

    # Get the single raster band
    band = dataset.GetRasterBand(1)  # Band index is 1 for the first (and only) band

    # Set the NoData value
    band.SetNoDataValue(-9999)
    print("NoData value set to -9999 for the single band.")

    # Flush changes and close the dataset
    dataset.FlushCache()
    dataset = None

    # Save the raster to a new file to ensure changes are saved
    gdal.Translate(null_tiff, input_tiff)

    return null_tiff


def resample_raster(in_dir, in_filename, resolution):
    """
    Resample a raster to a higher resolution.

    Parameters:
        in_dir (str): The input directory containing the raster file.
        in_filename (str): The input filename of the raster file.
        resolution (float): The target resolution for resampling.

    Returns:
        None
    """
    print("Resampling raster to higher resolution...")

    # Register the native algorithms in the QGIS Processing framework
    print("\nRegistering the native algorithms in the QGIS Processing framework...")
    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    for alg in QgsApplication.processingRegistry().algorithms():
        print(alg.id())

    # Set input and output paths
    print("\nSetting up resampling inputs...")
    res_tiff = os.path.join(in_dir, f"{in_filename}_NULL_res.tif")

    # Open the input dataset
    input_raster = gdal.Open(in_filename)

    # Define the target resolution
    x_res = resolution  # X resolution in degrees
    y_res = resolution  # Y resolution in degrees

    # Perform the resampling
    gdal.Warp(
        res_tiff,
        input_raster,
        xRes=x_res,
        yRes=y_res,
        resampleAlg='bilinear'  # Resampling method (e.g., 'nearest', 'bilinear', 'cubic')
    )

    print("\nResampled raster created successfully!")
    return res_tiff