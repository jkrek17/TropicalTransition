# Storm Configuration Guide

This guide explains how to use the new storm selection configuration options in `config.py` to easily switch between different tropical cyclones and ocean basins.

## Quick Start

To change the storm being analyzed, simply edit these three lines in `config.py`:

```python
STORM_YEAR = 2022                    # Year to search for storms
STORM_NAME = "Fiona"                # Name of the storm (case-insensitive)
STORM_BASIN = "Atlantic"             # Basin: "Atlantic", "Pacific", "Indian", or "All"
```

## Configuration Options

### Storm Selection
```python
# Storm selection options
STORM_YEAR = 2022                    # Year to search for storms
STORM_NAME = "Fiona"                # Name of the storm (case-insensitive)
STORM_BASIN = "Atlantic"             # Basin: "Atlantic", "Pacific", "Indian", or "All"
```

### Auto-Download Settings
```python
# Auto-download options
AUTO_DOWNLOAD_STORM_DATA = True      # Automatically download storm data from NOAA
FALLBACK_TO_SAMPLE_DATA = True       # Use sample data if storm not found
SAVE_DOWNLOADED_DATA = True          # Save downloaded data to files
```

### Basin-Specific Settings
The system automatically adjusts map center, zoom, and bounds based on the selected basin:

```python
BASIN_SETTINGS = {
    "Atlantic": {
        "center": [30.0, -60.0],               # [lat, lon] for map center
        "zoom": 4,                             # Default zoom level
        "bounds": (-85.0, -20.0, 5.0, 50.0)   # (lon_min, lon_max, lat_min, lat_max)
    },
    "Pacific": {
        "center": [25.0, -130.0],
        "zoom": 4,
        "bounds": (-180.0, -80.0, 5.0, 50.0)
    },
    "Indian": {
        "center": [-5.0, 80.0],
        "zoom": 4,
        "bounds": (40.0, 120.0, -40.0, 30.0)
    }
}
```

## Example Configurations

### Hurricane Laura (2020)
```python
STORM_YEAR = 2020
STORM_NAME = "Laura"
STORM_BASIN = "Atlantic"
```

### Hurricane Ida (2021)
```python
STORM_YEAR = 2021
STORM_NAME = "Ida"
STORM_BASIN = "Atlantic"
```

### Hurricane Ian (2022)
```python
STORM_YEAR = 2022
STORM_NAME = "Ian"
STORM_BASIN = "Atlantic"
```

### Hurricane Fiona (2022) - Default
```python
STORM_YEAR = 2022
STORM_NAME = "Fiona"
STORM_BASIN = "Atlantic"
```

## How It Works

1. **Storm Data Source**: The system automatically downloads real hurricane track data from NOAA's HURDAT2 database
2. **Basin Selection**: Based on the `STORM_BASIN` setting, the system uses the appropriate HURDAT2 dataset (Atlantic or Pacific)
3. **Automatic Fallback**: If the specified storm isn't found, the system can fall back to sample data
4. **Map Optimization**: Map center, zoom, and bounds are automatically adjusted for the selected basin

## Data Sources

- **Atlantic Basin**: HURDAT2 Atlantic hurricane database (1851-2023)
- **Pacific Basin**: HURDAT2 Northeast Pacific hurricane database (1949-2023)
- **Indian Basin**: Currently uses sample data (no HURDAT2 equivalent available)

## Usage Examples

### Basic Usage
1. Edit `config.py` with your desired storm settings
2. Run `python main.py` to create maps with the configured storm
3. Output files will be named based on your configuration

### Testing Configuration
Run the configuration demo to test your settings:
```bash
python config_demo.py
```

This will:
- Show your current configuration
- Search for available storms in the specified year
- Create a test map with your settings
- Provide examples of other storm configurations

### Searching for Available Storms
The demo script will show you all available storms for a given year. For example, storms available in 2022 include:
- ALEX, BONNIE, COLIN, DANIELLE, EARL, FIONA, GASTON, HERMINE, IAN, JULIA, KARL, LISA, MARTIN, NICOLE, OWEN, and others

## Output Files

With the new configuration system, output files are automatically named based on your settings:
- Interactive map: `output/{storm_name}_{year}_{basin}_map.html`
- Storm track: `output/{storm_name}_{year}_track.geojson`
- Static map: `output/tropical_cyclone_map_static.png`

## Advanced Features

### Storm Search Options
```python
STORM_SEARCH_OPTIONS = {
    "exact_match": True,              # Require exact name match (case-insensitive)
    "partial_match": False,           # Allow partial name matching
    "show_alternatives": True,        # Show alternative storms if not found
    "max_alternatives": 10            # Maximum number of alternatives to show
}
```

### Custom Data Sources
```python
# Storm data sources
HURDAT2_ATLANTIC_URL = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2023-051124.txt"
HURDAT2_PACIFIC_URL = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-nepac-1949-2023-051124.txt"
```

## Troubleshooting

### Storm Not Found
If your specified storm isn't found:
1. Check the storm name spelling (case-insensitive)
2. Verify the year is correct
3. Ensure the storm occurred in the specified basin
4. Run `python config_demo.py` to see available storms for that year

### Connection Issues
If NOAA data download fails:
1. Check your internet connection
2. The system will automatically fall back to sample data if `FALLBACK_TO_SAMPLE_DATA = True`
3. You can disable auto-download by setting `AUTO_DOWNLOAD_STORM_DATA = False`

### Basin-Specific Issues
- Atlantic and Pacific basins have full HURDAT2 support
- Indian Ocean currently uses sample data only
- Check the `BASIN_SETTINGS` for supported basins

## Integration with Existing Code

The configuration system is fully integrated with:
- `main.py` - Shows current configuration at startup
- `data_processor.py` - Loads storm data based on configuration
- `map_creator.py` - Uses basin-specific map settings
- `config_demo.py` - Demonstrates configuration usage

All existing functionality remains unchanged, but now uses the centralized configuration system for better maintainability and ease of use. 