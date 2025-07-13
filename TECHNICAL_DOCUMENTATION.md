# Technical Documentation: Tropical Cyclone and Ship Track Visualization Project

## Overview

This document provides detailed technical explanations of each component in the project. It is intended for developers, researchers, and advanced users who need to understand the implementation details, modify the code, or extend the functionality.

---

## Critical Technical Challenge: Dateline Crossing

### The Problem

**Dateline crossing is one of the most pervasive challenges in weather data mapping.** When tropical cyclones, ship tracks, or any geospatial data crosses the International Date Line (180° longitude), traditional mapping approaches fail catastrophically:

#### Common Failures:
1. **Track Discontinuity**: Lines appear to "jump" from -180° to +180°, creating visual gaps
2. **Global Wrapping**: Maps show the entire globe instead of focusing on the data region
3. **Coordinate Confusion**: Longitudes switch from negative to positive values unexpectedly
4. **Incorrect Distances**: Great-circle paths are not rendered correctly across the dateline
5. **Zoom Failures**: Cartopy's `set_extent()` cannot handle regions that cross ±180°

#### Real-World Impact:
- **Pacific Typhoons**: Many cross the dateline during their lifecycle (e.g., Typhoon Hagibis 2019)
- **Global Shipping**: Trans-Pacific voyages often cross 180° longitude
- **Climate Research**: Long-term storm tracking across ocean basins
- **Maritime Safety**: Accurate visualization of vessel movements worldwide

### Our Solution: Intelligent Coordinate System Selection

The project implements an advanced, automatic solution that detects and handles dateline crossing seamlessly:

#### Detection Algorithm
```python
def detect_dateline_crossing(lon_min, lon_max):
    """
    Detects if data crosses the International Date Line.
    
    Args:
        lon_min (float): Minimum longitude in dataset
        lon_max (float): Maximum longitude in dataset
    
    Returns:
        bool: True if dateline crossing detected
    """
    # Method 1: Check if data spans negative and positive longitudes
    crosses_zero = (lon_min < 0 and lon_max > 0)
    
    # Method 2: Check if data spans around 180° longitude
    crosses_180 = (lon_min < 180 and lon_max > 180)
    
    return crosses_zero or crosses_180
```

#### Coordinate System Selection
```python
def create_appropriate_map_projection(dateline_crossing):
    """
    Creates the appropriate map projection based on dateline crossing.
    
    Args:
        dateline_crossing (bool): Whether data crosses the dateline
    
    Returns:
        cartopy.crs.Projection: Appropriate projection
    """
    if dateline_crossing:
        # Use 0-360 longitude system centered at 180°
        return ccrs.PlateCarree(central_longitude=180)
    else:
        # Use standard -180 to 180 system
        return ccrs.PlateCarree()
```

#### Dynamic Extent Calculation
```python
def calculate_safe_extent(lon_min, lon_max, lat_min, lat_max, dateline_crossing):
    """
    Calculates safe map extent that avoids global wrapping.
    
    Args:
        lon_min, lon_max, lat_min, lat_max (float): Data bounds
        dateline_crossing (bool): Whether data crosses dateline
    
    Returns:
        tuple: (lon_min, lon_max, lat_min, lat_max) for map extent
    """
    if dateline_crossing:
        # Transform bounds to 0-360 system
        lon_min_0360 = lon_min + 360 if lon_min < 0 else lon_min
        lon_max_0360 = lon_max + 360 if lon_max < 0 else lon_max
        
        # Constrain to 120-240° to avoid wrapping
        extent_lon_min = max(lon_min_0360, 120)
        extent_lon_max = min(lon_max_0360, 240)
        
        # If range is too wide, center it
        if extent_lon_max - extent_lon_min > 120:
            center = (extent_lon_min + extent_lon_max) / 2
            extent_lon_min = center - 60
            extent_lon_max = center + 60
            
        return (extent_lon_min, extent_lon_max, lat_min, lat_max)
    else:
        # Standard extent for non-dateline crossing data
        return (lon_min, lon_max, lat_min, lat_max)
```

#### Coordinate Transformation for Plotting
```python
def transform_coordinates_for_plotting(lons, use_360_system):
    """
    Transforms coordinates for plotting based on coordinate system.
    
    Args:
        lons (list): Longitude coordinates
        use_360_system (bool): Whether using 0-360 system
    
    Returns:
        list: Transformed longitude coordinates
    """
    if use_360_system:
        # Transform to 0-360 for central_longitude=180 projection
        return [lon + 360 if lon < 0 else lon for lon in lons]
    else:
        # Use original coordinates for standard projection
        return lons
```

