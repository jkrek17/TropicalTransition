"""
Configuration file for Tropical Cyclone and Ship Track Visualization Project

This file contains all the customizable settings for the map generation.
Modify these values to easily change map appearance and behavior.
"""

# =============================================================================
# STORM SELECTION SETTINGS
# =============================================================================

# Storm selection options
STORM_YEAR = 2022                    # Year to search for storms
STORM_NAME = "Fiona"               # Name of the storm (case-insensitive)
STORM_BASIN = "Atlantic"             # Basin: "Atlantic", "Pacific", "Indian", or "All"

# Auto-download options
AUTO_DOWNLOAD_STORM_DATA = True      # Automatically download storm data from NOAA
FALLBACK_TO_SAMPLE_DATA = True       # Use sample data if storm not found
SAVE_DOWNLOADED_DATA = True          # Save downloaded data to files

# Storm data sources
HURDAT2_ATLANTIC_URL = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2023-051124.txt"
HURDAT2_PACIFIC_URL = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-nepac-1949-2023-051124.txt"

# Basin-specific settings (used for default map center/zoom when no data available)
BASIN_SETTINGS = {
    "Atlantic": {
        "data_url": HURDAT2_ATLANTIC_URL,
        "data_file": "hurdat2_atlantic.txt",
        "bounds": (-85.0, -20.0, 5.0, 50.0),  # (lon_min, lon_max, lat_min, lat_max)
        "center": [30.0, -60.0],               # [lat, lon] for map center
        "zoom": 4
    },
    "Pacific": {
        "data_url": HURDAT2_PACIFIC_URL,
        "data_file": "hurdat2_pacific.txt", 
        "bounds": (-180.0, -80.0, 5.0, 50.0),
        "center": [25.0, -130.0],
        "zoom": 4
    },
    "Indian": {
        "data_url": None,  # No HURDAT2 data for Indian Ocean
        "data_file": None,
        "bounds": (40.0, 120.0, -40.0, 30.0),
        "center": [-5.0, 80.0],
        "zoom": 4
    }
}

# =============================================================================
# MAP APPEARANCE SETTINGS
# =============================================================================

# Figure settings for static maps
FIGURE_SIZE = (12, 8)  # Width, height in inches
FIGURE_DPI = 300       # Resolution for high-quality output

# Default bounds (used as fallback when no data is available)
DEFAULT_BOUNDS = (-85.0, -50.0, 15.0, 50.0)  # Western Atlantic
AUTO_BOUNDS_PADDING = 10.0  # Degrees of padding when auto-calculating bounds from data

# Grid settings
LATITUDE_SPACING = 5   # Degrees between latitude lines
LONGITUDE_SPACING = 5  # Degrees between longitude lines
GRID_LINEWIDTH = 0.5
GRID_COLOR = 'gray'
GRID_ALPHA = 0.5
GRID_LINESTYLE = '--'

# Map features
LAND_COLOR = 'lightgray'
LAND_ALPHA = 0.8
OCEAN_COLOR = 'lightblue'
OCEAN_ALPHA = 0.6
COASTLINE_WIDTH = 0.8
COASTLINE_COLOR = 'black'
BORDERS_WIDTH = 0.5
BORDERS_COLOR = 'gray'
STATES_WIDTH = 0.5
STATES_COLOR = 'gray'

# =============================================================================
# LEGEND SETTINGS
# =============================================================================

# Legend positioning - choose from: 'upper left', 'upper right', 'lower left', 'lower right'
LEGEND_POSITION = 'upper left'
LEGEND_FONTSIZE = 10
LEGEND_FRAME_ALPHA = 0.9

# Legend corner positions (automatically calculated based on LEGEND_POSITION)
LEGEND_CORNER_POSITIONS = {
    'upper left': {'matplotlib': 'upper left', 'folium': {'bottom': 'auto', 'left': '50px', 'top': '50px', 'right': 'auto'}},
    'upper right': {'matplotlib': 'upper right', 'folium': {'bottom': 'auto', 'left': 'auto', 'top': '50px', 'right': '50px'}},
    'lower left': {'matplotlib': 'lower left', 'folium': {'bottom': '50px', 'left': '50px', 'top': 'auto', 'right': 'auto'}},
    'lower right': {'matplotlib': 'lower right', 'folium': {'bottom': '50px', 'left': 'auto', 'top': 'auto', 'right': '50px'}}
}

# =============================================================================
# OUTPUT SETTINGS
# =============================================================================

# File paths
OUTPUT_DIR = "output"
STATIC_MAP_FILENAME = "tropical_cyclone_map_static.png"
INTERACTIVE_MAP_FILENAME = "tropical_cyclone_map.html"

# Save settings
SAVE_DPI = 300
SAVE_BBOX_INCHES = 'tight'
SAVE_FACECOLOR = 'white'
SAVE_EDGECOLOR = 'none'

# =============================================================================
# DATA PROCESSING SETTINGS
# =============================================================================

# CSV file paths
SAMPLE_SHIP_DATA = "sample_data/sample_ship_data.csv"
# Dynamic storm data file path based on storm configuration
STORM_DATA_FILE = f"data/{STORM_NAME.lower()}_{STORM_YEAR}_storm_track.geojson"

# =============================================================================
# DEBUG AND LOGGING SETTINGS
# =============================================================================

VERBOSE_OUTPUT = True
SAVE_DEBUG_INFO = True 