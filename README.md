# Tropical Cyclone and Ship Track Visualization Project

This project creates interactive and static maps showing tropical cyclone tracks and ship positions **globally** - automatically adapting to any geographic location worldwide, including the critical challenge of **dateline crossing**.

## Project Overview

The project visualizes:
- **Tropical Cyclone Data** - Storm tracks from NOAA HURDAT2 database or sample data
- **Ship Track Data** - Vessel positions from SeaVision CSV data or real AIS data
- **Interactive Maps** - Modern web-based maps with multiple layers
- **Static Maps** - High-quality presentation maps for publications
- **Global Capability** - Works with data from any geographic region
- **Dateline Crossing** - Advanced handling of International Date Line crossing

## Critical Challenge: Dateline Crossing

**Dateline crossing is one of the most common and challenging problems in weather data mapping.** When tropical cyclones or ship tracks cross the International Date Line (180° longitude), traditional mapping approaches fail because:

- **Track Discontinuity**: Lines appear to "jump" from one side of the map to the other
- **Global Wrapping**: Maps show the entire globe instead of focusing on the data
- **Coordinate Confusion**: Longitudes switch from negative to positive values
- **Incorrect Distances**: Great-circle paths are not rendered correctly

### Our Solution: Intelligent Coordinate System Selection

The project implements an advanced solution that automatically detects and handles dateline crossing:

```python
# Automatic detection of dateline crossing
dateline_crossing = (lon_min < 0 and lon_max > 0) or (lon_min < 180 and lon_max > 180)

if dateline_crossing:
    # Use 0-360 longitude system with central_longitude=180
    projection = ccrs.PlateCarree(central_longitude=180)
    # Transform coordinates to 0-360 for plotting
    lons = [lon + 360 if lon < 0 else lon for lon in lons]
    # Set focused extent (120-240°) to avoid global wrapping
    extent = (120, 240, lat_min, lat_max)
else:
    # Standard -180 to 180 system for normal data
    projection = ccrs.PlateCarree()
    # Use original coordinates
    extent = (lon_min, lon_max, lat_min, lat_max)
```

### Key Features of the Dateline Solution:

✅ **Automatic Detection** - Identifies dateline crossing in any dataset  
✅ **Dynamic Coordinate Transformation** - Switches between -180/180 and 0/360 systems  
✅ **Focused Map Extent** - Avoids global wrapping with intelligent bounds  
✅ **Great-Circle Accuracy** - Uses geodetic transformation for correct track rendering  
✅ **Seamless Integration** - Works with both interactive and static maps  

### Real-World Applications:

This solution is essential for:
- **Pacific Typhoons** - Many cross the dateline during their lifecycle
- **Global Shipping Routes** - Trans-Pacific voyages often cross 180°
- **Climate Research** - Long-term storm tracking across ocean basins
- **Maritime Safety** - Accurate visualization of vessel movements

## Project Structure

```
StudentProject/
├── main.py                           # Application entry point
├── config.py                         # Centralized configuration
├── src/
│   ├── data_processor.py            # Data loading and processing
│   ├── nhc_data_downloader.py      # NOAA storm data acquisition
│   ├── map_creator.py               # Interactive Folium maps
│   ├── matplotlib_mapper.py         # Static Matplotlib maps (with dateline handling)
│   └── utils.py                     # Shared utilities
├── data/                            # Real data files
├── sample_data/                     # Sample data files
├── output/                          # Generated maps and data
├── tests/                           # Test files
├── TUTORIAL.md                      # Comprehensive tutorial
├── STUDENT_SETUP_GUIDE.md          # Student setup instructions
└── TECHNICAL_DOCUMENTATION.md      # Technical implementation details
```

## Global Mapping Capability

The project now supports **automatic global mapping** with advanced dateline handling:

✅ **Any Geographic Region** - Pacific, Indian, Atlantic, or any ocean  
✅ **Automatic Bounds Calculation** - Maps adapt to your data coordinates  
✅ **Smart Zoom Levels** - Optimal viewing based on data extent  
✅ **Dateline Crossing** - Intelligent handling of 180° longitude crossing  
✅ **No Manual Configuration** - Works with any coordinate system  

### Example Regions Tested:
- **Pacific Ocean**: 135°E to 170°E, 18°N to 35°N (with dateline crossing)
- **Indian Ocean**: 55°E to 90°E, -12°S to 2°N  
- **Atlantic Ocean**: Western Atlantic (existing data)

## Quick Start

### Prerequisites
- Python 3.8+ installed
- Internet connection for downloading dependencies

### Installation
1. **Clone or download the project** to your computer
2. **Open terminal/command prompt** in the project directory
3. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   
   # Activate virtual environment
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Project
1. **Basic usage**:
   ```bash
   python main.py
   ```
2. **Test global mapping capabilities**:
   ```bash
   python test_global_mapping.py
   ```