### Implementation in MatplotlibMapper

The `MatplotlibMapper` class implements this solution with the following key methods:

#### `calculate_bounds_from_data()`
- **Purpose**: Calculates map bounds from actual data coordinates
- **Dateline Detection**: Automatically detects dateline crossing in the data
- **Coordinate Transformation**: Converts to 0-360 system when needed
- **Safe Bounds**: Ensures bounds work with the chosen coordinate system

#### `create_base_map()`
- **Dynamic Projection**: Selects appropriate projection based on dateline crossing
- **Safe Extent**: Calculates extent that avoids global wrapping
- **Coordinate System**: Uses 0-360 with central_longitude=180 for dateline crossing
- **Standard System**: Uses -180 to 180 for normal data

#### `add_ship_tracks()` and `add_storm_track()`
- **Coordinate Detection**: Automatically detects the projection being used
- **Dynamic Transformation**: Transforms coordinates only when needed
- **Geodetic Plotting**: Uses `transform=ccrs.Geodetic()` for correct great-circle lines

### Key Technical Features

#### 1. Automatic Detection
```python
# Detects dateline crossing in any dataset
dateline_crossing = (lon_min < 0 and lon_max > 0) or (lon_min < 180 and lon_max > 180)
```

#### 2. Dynamic Coordinate Transformation
```python
# Switches between coordinate systems seamlessly
if use_360_system:
    lons = [lon + 360 if lon < 0 else lon for lon in lons]
```

#### 3. Focused Map Extent
```python
# Avoids global wrapping with intelligent bounds
extent_lon_min = max(lon_min, 120)  # Don't go below 120°
extent_lon_max = min(lon_max, 240)  # Don't go above 240°
```

#### 4. Great-Circle Accuracy
```python
# Ensures correct track rendering across the dateline
ax.plot(lons, lats, transform=ccrs.Geodetic())
```

#### 5. Seamless Integration
- Works with both interactive (Folium) and static (Matplotlib) maps
- No manual configuration required
- Handles any geographic region automatically

### Interactive Maps (Folium) Dateline Handling

While the static maps use coordinate system transformation, **Folium/Leaflet requires a different approach** due to web mapping library constraints:

#### The Folium Challenge

Folium (based on Leaflet.js) has specific limitations with dateline crossing:
- **Coordinate System**: Only supports -180 to +180 longitude
- **No Native Dateline Support**: Cannot handle tracks that cross 180°/-180°
- **Global Wrapping**: Tracks appear to wrap around the entire globe
- **Discontinuous Lines**: Tracks break at the dateline boundary

#### Our Folium Solution: Track Splitting

Instead of coordinate transformation, we use **intelligent track splitting**:

```python
def handle_folium_dateline_crossing(coords):
    """
    Split track at dateline for Folium display.
    
    Args:
        coords (list): Original track coordinates
    
    Returns:
        tuple: (coords_before_dateline, coords_after_dateline)
    """
    folium_coords_before = []
    folium_coords_after = []
    
    for coord in coords:
        lon, lat = coord
        # Convert to -180 to 180 for Folium
        if lon > 180:
            lon = lon - 360
        folium_coord = [lat, lon]  # Folium expects [lat, lon]
        
        # Split at approximately 180° (or -180°)
        if lon > 0:
            folium_coords_after.append(folium_coord)
        else:
            folium_coords_before.append(folium_coord)
    
    return folium_coords_before, folium_coords_after
```

#### Implementation in MapCreator

The `MapCreator` class implements Folium dateline handling:

##### `calculate_map_center_and_zoom()`
```python
def calculate_map_center_and_zoom(self, ship_geojson=None, storm_geojson=None):
    """Calculate optimal center and zoom with dateline detection."""
    # Detect dateline crossing
    dateline_crossing = (min(all_lons) < 0 and max(all_lons) > 0) or \
                       (min(all_lons) < 180 and max(all_lons) > 180)
    
    if dateline_crossing:
        # Convert to 0-360 for center calculation
        lons_0360 = [lon + 360 if lon < 0 else lon for lon in all_lons]
        center_lon_0360 = (min(lons_0360) + max(lons_0360)) / 2
        
        # Convert back to -180 to 180 for Folium
        if center_lon_0360 > 180:
            center_lon = center_lon_0360 - 360
        else:
            center_lon = center_lon_0360
    else:
        # Standard calculation
        center_lon = (min(all_lons) + max(all_lons)) / 2
```

