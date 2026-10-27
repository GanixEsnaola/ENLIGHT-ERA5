"""Going further: six starting points built on resource_maps.py.

Each function is independent. Most of them make sense with hourly (or 6-hourly)
data: set FREQUENCY in resource_maps.py, download, then call the function you
need at the bottom of this file. With monthly data they run, but extremes and
seasons are smoothed out.
"""

import numpy as np
import xarray as xr

import resource_maps as rm
from download_era5 import download_era5_multi

YEARS = range(rm.START_YEAR, rm.END_YEAR + 1)
HS = "significant_height_of_combined_wind_waves_and_swell"


def all_years(power):
    """Concatenate one quantity (rm.wpd, rm.wef, ...) over all years.
    With hourly data this needs a lot of memory: use a small area."""
    return xr.concat([power(year) for year in YEARS], dim="valid_time")


# 1. Seasons: winter (DJF) and summer (JJA) maps
def seasons():
    seasonal = all_years(rm.wpd).groupby("valid_time.season").mean()
    for season in ("DJF", "JJA"):
        rm.plot_map(seasonal.sel(season=season), f"Mean WPD, {season}", "WPD (W/m²)",
                    "viridis", f"WPD_{season}.png")


# 2. Variability: how much does the yearly mean change from year to year?
def variability():
    yearly = xr.concat([rm.wpd(year).mean("valid_time") for year in YEARS], dim="year")
    cv = yearly.std("year") / yearly.mean("year")          # coefficient of variation
    rm.plot_map(cv, "Year-to-year variability of WPD", "CV (-)", "magma", "WPD_cv.png")


# 3. Extremes: percentiles and exceedance of the significant wave height
def extremes(threshold=6.0):
    hs = all_years(lambda year: rm.load(HS, year))
    exceedance = 100 * (hs > threshold).mean("valid_time")   # % of time above the threshold
    hs99 = hs.quantile(0.99, dim="valid_time")              # 99th percentile
    rm.plot_map(exceedance, f"Time with Hs > {threshold:g} m", "%", "magma", "Hs_exceedance.png")
    rm.plot_map(hs99, "99th percentile of Hs", "Hs (m)", "magma", "Hs_p99.png")


# 4. Hub height: WPD with the 100 m wind instead of the 10 m wind
#    (100 m speed is only built from u and v: use hourly or 6-hourly data)
def hub_height():
    download_era5_multi(["100m wind speed (u-component)", "100m wind speed (v-component)"],
                        rm.FREQUENCY, rm.START_YEAR, rm.END_YEAR, rm.AREA, rm.DATA_FOLDER)

    def wpd100(year):
        speed = np.hypot(rm.load("100m_u_component_of_wind", year),
                         rm.load("100m_v_component_of_wind", year))
        rho = rm.load("air_density_over_the_oceans", year).reindex_like(speed, method="nearest")
        return 0.5 * rho * speed**3

    rm.plot_map(rm.time_mean(wpd100), "Mean WPD at 100 m", "WPD (W/m²)", "viridis", "WPD_100m.png")


# 5. Monthly cycle: twelve mean maps, and the annual cycle at one point
def monthly_cycle(lat=45.0, lon=-5.0):
    cycle = all_years(rm.wef).groupby("valid_time.month").mean()
    point = cycle.sel(latitude=lat, longitude=lon, method="nearest")
    print("Mean WEF (kW/m) by month:", np.round(point.values, 1))
    return cycle


# 6. GIS export: the mean map as a GeoTIFF for QGIS (needs rioxarray)
def gis_export():
    import rioxarray  # noqa: F401  (adds the .rio accessor)
    wpd_map = rm.time_mean(rm.wpd)
    wpd_map = wpd_map.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude")
    wpd_map = wpd_map.rio.write_crs("EPSG:4326").rio.write_nodata(np.nan)   # land = no data
    wpd_map.rio.to_raster("WPD_mean.tif")
    print("Saved WPD_mean.tif")


if __name__ == "__main__":
    seasons()
    variability()
    monthly_cycle()
    gis_export()
    # extremes() and hub_height() need hourly or 6-hourly data (see above)
