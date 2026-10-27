# =============================================================================
# create_enlight_venv.ps1
# =============================================================================
# PURPOSE:
#   Windows (PowerShell) version of create_enlight_venv.sh. Run this ONCE.
#
# HOW TO USE (in PowerShell, inside the course folder):
#   1. Allow local scripts (once per user):
#        Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
#   2. Run once:    .\create_enlight_venv.ps1
#   3. Activate:    .\enlight\Scripts\Activate.ps1
#      (cmd.exe:    enlight\Scripts\activate.bat)
#   4. Deactivate:  deactivate
#
# PYTHON:
#   Install Python 3.10+ from https://www.python.org/downloads/windows/ and
#   tick "Add python.exe to PATH". The "py" launcher comes with it.
#   cartopy, netCDF4 and rioxarray ship Windows wheels, so no compiler needed.
# =============================================================================

# Same package list as the Linux/macOS script, written to a temporary file.
@"
xarray
netCDF4
cartopy
rioxarray
cdsapi
"@ | Set-Content requirements.txt

# Create the virtual environment in .\enlight
py -3 -m venv enlight

# Activate it: 'python' and 'pip' now point to .\enlight
.\enlight\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

Remove-Item requirements.txt

Write-Host ""
Write-Host "Setup complete. To activate the environment in future sessions:"
Write-Host "  .\enlight\Scripts\Activate.ps1"
