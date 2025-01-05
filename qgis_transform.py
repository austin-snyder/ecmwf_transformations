# Standard libraries
import os
import pathlib

# Third-party libraries
from osgeo import gdal

# QGIS-specific libraries
from qgis import processing
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry, QgsNativeAlgorithms
from qgis.core import (
    QgsApplication,
    QgsRasterLayer,
    QgsRasterBandStats,
    QgsProcessingFeedback,
    QgsSingleBandPseudoColorRenderer,
    QgsVectorLayer,
    QgsMapSettings,
    QgsMapRendererCustomPainterJob,
    QgsColorRampShader,
    QgsRasterShader
)
from PyQt5.QtGui import QImage, QPainter, QColor
from PyQt5.QtCore import QSize, Qt


def init_qgis(variables, periods, input_dir):
    """
    Initialize the QGIS application.

    Parameters:
        variables (list): List of variables.
        periods (list): List of periods.
        input_dir (str): Input directory.

    Returns:
        None
    """
    print("Initializing QGIS...")
    qgs = QgsApplication([], False)
    qgs.initQgis()
    from processing.core.Processing import Processing
    Processing.initialize()

    for period in periods:
        print(f"Applying QGIS transformations to the data for period {period}")

        # Load the raster
        variable_list = '-'.join(map(str, variables))
        directory_path = pathlib.Path(f'./era5_data/{variable_list}')
        input_directory = pathlib.Path(f'{directory_path}/{input_dir}/geotiffs/')
        png_directory = pathlib.Path(f'{directory_path}/{input_dir}/png/')

        month = period[4:6]
        if (month == "") or (input_dir == "monthly_means"):
            input_path_suffix = f"{period}"
        else:
            input_path_suffix = f"month{month}_{period}"

        # Anomaly Check
        if input_dir == "monthly_anomalies":
            input_path_name = f"anomaly_{input_path_suffix}"
        elif input_dir == "monthly_means":
            input_path_name = f"mean_{input_path_suffix}"

        null_tiff = set_null_in_raster(input_directory, input_path_name)
        res_tiff = resample_raster(input_directory, f"{input_path_name}_NULL", 0.018)
        create_raster_image(res_tiff, png_directory, input_path_name)

    qgs.exitQgis()