3. **Explore the interactive demo**:
   - Open `dateline_demo.ipynb` in VS Code or Jupyter
   - Run cells to see dateline crossing demonstrations
   - See [JUPYTER_NOTEBOOK_GUIDE.md](JUPYTER_NOTEBOOK_GUIDE.md) for detailed instructions

### Expected Output
- `output/tropical_cyclone_map.html` - Interactive web map
- `output/tropical_cyclone_map_static.png` - High-resolution static map
- `output/data_table.png` - Data summary table
- Various GeoJSON files for data exchange

### For Detailed Setup
📖 **New to Python or need detailed setup?** → See [`STUDENT_SETUP_GUIDE.md`](STUDENT_SETUP_GUIDE.md)  
🔧 **Want to configure the project?** → See [`CONFIG_GUIDE.md`](CONFIG_GUIDE.md)  
📚 **Want to learn how it works?** → See [`TUTORIAL.md`](TUTORIAL.md)  
⚙️ **Need technical details?** → See [`TECHNICAL_DOCUMENTATION.md`](TECHNICAL_DOCUMENTATION.md)  
🖥️ **Having environment issues?** → See [`ENVIRONMENT_SETUP.md`](ENVIRONMENT_SETUP.md)  
📓 **Want to use the interactive notebook?** → See [`JUPYTER_NOTEBOOK_GUIDE.md`](JUPYTER_NOTEBOOK_GUIDE.md)

## Features

### Interactive Maps (Folium)
- **Layer Controls** - Show/hide different data layers
- **Interactive Popups** - Detailed information on click
- **Multiple Tile Layers** - Different map backgrounds
- **Measurement Tools** - Distance and area calculation
- **Fullscreen Mode** - Professional presentation capability
- **Responsive Design** - Works on various screen sizes

### Static Maps (Matplotlib/Cartopy)
- **High Resolution** - 300 DPI output suitable for publications
- **Professional Styling** - Clean, publication-ready appearance
- **Configurable Grid** - Customizable latitude/longitude spacing
- **Comprehensive Legend** - Visual representation of all data types
- **Data Attribution** - Professional source citations
- **Dateline Handling** - Advanced coordinate system management

### Data Processing
- **Real Data Support** - NOAA HURDAT2 storm data, AIS ship data
- **Sample Data** - Built-in sample data for testing
- **Multiple Formats** - CSV, GeoJSON, and more
- **Error Handling** - Graceful fallback from real to sample data
- **Coordinate Validation** - Ensures data integrity across systems

### Interactive Learning
- **Jupyter Notebook** - Interactive demonstrations of dateline crossing
- **Educational Content** - Learn about coordinate systems and mapping challenges
- **Code Examples** - Runnable examples you can modify and experiment with
- **Visual Comparisons** - See correct vs. incorrect approaches side-by-side

## Learning Objectives

This project demonstrates:
- **Geographic Data Processing** - pandas, geopandas, coordinate systems
- **Web Mapping** - Folium, Leaflet.js, interactive visualizations
- **Static Mapping** - Matplotlib, Cartopy, publication-quality maps
- **Data Visualization** - Best practices for geospatial data
- **File Format Conversions** - CSV to GeoJSON, data validation
- **Modular Architecture** - Clean code organization and reusability
- **Global Mapping** - Automatic adaptation to any geographic region
- **Dateline Crossing** - Advanced handling of International Date Line challenges

## Documentation

- **TUTORIAL.md** - Step-by-step tutorial for learning the project
- **STUDENT_SETUP_GUIDE.md** - Complete setup instructions for students
- **ENVIRONMENT_SETUP.md** - Detailed environment setup for Windows, macOS, and Linux
- **TECHNICAL_DOCUMENTATION.md** - Detailed technical implementation
- **CONFIG_GUIDE.md** - How to configure storm and map settings
- **JUPYTER_NOTEBOOK_GUIDE.md** - Complete guide for using the interactive Jupyter notebook
- **dateline_demo.ipynb** - Interactive Jupyter notebook demonstrating dateline crossing
- **test_global_mapping.py** - Demonstrates global mapping capability

## Usage Examples

```python
# The system automatically adapts to any geographic data, including dateline crossing
pacific_data = load_pacific_ship_data()  # May cross 180° longitude
pacific_storms = load_pacific_storm_data()  # Typhoons often cross dateline

# Maps will automatically detect dateline crossing and handle appropriately
map_creator.create_complete_map(ship_geojson=pacific_data, storm_geojson=pacific_storms)
static_mapper.create_complete_static_map(ship_geojson=pacific_data, storm_geojson=pacific_storms)
```

## Output Files

- **Interactive Map**: `output/tropical_cyclone_map.html`
- **Static Map**: `output/tropical_cyclone_map_static.png`
- **Data Table**: `output/data_table.png`
- **GeoJSON Data**: Ship and storm track data files
- **Test Maps**: Pacific and Indian Ocean demonstration maps 