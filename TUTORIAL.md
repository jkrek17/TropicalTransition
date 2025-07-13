# Tropical Cyclone and Ship Track Visualization Project: Full Tutorial

> **Note**: If you're new to this project, please begin with `STUDENT_SETUP_GUIDE.md` for installation instructions.

## 1. Project Overview

This project visualizes tropical cyclone (storm) tracks and ship movements on both interactive web maps and static presentation maps. It uses real-world data from NOAA (for storms) and AIS/SeaVision (for ships). The project is modular, configurable, and demonstrates best practices in Python data science and mapping.

**Advanced Feature**: The project includes sophisticated handling of **dateline crossing** - one of the most challenging problems in weather data mapping.

---

## 2. Critical Challenge: Dateline Crossing

### The Problem

When tropical cyclones or ship tracks cross the International Date Line (180° longitude), traditional mapping approaches fail because:

- **Track Discontinuity**: Lines appear to "jump" from one side of the map to the other
- **Global Wrapping**: Maps show the entire globe instead of focusing on the data
- **Coordinate Confusion**: Longitudes switch from negative to positive values
- **Incorrect Distances**: Great-circle paths are not rendered correctly

### Our Solution

The project automatically detects and handles dateline crossing:

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

### Real-World Applications

This solution is essential for:
- **Pacific Typhoons**: Many cross the dateline during their lifecycle
- **Global Shipping**: Trans-Pacific voyages often cross 180° longitude
- **Climate Research**: Long-term storm tracking across ocean basins
- **Maritime Safety**: Accurate visualization of vessel movements

---

## 3. Project Structure

```
StudentProject/
│
├── src/                  # All main Python modules
│   ├── data_processor.py
│   ├── map_creator.py
│   ├── matplotlib_mapper.py
│   ├── nhc_data_downloader.py
│   └── utils.py
├── main.py               # Main entry point
├── config.py             # All map and data settings
├── requirements.txt      # Python dependencies
├── README.md
│
├── data/                 # Raw data (real ship track, HURDAT2)
│   ├── shiptrack1.csv
│   └── hurdat2_atlantic.txt
├── sample_data/          # Example ship data
│   └── sample_ship_data.csv
├── output/               # All generated files (maps, geojson, tables)
│   ├── tropical_cyclone_map.html
│   ├── tropical_cyclone_map_static.png
│   ├── real_ship_tracks.geojson
│   ├── fiona_2022_storm_track.geojson
│   └── data_table.png
├── tests/                # Test scripts
│   └── test_project.py
└── .gitignore
```

---

## 4. Key Technologies

- **Python**: Data processing, mapping, and automation
- **Pandas/GeoPandas**: Data wrangling and geospatial operations
- **Folium**: Interactive web maps (uses Leaflet.js)
- **Matplotlib/Cartopy**: High-quality static maps for presentations
- **NOAA HURDAT2**: Real storm data
- **AIS/SeaVision CSV**: Real ship track data
- **Advanced Cartopy**: Dateline crossing handling with coordinate system selection

---

## 5. How the Project Works

### a. Data Processing

- **Ship Data**: Reads either a sample or real ship track CSV, parses timestamps, coordinates, speed, and heading, and creates a GeoDataFrame.
- **Storm Data**: Uses either sample data or real NOAA HURDAT2 data (downloaded and parsed) for storm tracks.

### b. Dateline Detection and Handling

- **Automatic Detection**: Analyzes coordinate bounds to detect dateline crossing
- **Coordinate System Selection**: Chooses appropriate projection (-180/180 or 0/360)
- **Dynamic Extent Calculation**: Creates focused map bounds that avoid global wrapping
- **Coordinate Transformation**: Transforms coordinates only when needed for dateline crossing

### c. GeoJSON Creation

- Both ship and storm data are converted to GeoJSON format for easy mapping and sharing.

### d. Mapping

- **Interactive Map**: Uses Folium to create a web map with layers for ship tracks and storm tracks, custom icons, popups, and measurement tools.
- **Static Map**: Uses Matplotlib and Cartopy to create a high-resolution PNG map for offline use and presentations, with advanced dateline handling.
- **Data Table**: Generates a PNG image of a table summarizing the ship and storm data.

### e. Configuration

- All map appearance, data paths, and output settings are controlled in `config.py` for easy customization.

---

## 6. How to Run the Project

