#!/bin/bash
# =============================================================================
# create_enlight_venv.sh
# =============================================================================
# PURPOSE:
#   Bootstrap the complete Python environment for the ERA5 wind and wave
#   resource practical session. Run this ONCE before the session.
#
# WHAT IS A VIRTUAL ENVIRONMENT?
#   A venv is an isolated Python installation that lives inside a folder
#   (here: ./enlight/). All packages installed with pip go into that folder,
#   not into the system Python. This means:
#     - No root/sudo privileges needed
#     - No conflicts with other Python projects on the same machine
#     - Fully reproducible: you know exactly which package versions are installed
#     - Easy to delete: rm -rf enlight/ and start fresh
#
# HOW TO USE:
#   1. Run once:    bash create_enlight_venv.sh
#   2. Activate:    source enlight/bin/activate
#   3. Deactivate:  deactivate
#   4. Your prompt will show (enlight) when the venv is active
#
# WHY EMBED requirements.txt INLINE?
#   The heredoc (cat > file << 'EOF' ... EOF) writes the file right here,
#   so students only need to handle one file, not two. The requirements file
#   is deleted at the end — it is just a temporary intermediary.
#
# PLATFORM NOTE:
#   cartopy requires the system GEOS/PROJ C libraries before pip can build it.
#   On Debian/Ubuntu:  sudo apt-get install libgeos-dev libproj-dev
#   On macOS:          brew install geos proj
#   On Windows:        use conda instead, or install Visual C++ Build Tools
# =============================================================================

# Write requirements.txt inline using a "heredoc".
# Everything between << 'EOF' and EOF is treated as file content.
# The single quotes around 'EOF' prevent shell variable expansion inside.
cat > requirements.txt << 'EOF'
# NetCDF and array handling
xarray          # Labelled N-D arrays — the main interface for NetCDF files
netCDF4         # NetCDF4 backend: without it xarray cannot open the ERA5 files


# Satellite/geospatial (cartopy needs GEOS: see note above)
cartopy         # Geographic map projections and coastline overlays

#GEOTiff exports
rioxarray

#For enlight
cdsapi
EOF

# Create the virtual environment.
# --without-pip skips the ensurepip step, which requires the python3-venv
# system package. We install pip ourselves via get-pip.py right after,
# so no admin rights (sudo) are needed at any point.
python3 -m venv enlight


# Activate the environment.
# After this command, 'python' and 'pip' refer to the venv's versions,
# not the system ones. Your shell prompt will change to show (enlight).
source enlight/bin/activate

# Install all packages listed in requirements.txt.
# pip resolves the dependency graph, downloads wheels (pre-compiled binaries
# where available), and installs everything into enlight/lib/python3.x/
pip install -r requirements.txt

# Remove the temporary requirements file — it has done its job.
rm requirements.txt

# Print a reminder message so students know how to re-activate next time.
echo ""
echo "Setup complete. To activate the environment in future sessions:"
echo "  source enlight/bin/activate"


