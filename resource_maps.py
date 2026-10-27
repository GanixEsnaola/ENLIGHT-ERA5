"""Wind Power Density (WPD) and Wave Energy Flux (WEF) maps from ERA5.

    WPD = 1/2 * rho_air * U^3                      (W/m^2)
    WEF = rho_w * g^2 / (64 pi) * Hs^2 * Te        (W/m, shown in kW/m)

Both are computed at every time step and then averaged in time:
the mean of U^3 is not the cube of the mean of U.
"""

import os

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from download_era5 import download_era5_multi

# ---- Settings: change these for your own study ----------------------------
AREA = [60, -40, 30, 20]          # [North, West, South, East], degrees
START_YEAR = 2020
END_YEAR = 2024
FREQUENCY = "monthly"             # "monthly", "daily", "6hourly" or "hourly"
DATA_FOLDER = "./ERA5_data"
DOWNLOAD = True                   # False once the files are on disk

RHO_WATER = 1025.0                # kg/m^3, sea water density
G = 9.81                          # m/s^2

# Monthly means already contain the mean wind *speed*. For the other
# frequencies we build the speed from u and v at each time step.
if FREQUENCY == "monthly":
    WIND_VARIABLES = ["10m wind speed"]
else:
    WIND_VARIABLES = ["10m wind speed (u-component)", "10m wind speed (v-component)"]

VARIABLES = WIND_VARIABLES + [
    "Air density over the oceans",
    "Significant height of combined wind waves and swell (Hs)",
    "Mean wave period (Te)",
]


def load(era5_variable, year):
    """Open one yearly file and return its data variable (si10, u10, swh, ...)."""
    filename = os.path.join(DATA_FOLDER, f"{era5_variable}_{FREQUENCY}_{year}.nc")
    ds = xr.open_dataset(filename)
    return ds[list(ds.data_vars)[0]]


def wpd(year):
    """Wind Power Density at every time step of one year (W/m^2)."""
    if FREQUENCY == "monthly":
        speed = load("10m_wind_speed", year)
    else:
        speed = np.hypot(load("10m_u_component_of_wind", year),
                         load("10m_v_component_of_wind", year))
    # Air density is a wave-model field (0.5 deg, sea only): take the nearest
    # value on the wind grid. Over land it is missing, so WPD is offshore only.
    rho_air = load("air_density_over_the_oceans", year).reindex_like(speed, method="nearest")
    return 0.5 * rho_air * speed**3


def wef(year):
    """Wave Energy Flux at every time step of one year (kW/m)."""
    hs = load("significant_height_of_combined_wind_waves_and_swell", year)
    te = load("mean_wave_period", year)
    return RHO_WATER * G**2 / (64 * np.pi) * hs**2 * te / 1000.0


def time_mean(power):
    """Mean over the whole period, reading one year at a time to save memory."""
    total, count = 0, 0
    for year in range(START_YEAR, END_YEAR + 1):
        p = power(year)
        total = total + p.sum("valid_time", min_count=1)
        count += p.sizes["valid_time"]
    return total / count


def plot_map(field, title, label, cmap, outplot):
    fig = plt.figure(figsize=(9, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    field.plot(ax=ax, transform=ccrs.PlateCarree(), cmap=cmap,
               cbar_kwargs={"label": label, "shrink": 0.8})
    ax.add_feature(cfeature.LAND, facecolor="lightgrey", zorder=2)
    ax.coastlines(resolution="50m", zorder=3)
    # Labels only left and bottom: the right side is for the colour bar
    ax.gridlines(draw_labels=["bottom", "left"], linewidth=0.3, linestyle="--")
    ax.set_title(title)
    fig.savefig(outplot, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {outplot}")


if __name__ == "__main__":
    if DOWNLOAD:
        download_era5_multi(VARIABLES, FREQUENCY, START_YEAR, END_YEAR, AREA, DATA_FOLDER)

    period = f"{START_YEAR}-{END_YEAR}"
    plot_map(time_mean(wpd), f"ERA5 mean WPD ({FREQUENCY}, {period})", "WPD (W/m²)",
             "viridis", f"WPD_{FREQUENCY}_{period}.png")
    plot_map(time_mean(wef), f"ERA5 mean WEF ({FREQUENCY}, {period})", "WEF (kW/m)",
             "magma", f"WEF_{FREQUENCY}_{period}.png")