> **Note**: If you haven't set up Python and VS Code yet, please refer to `STUDENT_SETUP_GUIDE.md` first.

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Add your data**:
   - Place real ship track CSVs in `data/`
   - Place HURDAT2 storm data in `data/` (or let the downloader fetch it)

3. **Run the main script**:
   ```bash
   python main.py
   ```

4. **View results**:
   - Open `output/tropical_cyclone_map.html` in your browser for the interactive map
   - Use `output/tropical_cyclone_map_static.png` for presentations
   - Check `output/data_table.png` for a summary table

**Note**: The system will automatically detect if your data crosses the dateline and handle it appropriately.

---

## 7. What Each Module Does

- **main.py**: Orchestrates the workflow—loads data, processes it, creates maps and tables.
- **src/data_processor.py**: Loads and processes both sample and real ship data, and sample storm data.
- **src/nhc_data_downloader.py**: Downloads and parses real storm data from NOAA.
- **src/map_creator.py**: Builds the interactive Folium map.
- **src/matplotlib_mapper.py**: Builds the static Matplotlib/Cartopy map with advanced dateline handling and the data table.
- **src/utils.py**: Shared helper functions (coordinate parsing, GeoJSON saving, etc.)
- **config.py**: All settings for map appearance, data paths, and output files.

---

## 8. Key Learning Points

- **Data Wrangling**: How to clean and process real-world geospatial data.
- **Mapping**: How to create both interactive and static maps in Python.
- **Modular Design**: How to structure a Python project for clarity and reusability.
- **Configuration**: How to make a project easily customizable for different datasets or map styles.
- **Real Data Integration**: How to work with real NOAA and AIS datasets.
- **Advanced Cartopy**: How to handle dateline crossing and coordinate system selection.
- **Geospatial Challenges**: Understanding and solving common problems in weather data mapping.

---

## 9. How to Extend the Project

- Add more ship tracks or storms by placing new CSVs in the `data/` folder.
- Change map appearance or output settings in `config.py`.
- Add new map layers (e.g., ports, weather) by extending the mapping modules.
- Use the data table output for further analysis or reporting.
- Test with data that crosses the dateline to see the advanced handling in action.

---

## 10. Troubleshooting

- If you see errors about missing data, check that your CSV files are in the correct folder and formatted properly.
- If the map doesn't show expected data, check the GeoJSON files in `output/` for issues.
- For any Python errors, check the traceback for which module or data file is causing the problem.
- If tracks appear discontinuous, check if your data crosses the dateline - the system should handle this automatically.
- **For environment setup issues**, see [`ENVIRONMENT_SETUP.md`](ENVIRONMENT_SETUP.md) for comprehensive troubleshooting
- **For detailed troubleshooting**, see the expanded section in [`STUDENT_SETUP_GUIDE.md`](STUDENT_SETUP_GUIDE.md)

---

## 11. Summary

This project is a complete, real-world example of geospatial data science in Python. It demonstrates how to process, analyze, and visualize both ship and storm data using modern, modular, and configurable code. The result is a set of professional-quality maps and data products ready for analysis, presentation, or further research.

**Advanced Features**: The project includes sophisticated handling of dateline crossing, making it suitable for global weather data visualization and research.

---

## 📚 Additional Resources

- **`STUDENT_SETUP_GUIDE.md`**: Complete installation and setup instructions for students
- **`ENVIRONMENT_SETUP.md`**: Detailed environment setup for Windows, macOS, and Linux
- **`JUPYTER_NOTEBOOK_GUIDE.md`**: Complete guide for using the interactive Jupyter notebook
- **`README.md`**: Project overview and quick start
- **`TECHNICAL_DOCUMENTATION.md`**: Detailed technical implementation including dateline handling
- **`CONFIG_GUIDE.md`**: How to configure storm and map settings
- **`config.py`**: All customizable settings for maps and data processing

## 🎓 Learning Objectives

This project is designed to teach:
- Real-world data science workflows
- Geospatial data processing
- Interactive and static visualization
- Modular Python programming
- Configuration management
- Advanced cartographic challenges (dateline crossing)
- Weather data mapping best practices

The project includes both sample and real data, making it suitable for different skill levels and learning objectives.

---

**We encourage you to explore the code, experiment with new data, and test different map configurations to enhance your understanding of geospatial data science. Try testing with data that crosses the dateline to see the advanced handling in action!** 