##### `add_ship_tracks()` and `add_storm_track()`
```python
def add_ship_tracks(self, ship_geojson, layer_name="Ship Tracks"):
    """Add ship tracks with dateline crossing handling."""
    for feature in ship_geojson['features']:
        if feature['geometry']['type'] == 'LineString':
            coords = feature['geometry']['coordinates']
            
            # Detect dateline crossing
            track_lons = [coord[0] for coord in coords]
            dateline_crossing = (min(track_lons) < 0 and max(track_lons) > 0) or \
                              (min(track_lons) < 180 and max(track_lons) > 180)
            
            if dateline_crossing:
                # Split track at dateline
                folium_coords_before, folium_coords_after = \
                    self._split_track_at_dateline(coords)
                
                # Add separate line segments
                if folium_coords_before:
                    folium.PolyLine(locations=folium_coords_before, ...)
                if folium_coords_after:
                    folium.PolyLine(locations=folium_coords_after, ...)
            else:
                # Standard single line
                folium_coords = self._convert_coords_for_folium(coords)
                folium.PolyLine(locations=folium_coords, ...)
```

#### Key Folium Features

##### 1. Automatic Detection
- Detects dateline crossing in each track individually
- Handles mixed datasets (some tracks cross, others don't)

##### 2. Track Splitting
- Splits tracks at the dateline boundary
- Creates separate line segments for each side
- Maintains visual continuity

##### 3. Coordinate Conversion
- Converts all coordinates to -180 to +180 for Folium
- Handles both 0-360 and -180 to +180 input data

##### 4. Center Calculation
- Uses 0-360 system for center calculation when dateline crossing detected
- Converts result back to -180 to +180 for Folium

##### 5. Popup Information
- Indicates when tracks cross the dateline in popups
- Provides clear information about track characteristics

#### Advantages of This Approach

1. **Compatibility**: Works with standard Folium/Leaflet libraries
2. **Accuracy**: Shows correct track paths without global wrapping
3. **Performance**: No complex coordinate transformations in browser
4. **User Experience**: Clear, intuitive visualization
5. **Scalability**: Handles multiple tracks efficiently

#### Real-World Examples

This solution correctly handles:

- **Pacific Typhoons**: Tracks crossing from Western to Eastern Pacific
- **Trans-Pacific Shipping**: Vessel routes from Asia to North America

### Real-World Applications

This solution is essential for:

#### Pacific Typhoon Tracking
- **Typhoon Hagibis (2019)**: Crossed dateline multiple times
- **Typhoon Faxai (2019)**: Tracked from 140°E to 180°E
- **Typhoon Kammuri (2019)**: Complex path crossing 180° longitude

#### Global Shipping Routes
- **Trans-Pacific Voyages**: Container ships crossing 180° longitude
- **Arctic Routes**: Vessels navigating through Bering Strait
- **Circumnavigation**: Ships traveling around the world


### Testing and Validation

The solution has been tested with:
- **Sample Data**: Synthetic dateline crossing scenarios
- **Real Storm Data**: NOAA HURDAT2 Pacific typhoon tracks
- **Ship Track Data**: AIS data from trans-Pacific voyages
- **Edge Cases**: Data exactly at ±180° longitude

### Performance Considerations

- **Detection Overhead**: Minimal computational cost for dateline detection
- **Coordinate Transformation**: Linear time complexity O(n) for n coordinates
- **Memory Usage**: No significant additional memory requirements
- **Rendering Performance**: Geodetic transformation adds minimal overhead

---

## Project Architecture

The project follows a modular architecture with clear separation of concerns:

```
main.py                    # Application entry point and workflow orchestration
config.py                  # Centralized configuration management
src/
├── data_processor.py      # Data loading, processing, and GeoJSON conversion
├── nhc_data_downloader.py # NOAA HURDAT2 data acquisition and parsing
├── map_creator.py         # Interactive Folium map generation
├── matplotlib_mapper.py   # Static Matplotlib/Cartopy map generation (with dateline handling)
└── utils.py              # Shared utility functions
```

---

## 1. main.py - Application Entry Point

### Purpose
The main application orchestrates the entire workflow, from data loading to map generation. It serves as the single entry point for the application.

### Key Components

#### Import Structure
```python
import os
import sys
import json
from src.data_processor import DataProcessor
from src.map_creator import MapCreator
from src.matplotlib_mapper import MatplotlibMapper
```

#### Main Function Workflow
1. **Initialization**: Creates instances of data processor and map creators
2. **Ship Data Processing**: Loads and processes ship track data
3. **Storm Data Processing**: Loads and processes storm track data
4. **Interactive Map Generation**: Creates Folium-based web map
5. **Static Map Generation**: Creates Matplotlib-based presentation map
6. **Data Table Generation**: Creates summary table visualization

### Data Flow
```
Real/Sample Ship Data → DataProcessor → GeoJSON → MapCreator → Interactive Map
Real/Sample Storm Data → DataProcessor → GeoJSON → MatplotlibMapper → Static Map
```

### Error Handling
- Graceful fallback from real data to sample data
- Comprehensive error reporting for each processing step
- Validation of output file generation

### Configuration Integration
- Uses config.py settings for file paths and processing parameters
- Supports both real and sample data workflows
- Configurable output file naming and locations

---

## 2. config.py - Configuration Management

### Purpose
Centralizes all configurable parameters, making the project easily customizable without code modifications.

### Configuration Categories

#### Map Appearance Settings
```python
FIGURE_SIZE = (12, 8)  # Width, height in inches
FIGURE_DPI = 300       # Resolution for high-quality output
DEFAULT_BOUNDS = (-85.0, -50.0, 15.0, 50.0)  # Western Atlantic
AUTO_BOUNDS_PADDING = 5.0  # Degrees of padding when auto-calculating bounds
```

#### Grid Configuration
```python
LATITUDE_SPACING = 5   # Degrees between latitude lines
LONGITUDE_SPACING = 5  # Degrees between longitude lines
GRID_LINEWIDTH = 0.5
GRID_COLOR = 'gray'
GRID_ALPHA = 0.5
GRID_LINESTYLE = '--'
```

#### Map Feature Styling
```python
LAND_COLOR = 'lightgray'
LAND_ALPHA = 0.8
OCEAN_COLOR = 'lightblue'
OCEAN_ALPHA = 0.6
COASTLINE_WIDTH = 0.8
COASTLINE_COLOR = 'black'
```

#### Storm Track Visualization
```python
STORM_TRACK_COLOR = 'red'
STORM_TRACK_WIDTH = 3
STORM_TRACK_ALPHA = 0.9
STORM_TRACK_LINESTYLE = '-'

STORM_MARKERS = {
    'hurricane': {  # >= 74 mph
        'color': 'red',
        'size': 100,
        'marker': 'o',
        'label': 'Hurricane (≥74 mph)'
    },
    'tropical_storm': {  # 39-73 mph
        'color': 'orange',
        'size': 80,
        'marker': 'o',
        'label': 'Tropical Storm (39-73 mph)'
    },
    'tropical_depression': {  # < 39 mph
        'color': 'yellow',
        'size': 60,
        'marker': 'o',
        'label': 'Tropical Depression (<39 mph)'
    }
}
```

#### Ship Track Visualization
```python
VESSEL_COLORS = {
    'Cargo': 'blue',
    'Tanker': 'darkblue',
    'Fishing': 'green',
    'Passenger': 'purple',
    'default': 'blue'
}

SHIP_TRACK_WIDTH = 2
SHIP_TRACK_ALPHA = 0.8
SHIP_MARKER_SIZE = 50
SHIP_MARKER_SHAPE = 's'  # Square
```

#### Output Configuration
```python
OUTPUT_DIR = "output"
STATIC_MAP_FILENAME = "tropical_cyclone_map_static.png"
INTERACTIVE_MAP_FILENAME = "tropical_cyclone_map.html"
DATA_TABLE_FILENAME = "data_table.png"
SAVE_DPI = 300
SAVE_BBOX_INCHES = 'tight'
```

### Benefits of Centralized Configuration
- **Maintainability**: All settings in one location
- **Customization**: Easy modification without code changes
- **Consistency**: Ensures uniform styling across components
- **Documentation**: Self-documenting configuration structure

---

## 3. src/data_processor.py - Data Processing Engine

### Purpose
Handles all data loading, processing, and GeoJSON conversion for both ship and storm data.

### Class Structure: DataProcessor

#### Core Methods

##### `load_ship_data_from_csv(csv_file_path)`
**Purpose**: Loads sample ship data from CSV format
**Input**: CSV file path with columns: timestamp, latitude, longitude, vessel_name, vessel_type, speed_knots, heading_degrees
**Output**: GeoPandas GeoDataFrame with Point geometries
**Key Features**:
- Automatic timestamp parsing
- Geometry creation from lat/lon coordinates
- Vessel categorization and ID assignment

##### `load_real_ship_data_from_csv(csv_file_path)`
**Purpose**: Loads real AIS ship data from different CSV format
**Input**: CSV file with columns: MMSI, TimeOfFix, Latitude, Longitude, SOG, Heading, PortIndex, EEZ
**Output**: GeoPandas GeoDataFrame with processed real ship data
**Key Features**:
- Handles different column naming conventions
- MMSI-based vessel identification
- Automatic data validation and error handling
- Comprehensive track information reporting

##### `create_ship_tracks_geojson(ship_data=None)`
**Purpose**: Converts ship data to GeoJSON format for mapping
**Input**: GeoPandas DataFrame with ship track data
**Output**: GeoJSON FeatureCollection with LineString and Point features
**Key Features**:
- Creates both track lines and individual position points
- Handles multiple vessels per dataset
- Generates comprehensive metadata for each feature
- Supports both sample and real data formats

##### `create_sample_storm_data(storm_name=None, storm_year=None)`
**Purpose**: Generates sample storm track data for any specified storm using config settings
**Output**: GeoJSON FeatureCollection with storm track and position data
**Key Features**:
- Realistic storm progression data
- Intensity-based color coding
- Comprehensive storm metadata
- Temporal progression tracking

##### `save_geojson(geojson_data, output_file)`
**Purpose**: Saves GeoJSON data to file with error handling
**Input**: GeoJSON dictionary and output file path
**Output**: Boolean success indicator
**Key Features**:
- Automatic directory creation
- Comprehensive error handling
- JSON formatting with proper indentation

### Data Processing Pipeline
1. **CSV Loading**: Raw data ingestion with validation
2. **Data Cleaning**: Timestamp parsing, coordinate validation
3. **Geometry Creation**: Point and LineString geometry generation
4. **Metadata Enhancement**: Vessel categorization, storm intensity classification
5. **GeoJSON Conversion**: Standardized geospatial data format
6. **File Output**: Persistent storage with error handling

---

## 4. src/nhc_data_downloader.py - NOAA Data Acquisition

### Purpose
Downloads and processes real hurricane track data from NOAA's HURDAT2 database.

### Class Structure: NHCDataDownloader

#### Core Methods

##### `download_hurdat2_data()`
**Purpose**: Downloads the complete HURDAT2 Atlantic hurricane database
**Source**: NOAA's National Hurricane Center FTP server
**Output**: Raw text data saved to local file
**Key Features**:
- Automatic data directory creation
- Comprehensive error handling
- Progress reporting and validation
- Network timeout protection

##### `parse_hurdat2_data()`
**Purpose**: Parses the HURDAT2 text format into structured data
**Input**: Raw HURDAT2 text data
**Output**: Dictionary of processed storm data
**Key Features**:
- Handles complex HURDAT2 format
- Storm header and track line parsing
- Coordinate string processing
- Comprehensive data validation

##### `_parse_coordinate(coord_str, coord_type)`
**Purpose**: Converts HURDAT2 coordinate strings to decimal degrees
**Input**: Coordinate string (e.g., "325N", "720W") and type ('lat' or 'lon')
**Output**: Decimal coordinate value
**Key Features**:
- Handles N/S/E/W direction indicators
- Automatic sign conversion for southern/western coordinates
- Robust error handling for malformed data
- Integration with shared utils.parse_coordinate()

##### `find_storm_by_name_year(name, year)`
**Purpose**: Locates specific storms in the processed data
**Input**: Storm name and year
**Output**: Storm ID and data dictionary
**Key Features**:
- Case-insensitive name matching
- Year-based filtering
- Comprehensive storm metadata

##### `get_storm_geojson(storm_id, storm_data)`
**Purpose**: Converts storm data to GeoJSON format
**Input**: Storm identifier and processed storm data
**Output**: GeoJSON FeatureCollection
**Key Features**:
- Creates both track lines and position points
- Intensity-based styling
- Comprehensive storm metadata
- Temporal progression tracking

### HURDAT2 Data Format
The HURDAT2 format consists of:
- **Header lines**: Storm identification and metadata
- **Track lines**: Individual position and intensity data
- **Coordinate format**: Degrees with direction indicators (e.g., "325N", "720W")
- **Intensity data**: Wind speed, pressure, storm status

### Data Processing Workflow
1. **Download**: Fetch raw data from NOAA servers
2. **Parse**: Convert text format to structured data
3. **Validate**: Ensure data quality and completeness
4. **Convert**: Transform to GeoJSON format
5. **Store**: Save processed data for mapping

---

## 5. src/map_creator.py - Interactive Map Generation

### Purpose
Creates interactive web maps using Folium (Leaflet.js) for ship and storm track visualization.

### Class Structure: MapCreator

#### Core Methods

##### `create_base_map(center_lat=32.5, center_lon=-72.0, zoom_start=6)`
**Purpose**: Initializes the base map with multiple tile layers
**Input**: Center coordinates and zoom level
**Output**: Folium Map object
**Key Features**:
- Multiple tile layer options (CartoDB, OpenStreetMap, Stamen)
- Scale controls and modern styling
- Configurable center and zoom settings
- Professional map appearance

##### `add_ship_tracks(ship_geojson, layer_name="Ship Tracks")`
**Purpose**: Adds ship track data to the interactive map
**Input**: Ship GeoJSON data and layer name
**Key Features**:
- LineString track visualization
- Individual ship position markers
- Interactive popups with detailed information
- Vessel type-based color coding
- Coordinate system conversion (GeoJSON to Folium)

##### `add_storm_track(storm_geojson, layer_name="Storm Track")`
**Purpose**: Adds storm track data to the interactive map
**Input**: Storm GeoJSON data and layer name
**Key Features**:
- Storm track line visualization
- Intensity-based marker styling
- Interactive popups with storm details
- Temporal progression visualization
- Coordinate system conversion

##### `add_legend()`
**Purpose**: Creates a comprehensive map legend
**Key Features**:
- Visual representation of all data types
- Color-coded storm intensity levels
- Ship track and position indicators
- Professional legend styling

##### `add_measurement_tools()`
**Purpose**: Adds distance and area measurement capabilities
**Key Features**:
- Interactive distance measurement
- Area calculation tools
- Professional measurement interface
- User-friendly controls

##### `add_fullscreen_button()`
**Purpose**: Adds fullscreen viewing capability
**Key Features**:
- Seamless fullscreen transition
- Professional presentation mode
- Enhanced user experience

##### `add_minimap()`
**Purpose**: Adds a minimap for navigation context
**Key Features**:
- Overview map for spatial context
- Synchronized navigation
- Professional map interface

##### `save_map(output_file="output/tropical_cyclone_map.html")`
**Purpose**: Saves the interactive map to HTML file
**Input**: Output file path
**Output**: Saved HTML file path
**Key Features**:
- Complete HTML document generation
- Embedded JavaScript and CSS
- Self-contained file for easy sharing
- Professional styling and layout

### Interactive Features
- **Layer Controls**: Show/hide different data layers
- **Interactive Popups**: Detailed information on click
- **Multiple Tile Layers**: Different map backgrounds
- **Measurement Tools**: Distance and area calculation
- **Fullscreen Mode**: Professional presentation capability
- **Responsive Design**: Works on various screen sizes

---

## 6. src/matplotlib_mapper.py - Static Map Generation

### Purpose
Creates high-quality static maps using Matplotlib and Cartopy for presentations and publications.

### Class Structure: MatplotlibMapper

#### Core Methods

##### `create_base_map(figsize=None, dpi=None, bounds=None)`
**Purpose**: Creates the base map with geographic features
**Input**: Figure size, DPI, and map bounds
**Output**: Matplotlib figure and axes objects
**Key Features**:
- Configurable map extent and resolution
- Professional geographic styling
- Grid line customization
- Coastline and political boundary rendering

##### `calculate_bounds_from_data(ship_geojson=None, storm_geojson=None, padding=None)`
**Purpose**: Automatically calculates optimal map bounds from data
**Input**: Ship and storm GeoJSON data
**Output**: Tuple of (lon_min, lon_max, lat_min, lat_max)
**Key Features**:
- Automatic bounds calculation
- Configurable padding
- Fallback to default bounds
- Data-driven map extent

##### `add_ship_tracks(ship_geojson, ax=None)`
**Purpose**: Adds ship tracks to the static map
**Input**: Ship GeoJSON data and matplotlib axes
**Key Features**:
- LineString track visualization
- Vessel type-based color coding
- Professional styling and transparency
- Coordinate system handling

##### `add_storm_track(storm_geojson, ax=None)`
**Purpose**: Adds storm tracks to the static map
**Input**: Storm GeoJSON data and matplotlib axes
**Key Features**:
- Storm track line visualization
- Intensity-based marker styling
- Professional color scheme
- Temporal progression representation

##### `add_legend(ax=None)`
**Purpose**: Creates a comprehensive map legend
**Input**: Matplotlib axes object
**Key Features**:
- Visual legend elements
- Professional styling
- Configurable position and appearance
- Comprehensive data representation

##### `add_title_and_info(title="Tropical Cyclone and Ship Track Analysis", ax=None)`
**Purpose**: Adds title and data source information
**Input**: Title text and matplotlib axes
**Key Features**:
- Professional title styling
- Data source attribution
- Current date information
- Professional layout

##### `save_map(output_file="output/tropical_cyclone_map_static.png", dpi=300, bbox_inches='tight')`
**Purpose**: Saves the static map to high-quality image file
**Input**: Output file path and quality settings
**Output**: Saved file path
**Key Features**:
- High-resolution output (300 DPI)
- Professional image quality
- Automatic directory creation
- Comprehensive error handling

##### `create_data_table(ship_geojson=None, storm_geojson=None, output_file="output/data_table.png")`
**Purpose**: Creates a summary table visualization
**Input**: Ship and storm GeoJSON data
**Output**: PNG image of data table
**Key Features**:
- Comprehensive data summary
- Professional table styling
- Multiple data categories
- High-quality image output

### Static Map Features
- **High Resolution**: 300 DPI output suitable for publications
- **Professional Styling**: Clean, publication-ready appearance
- **Configurable Grid**: Customizable latitude/longitude spacing
- **Comprehensive Legend**: Visual representation of all data types
- **Data Attribution**: Professional source citations
- **Multiple Output Formats**: PNG, PDF, and other formats supported

---

## 7. src/utils.py - Shared Utilities

### Purpose
Provides shared utility functions used across multiple modules to ensure consistency and reduce code duplication.

### Key Functions

##### `parse_coordinate(coord_str, coord_type)`
**Purpose**: Parses coordinate strings from HURDAT2 format
**Input**: Coordinate string and type ('lat' or 'lon')
**Output**: Decimal coordinate value or None
**Key Features**:
- Handles N/S/E/W direction indicators
- Automatic sign conversion
- Robust error handling
- Used by multiple modules

##### `determine_storm_intensity(wind_speed)`
**Purpose**: Classifies storm intensity based on wind speed
**Input**: Wind speed in mph
**Output**: Dictionary with color, size, marker, and label information
**Key Features**:
- Standardized intensity classification
- Consistent styling across modules
- Configurable thresholds
- Professional color scheme

##### `save_geojson(geojson_data, output_file)`
**Purpose**: Saves GeoJSON data to file with error handling
**Input**: GeoJSON dictionary and output file path
**Output**: Boolean success indicator
**Key Features**:
- Automatic directory creation
- JSON formatting with indentation
- Comprehensive error handling
- Consistent file output

##### `load_geojson(input_file)`
**Purpose**: Loads GeoJSON data from file
**Input**: Input file path
**Output**: GeoJSON dictionary or None
**Key Features**:
- Robust file loading
- Error handling for missing files
- Consistent data format
- Used across multiple modules

##### `calculate_bounds_from_coordinates(coordinates, padding=5.0)`
**Purpose**: Calculates map bounds from coordinate list
**Input**: List of [lon, lat] coordinates and padding
**Output**: Tuple of (lon_min, lon_max, lat_min, lat_max)
**Key Features**:
- Automatic bounds calculation
- Configurable padding
- Fallback to default bounds
- Used for map extent determination

##### `format_coordinate(coord, coord_type)`
**Purpose**: Formats coordinates for display
**Input**: Coordinate value and type ('lat' or 'lon')
**Output**: Formatted coordinate string
**Key Features**:
- Professional coordinate formatting
- Direction indicator handling
- Consistent display format
- Used for data table generation

### Benefits of Shared Utilities
- **Code Reuse**: Eliminates duplication across modules
- **Consistency**: Ensures uniform behavior
- **Maintainability**: Single point of modification
- **Testing**: Centralized testing of common functionality
- **Documentation**: Clear function specifications

---

## Data Flow Architecture

### Complete Workflow
```
1. Data Sources
   ├── Real Ship Data (AIS/SeaVision CSV)
   ├── Sample Ship Data (CSV)
   ├── Real Storm Data (NOAA HURDAT2)
   └── Sample Storm Data (Generated)

2. Data Processing
   ├── CSV Loading (data_processor.py)
   ├── Coordinate Parsing (utils.py)
   ├── Geometry Creation (GeoPandas)
   └── GeoJSON Conversion (data_processor.py)

3. Map Generation
   ├── Interactive Maps (map_creator.py)
   ├── Static Maps (matplotlib_mapper.py)
   └── Data Tables (matplotlib_mapper.py)

4. Output Files
   ├── HTML Interactive Maps
   ├── PNG Static Maps
   ├── PNG Data Tables
   └── GeoJSON Data Files
```

### Configuration Integration
All modules integrate with config.py for:
- File paths and naming
- Map appearance settings
- Data processing parameters
- Output quality settings
- Grid and styling options

### Error Handling Strategy
- **Graceful Degradation**: Fallback from real to sample data
- **Comprehensive Logging**: Detailed error reporting
- **Validation**: Data quality checks at each step
- **User Feedback**: Clear progress and status messages

---

## Global Mapping Capability

### Overview
The project now supports automatic global mapping, meaning it can create maps for any geographic location worldwide without manual configuration. The system automatically calculates optimal map bounds, center coordinates, and zoom levels based on the provided data coordinates.

### Automatic Adaptation Features

#### 1. Dynamic Bounds Calculation
- **Matplotlib Maps**: Automatically calculates map extent from data coordinates
- **Folium Maps**: Automatically determines center coordinates and zoom level
- **Padding**: Configurable padding around data points for optimal viewing
- **Fallback**: Uses default bounds only when no data is available

#### 2. Geographic Flexibility
- **Pacific Ocean**: Works with coordinates like (140°E, 20°N) to (170°E, 35°N)
- **Indian Ocean**: Works with coordinates like (60°E, -10°S) to (90°E, 2°N)
- **Atlantic Ocean**: Works with existing Western Atlantic data
- **Any Region**: Adapts to any geographic coordinates worldwide

#### 3. Zoom Level Intelligence
The system automatically determines appropriate zoom levels based on data extent:
- **Very Wide View** (>100° range): Zoom level 3
- **Wide View** (50-100° range): Zoom level 4
- **Medium View** (20-50° range): Zoom level 5
- **Regional View** (10-20° range): Zoom level 6
- **Local View** (5-10° range): Zoom level 7
- **Detailed View** (2-5° range): Zoom level 8
- **Close View** (<2° range): Zoom level 9

### Implementation Details

#### Matplotlib Mapper (`src/matplotlib_mapper.py`)
```python
def calculate_bounds_from_data(self, ship_geojson=None, storm_geojson=None, padding=None):
    """Calculate map bounds from data with padding."""
    # Collects all coordinates from ship and storm data
    # Calculates min/max bounds with configurable padding
    # Returns (lon_min, lon_max, lat_min, lat_max)
```

#### Folium Map Creator (`src/map_creator.py`)
```python
def calculate_map_center_and_zoom(self, ship_geojson=None, storm_geojson=None):
    """Calculate optimal center coordinates and zoom level from data."""
    # Collects all coordinates from ship and storm data
    # Calculates center point and appropriate zoom level
    # Returns (center_lat, center_lon, zoom_start)
```

### Testing Global Capability
The `tests/test_global_mapping.py` script demonstrates this capability by creating sample data for different regions:

#### Pacific Ocean Test
- **Coordinates**: 135°E to 170°E, 18°N to 35°N
- **Auto-calculated center**: (26.5°N, 152.5°E)
- **Auto-calculated zoom**: 5 (medium view)
- **Result**: Perfectly centered Pacific Ocean map

#### Indian Ocean Test
- **Coordinates**: 55°E to 90°E, -12°S to 2°N
- **Auto-calculated center**: (-5.0°S, 72.5°E)
- **Auto-calculated zoom**: 5 (medium view)
- **Result**: Perfectly centered Indian Ocean map

#### International Date Line Crossing Test
- **Coordinates**: 170°E to -165°E (crosses 180°/-180°)
- **Auto-calculated center**: (27.5°N, 0.5°E)
- **Auto-calculated zoom**: 3 (very wide view)
- **Result**: Correctly handles dateline crossing with wide view

### Benefits of Global Mapping
1. **No Manual Configuration**: Works with any geographic data automatically
2. **Optimal Viewing**: Always shows the most relevant area
3. **Consistent Quality**: Same high-quality output regardless of location
4. **Future-Proof**: Ready for any new geographic regions or data sources
5. **User-Friendly**: No need to understand coordinate systems or map projections

### Usage Examples
```python
# Pacific Ocean data - automatically adapts
pacific_ships = load_pacific_ship_data()
pacific_storms = load_pacific_storm_data()
map_creator.create_complete_map(ship_geojson=pacific_ships, storm_geojson=pacific_storms)

# Indian Ocean data - automatically adapts
indian_ships = load_indian_ship_data()
indian_storms = load_indian_storm_data()
static_mapper.create_complete_static_map(ship_geojson=indian_ships, storm_geojson=indian_storms)

# Any other region - automatically adapts
any_ships = load_any_ship_data()
any_storms = load_any_storm_data()
# Maps will automatically center and zoom appropriately
```

---

## Extension Points