def set_null_in_raster(in_dir, in_filename):
    """
    Set missing values in a raster to NULL.

    Parameters:
        in_dir (str): The input directory containing the raster file.
        in_filename (str): The input filename of the raster file.

    Returns:
        str: Path to the new raster file with NULL values set.
    """
    print("\tSetting missing values to NULL...")

    input_tiff = os.path.join(in_dir, f"{in_filename}.tif")
    null_tiff = os.path.join(in_dir, f"{in_filename}_NULL.tif")

    # Check if the output file already exists
    if os.path.exists(null_tiff):
        print(f"\t\tData for the period has already been set to NULL. Skipping setting NULL values.")
        return null_tiff

    print("\t\tLoading raster...")
    dataset = gdal.Open(input_tiff, gdal.GA_Update)  # Open the raster file in update mode

    if dataset is None:
        print("\t\tFailed to open the raster file.")
        exit()

    # Get the single raster band
    band = dataset.GetRasterBand(1)  # Band index is 1 for the first (and only) band
    band.SetNoDataValue(-9999) # set the NoData value for the band
    print("\t\tNoData value set to -9999 for the single band.")

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
        str: Path to the resampled raster file.
    """
    print("\tResampling raster to higher resolution...")

    res_tiff = os.path.join(in_dir, f"{in_filename}_res.tif")

    # Check if the output file already exists
    if os.path.exists(res_tiff):
        print(f"\t\tData for the period has already been resampled. Skipping resampling.")
        return res_tiff

    # Set input and output paths
    print("\t\tSetting up resampling inputs...")
    res_tiff = os.path.join(in_dir, f"{in_filename}_res.tif")

    # Open the input dataset
    input_raster = gdal.Open(os.path.join(in_dir, f"{in_filename}.tif"))

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

    print("\t\tResampled raster created successfully!")
    return res_tiff


def create_raster_image(raster_path, image_directory, input_path_name):
    """
    Create a raster image.

    Parameters:
        raster_path (str): Path to the raster file.
        image_directory (str): Directory to save the output image.
        input_path_name (str): Input path name.

    Returns:
        None
    """
    shapefile_path = pathlib.Path(f"./shpfiles/world_map/ne_10m_land.shp")
    output_png_path = os.path.join(image_directory, f"{input_path_name}_NULL_res.png")
    if pathlib.Path(output_png_path).exists():
        print(f"\t\tData for the period has already been imaged.")
    else:
        os.makedirs(image_directory, exist_ok=True)
        apply_symbology_and_export_png(raster_path, shapefile_path, output_png_path, input_path_name)
        print(f"\t\tData for the period has been imaged.")


def create_color_ramp_renderer(raster_layer, input_path_name):
    """
    Create a color ramp renderer for the raster layer.

    Parameters:
        raster_layer (QgsRasterLayer): The raster layer to apply the color ramp to.

    Returns:
        QgsSingleBandPseudoColorRenderer: The renderer with the color ramp applied.
    """
    # Calculate Color Ramp Cutoffs
    data_provider = raster_layer.dataProvider()
    band = 1  # Single band raster
    stats = data_provider.bandStatistics(band, QgsRasterBandStats.All, raster_layer.extent(), 0)
    min_value = stats.minimumValue
    max_value = stats.maximumValue
    # cutoffs = [min_value,
    #            min_value + 0.33 * (max_value - min_value),
    #            min_value + 0.66 * (max_value - min_value),
    #            max_value]

    if (input_path_name).startswith("anomaly"):
        cutoffs = [-20, -10, 0, 10, 20]
    elif (input_path_name).startswith("mean"):
        cutoffs = [min_value,
                   min_value + 0.25 * (max_value - min_value),
                   min_value + 0.5 * (max_value - min_value),
                   min_value + 0.75 * (max_value - min_value),
                   max_value]

    # Create and Apply Color Ramp Shader
    raster_shader = QgsRasterShader()
    color_ramp_shader = QgsColorRampShader()
    color_ramp_shader.setColorRampType(QgsColorRampShader.Interpolated)

    # evan notes --- do the green/blue from the default pseudocolor + use the orange from the new suggestion
    # evan orange-red: (249, 88, 8)
    # evan yellow: (255, 192, 13)
    # evan pink: (253, 130, 247)
    # evan blue: (76, 157, 249)
    # default red: (215, 25, 28)
    # default orange: (253, 174, 97)
    # default yellow: (255, 255, 191)
    # default light green: (171, 221, 164)
    # default blue: (43, 131, 186)

    color_ramp = [
        QgsColorRampShader.ColorRampItem(cutoffs[0], QColor(43, 131, 186), f'{cutoffs[0]:.2f}'),  # Default Blue: 43, 131, 186
        QgsColorRampShader.ColorRampItem(cutoffs[1], QColor(171, 221, 164), f'{cutoffs[1]:.2f}'),  # Default Light Green: 171, 221, 164
        QgsColorRampShader.ColorRampItem(cutoffs[2], QColor(255, 255, 191), f'{cutoffs[2]:.2f}'),  # Default Yellow: 255, 255, 191
        QgsColorRampShader.ColorRampItem(cutoffs[3], QColor(253, 174, 97), f'{cutoffs[3]:.2f}'),  # Default Orange: 253, 174, 97
        QgsColorRampShader.ColorRampItem(cutoffs[4], QColor(249, 88, 8), f'{cutoffs[4]:.2f}')  # Evan Orange-Red: 249, 88, 8
    ]

    color_ramp_shader.setColorRampItemList(color_ramp)
    raster_shader.setRasterShaderFunction(color_ramp_shader)
    renderer = QgsSingleBandPseudoColorRenderer(data_provider, band, raster_shader)

    # Set the color for "no data" values to grey
    # renderer.setNodataColor(QColor(128, 128, 128))  # Grey color for no data values

    return renderer


def apply_symbology_and_export_png(raster_path, shapefile_path, output_png_path, input_path_name):
    """
    Apply single pseudocolor symbology to the raster and mask it with a shapefile before exporting as PNG.

    Parameters:
        raster_path (str): Path to the raster file.
        shapefile_path (str): Path to the shapefile for masking.
        output_png_path (str): Path to save the output PNG file.
        input_path_name (str): Input path name.

    Returns:
        None
    """
    print("\t\tApplying symbology and exporting PNG...")

    # Load the raster layer
    raster_layer = QgsRasterLayer(raster_path, "Resampled Raster")
    if not raster_layer.isValid():
        print("\t\tFailed to load the raster layer.")
        return

    # Load the shapefile layer
    shapefile_layer = QgsVectorLayer(str(shapefile_path), "Mask Layer", "ogr")
    if not shapefile_layer.isValid():
        print("\t\tFailed to load the shapefile layer.")
        return

    # Set fill color to transparent for the shapefile layer
    shapefile_layer.renderer().symbol().setColor(QColor(0, 0, 0, 0))

    # Mask the raster with the shapefile
    raster_dir = os.path.dirname(raster_path)
    masked_path = os.path.join(raster_dir, f"{input_path_name}_NULL_res_mask.tif")
    processing.run(
        "gdal:cliprasterbymasklayer",
        {'INPUT': raster_layer, 'MASK': shapefile_layer, 'OUTPUT': masked_path}
    )

    masked_layer = QgsRasterLayer(masked_path, "Masked Raster")

    renderer = create_color_ramp_renderer(masked_layer, input_path_name)
    masked_layer.setRenderer(renderer)
    masked_layer.triggerRepaint()

    base_ratio_x = 800
    base_ratio_y = 600

    final_ratio_x = base_ratio_x * 10
    final_ratio_y = base_ratio_y * 10

    # Create a QgsMapSettings object
    map_settings = QgsMapSettings()
    map_settings.setLayers([shapefile_layer, masked_layer])
    map_settings.setExtent(masked_layer.extent())
    map_settings.setOutputSize(QSize(final_ratio_x, final_ratio_y))  # Increase the output size to twice the current size

    # Create a QgsMapRendererCustomPainterJob object
    image = QImage(QSize(final_ratio_x, final_ratio_y), QImage.Format_ARGB32_Premultiplied)  # Increase the image size to match the output size
    image.fill(Qt.white)
    painter = QPainter(image)
    job = QgsMapRendererCustomPainterJob(map_settings, painter)
    job.start()
    job.waitForFinished()
    painter.end()

    # Save the image as PNG
    image.save(output_png_path)
    print(f"\t\tPNG exported successfully to {output_png_path}")