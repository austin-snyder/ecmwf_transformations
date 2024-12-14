import os
import pathlib

import cdsapi


def batch_download(variables, years, months):
    """
    Downloads data for specified variables, years, and months in batches.

    Parameters:
        variables (list of str): List of variables to download data for.
        years (list of str): List of years to download data for.
        months (list of str): List of months to download data for.

    Returns:
        list: List of periods for which data was downloaded.
    """
    periods = []
    for year in years:
        for month in months:
            days = monthdays(month, year)
            times = [
                "00:00", "01:00", "02:00", "03:00", "04:00", "05:00",
                "06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
                "12:00", "13:00", "14:00", "15:00", "16:00", "17:00",
                "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"
            ]
            period = api_request(variables, year, month, days, times)
            periods.append(period)
    return periods


def monthdays(month, year):
    """
    Returns a list of days for a given month and year.

    Parameters:
        month (str): The month for which to get the days.
        year (str): The year for which to get the days.

    Returns:
        list: List of days in the specified month and year.
    """
    if month in ["01", "03", "05", "07", "08", "10", "12"]:
        days = [
            "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
            "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
            "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31"
        ]
    else:
        if month == "02":
            if int(year) % 4 == 0:
                days = [
                    "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
                    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
                    "21", "22", "23", "24", "25", "26", "27", "28", "29"
                ]
            else:
                days = [
                    "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
                    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
                    "21", "22", "23", "24", "25", "26", "27", "28"
                ]
        else:
            days = [
                "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
                "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
                "21", "22", "23", "24", "25", "26", "27", "28", "29", "30"
            ]
    return days


def download_period(years, months, days, times):
    """
    Finds the minimum and maximum date-times for the period.

    Parameters:
        years (list of str): List of years.
        months (list of str): List of months.
        days (list of str): List of days.
        times (list of str): List of times.

    Returns:
        list: List containing the minimum and maximum date-times.
    """
    min_yr = min(years)
    min_mo = min(months)
    min_dy = min(days)
    min_tm = min(times).split(':')[0:1]

    max_yr = max(years)
    max_mo = max(months)
    max_dy = max(days)
    max_tm = max(times).split(':')[0:1]

    minmaxperiod = [min_yr, min_mo, min_dy, max_yr, max_mo, max_dy]

    return minmaxperiod


def api_request(variables, year, month, days, times):
    """
    Downloads ERA5 reanalysis data for specified years, months, and variables.

    Parameters:
        years (list of str): List of years to download data for.
        months (list of str): List of months to download data for.
        variables (list of str): List of variables to download data for.
    
    Returns:
        None

    The function checks if the data for the specified period already exists
    and skips the download if it does. Otherwise, it retrieves the data from
    the CDS API and saves it in the specified directory.
    """
    dataset = "reanalysis-era5-single-levels"
    request = {
        "product_type": ["reanalysis"],
        "year": [year],
        "month": [month],
        "day": days,
        "time": times,
        "data_format": "netcdf",
        "download_format": "unarchived",
        "variable": variables
    }

    period = download_period([year], [month], days, times)

    print(f'Downloading data from: {period[0]}-{period[1]}-{period[2]} to {period[3]}-{period[4]}-{period[5]}.')
    period = f'{period[0]}{period[1]}{period[2]}_to_{period[3]}{period[4]}{period[5]}'
    filename = f'download_{period}'

    client = cdsapi.Client()

    variable_list = '-'.join(map(str, variables))
    output_dir = os.path.join('.', 'era5_data', f'{variable_list}', 'downloads')
    output_filename = f'{filename}.nc'
    output_location = os.path.join(f'{output_dir}', f'{output_filename}')

    file_path = pathlib.Path(f'{output_location}')
    if file_path.exists():
        print(f"Data for the period {period} has already been downloaded.")
    else:
        os.makedirs(output_dir, exist_ok=True)
        client.retrieve(dataset, request).download(output_location)
        print(f"Data for the period {period} has been downloaded.")

    return period