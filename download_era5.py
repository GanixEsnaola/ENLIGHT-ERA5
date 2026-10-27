"""Download ERA5 wind/wave variables from the Copernicus Climate Data Store."""

import os
from datetime import date

import cdsapi

ERA5_FIRST_YEAR = 1940

# Friendly name (shown in the GUI) -> ERA5 variable name (used by the CDS API)
VARIABLES = {
    "10m wind speed (u-component)": "10m_u_component_of_wind",
    "10m wind speed (v-component)": "10m_v_component_of_wind",
    "10m wind speed": "10m_wind_speed",
    "100m wind speed (u-component)": "100m_u_component_of_wind",
    "100m wind speed (v-component)": "100m_v_component_of_wind",
    "Air density over the oceans": "air_density_over_the_oceans",
    "Peak wave period (Tp)": "peak_wave_period",
    "Mean wave period (Te)": "mean_wave_period",
    "Significant height of combined wind waves and swell (Hs)": "significant_height_of_combined_wind_waves_and_swell",
    "Maximum individual wave height (Hmax)": "maximum_individual_wave_height",
}

TIME_FREQUENCIES = ("hourly", "6hourly", "daily", "monthly")

ALL_MONTHS = [f"{m:02d}" for m in range(1, 13)]
ALL_DAYS = [f"{d:02d}" for d in range(1, 32)]
ALL_HOURS = [f"{h:02d}:00" for h in range(24)]
SIX_HOURLY_TIMES = ["00:00", "06:00", "12:00", "18:00"]


def check_period(start_year, end_year):
    last_year = date.today().year
    if start_year > end_year or start_year < ERA5_FIRST_YEAR or end_year > last_year:
        raise ValueError(
            f"Period {start_year}-{end_year} is outside the ERA5 available "
            f"period ({ERA5_FIRST_YEAR}-{last_year})."
        )


def build_request(era5_variable, frequency, year, area):
    request = {
        "variable": [era5_variable],
        "year": [str(year)],
        "month": ALL_MONTHS,
        "day": ALL_DAYS,
        "area": area,
        "data_format": "netcdf",
        "download_format": "unarchived",
    }

    if frequency == "hourly":
        dataset = "reanalysis-era5-single-levels"
        request["product_type"] = ["reanalysis"]
        request["time"] = ALL_HOURS

    elif frequency == "6hourly":
        dataset = "reanalysis-era5-single-levels"
        request["product_type"] = ["reanalysis"]
        request["time"] = SIX_HOURLY_TIMES

    elif frequency == "daily":
        dataset = "derived-era5-single-levels-daily-statistics"
        request["product_type"] = "reanalysis"
        request["daily_statistic"] = "daily_mean"
        request["time_zone"] = "utc+00:00"
        request["frequency"] = "1_hourly"

    elif frequency == "monthly":
        dataset = "reanalysis-era5-single-levels-monthly-means"
        request["product_type"] = ["monthly_averaged_reanalysis"]
        request["time"] = ["00:00"]

    else:
        raise ValueError(f"Unknown time frequency: {frequency}")

    return dataset, request


def download_era5(variable, frequency, start_year, end_year, area, output_folder):
    """Download one ERA5 variable, year by year, into output_folder.

    area is [North, West, South, East], in degrees.
    """
    if variable not in VARIABLES:
        raise ValueError(f"Unknown variable: {variable}")
    if frequency not in TIME_FREQUENCIES:
        raise ValueError(f"Unknown time frequency: {frequency}")
    check_period(start_year, end_year)

    os.makedirs(output_folder, exist_ok=True)
    era5_variable = VARIABLES[variable]
    client = None   # only contact the CDS if something is missing

    for year in range(start_year, end_year + 1):
        filename = os.path.join(output_folder, f"{era5_variable}_{frequency}_{year}.nc")
        if os.path.exists(filename):
            continue
        if client is None:
            client = cdsapi.Client()
        dataset, request = build_request(era5_variable, frequency, year, area)
        client.retrieve(dataset, request, filename)


def download_era5_multi(variables, frequency, start_year, end_year, area, output_folder):
    """Download several ERA5 variables for the same frequency/period/area."""
    for variable in variables:
        download_era5(variable, frequency, start_year, end_year, area, output_folder)


if __name__ == "__main__":
    download_era5_multi(
        variables=[
            "10m wind speed (u-component)",
            "10m wind speed (v-component)",
            "Significant height of combined wind waves and swell (Hs)",
        ],
        frequency="6hourly",
        start_year=2020,
        end_year=2021,
        area=[60, -40, 30, 20],
        output_folder="./ERA5_data",
    )
