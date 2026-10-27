# ENLIGHT-ERA5

Scripts for the ENLIGHT / NEXTGENOFFSHORE lesson **"Offshore wind and wave resource maps from
ERA5 with Python"**: download ERA5 data for an area of your choice from the Copernicus Climate
Data Store, then compute and map the **Wind Power Density (WPD)** and the **Wave Energy Flux (WEF)**.

## Files

| File | Purpose |
|---|---|
| `create_enlight_venv.sh` | Creates the `enlight` Python environment (Linux, macOS) |
| `create_enlight_venv.ps1` | Creates the `enlight` Python environment (Windows PowerShell) |
| `download_era5.py` | Downloads ERA5 variables, one file per variable and year (hourly, 6-hourly, daily or monthly) |
| `resource_maps.py` | Downloads what it needs and plots the mean WPD and WEF maps |
| `wpd_averaging_demo.py` | Shows how much WPD is lost when the wind is averaged before computing the power |
| `going_further.py` | Starting points: seasons, year-to-year variability, extremes, 100 m wind, monthly cycle, GeoTIFF export |

## Quick start

1. **Get the files** into your home folder:

   ```bash
   cd ~
   git clone https://github.com/GanixEsnaola/ENLIGHT-ERA5
   cd ENLIGHT-ERA5
   ```

   Without git: *Code → Download ZIP*, unzip it in your home folder and rename
   `ENLIGHT-ERA5-main` to `ENLIGHT-ERA5`.

2. **Create and activate the environment** (Python 3.10 or newer):

   | | Linux / macOS | Windows (PowerShell) |
   |---|---|---|
   | Create (once) | `bash create_enlight_venv.sh` | `.\create_enlight_venv.ps1` |
   | Activate | `source enlight/bin/activate` | `.\enlight\Scripts\Activate.ps1` |
   | Deactivate | `deactivate` | `deactivate` |

   On Windows, allow local scripts once with
   `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
   Check the environment with:

   ```bash
   python -c "import xarray, netCDF4, cartopy, cdsapi; print('OK')"
   ```

3. **Set up your Climate Data Store key.** Register at <https://cds.climate.copernicus.eu>,
   copy your API key from your profile into a file called `.cdsapirc` in your home folder
   (Windows: `C:\Users\<you>\.cdsapirc`):

   ```
   url: https://cds.climate.copernicus.eu/api
   key: <your-personal-access-token>
   ```

   and accept the licence of each dataset once (bottom of its *Download* tab): ERA5 monthly
   means and ERA5 hourly data on single levels.

4. **Make the maps.** Edit the settings at the top of `resource_maps.py` (`AREA`, years,
   `FREQUENCY`) and run:

   ```bash
   python resource_maps.py           # -> WPD_monthly_2020-2024.png, WEF_monthly_2020-2024.png
   python wpd_averaging_demo.py      # why the time resolution matters
   ```

   Requests wait in a queue at the Climate Data Store, from seconds to hours. Files already on
   disk are never downloaded again, so it is always safe to run a script again.

## Formulas

- WPD = ½ ρ<sub>a</sub> U³ (W/m²), with ρ<sub>a</sub> the ERA5 *air density over the oceans*
- WEF = ρ<sub>w</sub> g² H<sub>s</sub>² T<sub>e</sub> / 64π ≈ 0.49 H<sub>s</sub>² T<sub>e</sub> (kW/m),
  with T<sub>e</sub> the ERA5 *mean wave period*

The power is computed at every time step and then averaged. Maps made from monthly means are a
lower bound of the resource: use 6-hourly or hourly data (`FREQUENCY = "hourly"`) for a resource
assessment.

## Data and references

Generated using Copernicus Climate Change Service information. ERA5 data are distributed by the
Copernicus Climate Data Store under the Copernicus licence.

- Hersbach, H. et al. (2020). The ERA5 global reanalysis. *Q. J. R. Meteorol. Soc.*, 146, 1999–2049.
  https://doi.org/10.1002/qj.3803
- Soci, C. et al. (2024). The ERA5 global reanalysis from 1940 to 2022. *Q. J. R. Meteorol. Soc.*,
  150, 4014–4048. https://doi.org/10.1002/qj.4803
