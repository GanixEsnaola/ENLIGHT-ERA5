"""Why the time resolution matters for WPD: average first, cube later = wrong.

Uses one year of hourly u10/v10 at a single ERA5 grid point off the Basque
coast (downloaded the first time it runs) and compares the mean WPD obtained from:
  - the hourly data (reference)
  - 6-hourly, daily and monthly averages of u, v  (vector mean)
  - 6-hourly, daily and monthly averages of the speed (scalar mean)
"""

import numpy as np
import xarray as xr

from download_era5 import download_era5_multi

POINT = [43.5, -2.5, 43.5, -2.5]   # [N, W, S, E]: a single grid point
YEAR = 1971
DATA_FOLDER = "./ERA5_data"
U_FILE = f"{DATA_FOLDER}/10m_u_component_of_wind_hourly_{YEAR}.nc"
V_FILE = f"{DATA_FOLDER}/10m_v_component_of_wind_hourly_{YEAR}.nc"
RHO_AIR_STD = 1.225  # kg/m^3


def wpd(speed):
    return float((0.5 * RHO_AIR_STD * speed**3).mean())


download_era5_multi(["10m wind speed (u-component)", "10m wind speed (v-component)"],
                    "hourly", YEAR, YEAR, POINT, DATA_FOLDER)   # skipped if already on disk

u = xr.open_dataset(U_FILE)["u10"].squeeze()
v = xr.open_dataset(V_FILE)["v10"].squeeze()
speed = np.hypot(u, v)

reference = wpd(speed)
print(f"Hourly mean speed: {float(speed.mean()):.2f} m/s")
print(f"Hourly WPD (reference): {reference:.1f} W/m2\n")
print(f"{'average':>8} | {'from mean u,v':>14} | {'from mean speed':>15}")

for label, rule in [("6-hourly", "6h"), ("daily", "1D"), ("monthly", "1MS")]:
    u_mean = u.resample(valid_time=rule).mean()
    v_mean = v.resample(valid_time=rule).mean()
    speed_mean = speed.resample(valid_time=rule).mean()
    from_uv = wpd(np.hypot(u_mean, v_mean))
    from_speed = wpd(speed_mean)
    print(f"{label:>8} | {from_uv:7.1f} ({100 * from_uv / reference:3.0f}%) "
          f"| {from_speed:7.1f} ({100 * from_speed / reference:3.0f}%)")

# Energy pattern factor <U^3>/<U>^3. For a Rayleigh distribution it is 6/pi = 1.91
epf = float((speed**3).mean() / speed.mean() ** 3)
print(f"\nEnergy pattern factor: {epf:.2f}  (Rayleigh: {6 / np.pi:.2f})")
