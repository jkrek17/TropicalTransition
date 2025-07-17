import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import json
from datetime import datetime
import config
from .utils import determine_storm_intensity, transform_geojson_to_360, detect_dateline_crossing

# Longitude System Logic for Static Maps:
# -------------------------------------------------------------
# If dateline crossing is detected (track crosses ±180°):
#   - All data (ship and storm) is transformed to 0–360 longitude.
#   - The map projection is set to PlateCarree(central_longitude=180).
#   - All plotting (lines, points, bounds) uses 0–360.
# If no dateline crossing:
#   - All data and map use standard -180–180 longitude.
#   - The map projection is PlateCarree(central_longitude=0).
# The transformation is applied once before plotting, and all plotting uses the same system as the map.

class MatplotlibMapper:
    """Creates static maps using matplotlib and cartopy for presentations."""

    def __init__(self):
        self.fig = None
        self.ax = None
        # Will be set dynamically based on data bounds
        self.western_atlantic_bounds = None

    def create_base_map(self, figsize=None, dpi=None, bounds=None):
        """
        Create a base map that automatically adapts to data location.

        Args:
            figsize (tuple): Figure size in inches (uses config if None)
            dpi (int): Resolution for high-quality output (uses config if None)
            bounds (tuple): Map bounds (lon_min, lon_max, lat_min, lat_max)

        Returns:
            tuple: (fig, ax) matplotlib figure and axes
        """
        # Use config values if not provided
        if figsize is None:
            figsize = config.FIGURE_SIZE
        if dpi is None:
            dpi = config.FIGURE_DPI

        # Set map extent - use provided bounds or default
        if bounds:
            self.western_atlantic_bounds = bounds
        elif self.western_atlantic_bounds:
            pass  # Use existing bounds
        else:
            # Default bounds for Western Atlantic (fallback)
            self.western_atlantic_bounds = config.DEFAULT_BOUNDS

        # Check for dateline crossing and create appropriate map
        lon_min, lon_max, lat_min, lat_max = self.western_atlantic_bounds

        # Detect if data crosses the dateline
        dateline_crossing = (lon_min < 0 and lon_max > 0) or (lon_min < 180 and lon_max > 180)

        if dateline_crossing:
            print(f"   Debug: Dateline crossing detected, using 0-360 system with central_longitude=180")
            # For dateline crossing, use 0-360 system with central_longitude=180
            self.fig, self.ax = plt.subplots(
                figsize=figsize,
                subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)},
                dpi=dpi
            )

            # Calculate dynamic extent based on data bounds
            # The bounds are already in 0-360 format from calculate_bounds_from_data
            extent_lon_min = max(lon_min, 120)  # Don't go below 120° to avoid wrapping
            extent_lon_max = min(lon_max, 240)  # Don't go above 240° to avoid wrapping

            # If the data range is too wide, center it around the middle
            if extent_lon_max - extent_lon_min > 120:
                center_lon = (extent_lon_min + extent_lon_max) / 2
                extent_lon_min = center_lon - 60
                extent_lon_max = center_lon + 60
                print(f"   Debug: Data range too wide, centering around {center_lon}°")

            extent_lat_min = max(lat_min - 5, -90)  # Add padding but don't exceed poles
            extent_lat_max = min(lat_max + 5, 90)

            self.ax.set_extent((extent_lon_min, extent_lon_max, extent_lat_min, extent_lat_max), crs=ccrs.PlateCarree())
            print(f"   Debug: Set dynamic 0-360 extent for dateline crossing: ({extent_lon_min}, {extent_lon_max}, {extent_lat_min}, {extent_lat_max})")
        else:
            # Standard extent for non-dateline crossing data
            self.fig, self.ax = plt.subplots(
                figsize=figsize,
                subplot_kw={'projection': ccrs.PlateCarree()},
                dpi=dpi
            )
            self.ax.set_extent(self.western_atlantic_bounds, crs=ccrs.PlateCarree())
            print(f"   Debug: Set standard extent: {self.western_atlantic_bounds}")

        # Add gridlines
        gl = self.ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                              linewidth=config.GRID_LINEWIDTH, color=config.GRID_COLOR, 
                              alpha=config.GRID_ALPHA, linestyle=config.GRID_LINESTYLE,
                              xlocs=np.arange(-180, 181, config.LONGITUDE_SPACING),
                              ylocs=np.arange(-90, 91, config.LATITUDE_SPACING))
        gl.top_labels = False
        gl.right_labels = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER

        # Add natural earth features
        self.ax.add_feature(cfeature.LAND, facecolor=config.LAND_COLOR, alpha=config.LAND_ALPHA)
        self.ax.add_feature(cfeature.OCEAN, facecolor=config.OCEAN_COLOR, alpha=config.OCEAN_ALPHA)
        self.ax.add_feature(cfeature.COASTLINE, linewidth=config.COASTLINE_WIDTH, color=config.COASTLINE_COLOR)
        self.ax.add_feature(cfeature.BORDERS, linewidth=config.BORDERS_WIDTH, color=config.BORDERS_COLOR)
        #self.ax.add_feature(cfeature.STATES, linewidth=config.STATES_WIDTH, color=config.STATES_COLOR)

        return self.fig, self.ax

    def calculate_bounds_from_data(self, ship_geojson=None, storm_geojson=None, padding=None):
        """
        Calculate map bounds from data with padding.
        Args:
            ship_geojson (dict): Ship track GeoJSON data
            storm_geojson (dict): Storm track GeoJSON data
            padding (float): Padding in degrees around data (uses config if None)
        Returns:
            tuple: (lon_min, lon_max, lat_min, lat_max)
        """
        if padding is None:
            padding = config.AUTO_BOUNDS_PADDING
        all_lons = []
        all_lats = []

        # Collect coordinates from ship data
        if ship_geojson and 'features' in ship_geojson:
            for feature in ship_geojson['features']:
                if feature['geometry']['type'] == 'Point':
                    coords = feature['geometry']['coordinates']
                    all_lons.append(coords[0])
                    all_lats.append(coords[1])
                elif feature['geometry']['type'] == 'LineString':
                    coords = feature['geometry']['coordinates']
                    for coord in coords:
                        all_lons.append(coord[0])
                        all_lats.append(coord[1])

        # Collect coordinates from storm data
        if storm_geojson and 'features' in storm_geojson:
            for feature in storm_geojson['features']:
                if feature['geometry']['type'] == 'Point':
                    coords = feature['geometry']['coordinates']
                    all_lons.append(coords[0])
                    all_lats.append(coords[1])
                elif feature['geometry']['type'] == 'LineString':
                    coords = feature['geometry']['coordinates']
                    for coord in coords:
                        all_lons.append(coord[0])
                        all_lats.append(coord[1])

        if all_lons and all_lats:
            # Check for dateline crossing
            dateline_crossing = (min(all_lons) < 0 and max(all_lons) > 0) or (min(all_lons) < 180 and max(all_lons) > 180)

            if dateline_crossing:
                print(f"   Debug: Dateline crossing detected in data, calculating bounds in 0-360 system")
                # Transform all longitudes to 0-360 for bounds calculation
                lons_0360 = []
                for lon in all_lons:
                    if lon < 0:
                        lons_0360.append(lon + 360)
                    else:
                        lons_0360.append(lon)

                lon_min_0360, lon_max_0360 = min(lons_0360), max(lons_0360)
                lat_min, lat_max = min(all_lats), max(all_lats)

                # Add padding
                lon_min_0360 -= padding
                lon_max_0360 += padding
                lat_min -= padding
                lat_max += padding

                # Convert back to [-180, 180] for the extent calculation
                # For central_longitude=180, we need to map 0-360 to the extent
                # The extent will be set to 120-240° in the 0-360 system
                print(f"   Debug: Data bounds in 0-360: ({lon_min_0360}, {lon_max_0360}, {lat_min}, {lat_max})")

                # Return bounds that will work with the 120-240° extent
                # We'll use the original bounds for the extent calculation
                return (lon_min_0360, lon_max_0360, lat_min, lat_max)
            else:
                # Standard bounds calculation for non-dateline crossing data
                lon_min, lon_max = min(all_lons), max(all_lons)
                lat_min, lat_max = min(all_lats), max(all_lats)

                # Add padding
                lon_min -= padding
                lon_max += padding
                lat_min -= padding
                lat_max += padding

                print(f"   Debug: Standard bounds: ({lon_min}, {lon_max}, {lat_min}, {lat_max})")
                return (lon_min, lon_max, lat_min, lat_max)

        # Default bounds if no data
        return config.DEFAULT_BOUNDS

    def add_ship_tracks(self, ship_geojson, ax=None):
        """
        Add ship tracks to the map.
        Args:
            ship_geojson (dict): GeoJSON data for ship tracks
            ax: matplotlib axes (uses self.ax if None)
        """
        import cartopy.crs as ccrs
        if ax is None:
            ax = self.ax

        # Check if we're using central_longitude=180 (dateline crossing case)
        use_360 = hasattr(ax.projection, 'central_longitude') and ax.projection.central_longitude == 180

        if not ship_geojson or 'features' not in ship_geojson:
            print("No valid ship data to add to map")
            return
        vessel_colors = {
            'Cargo': 'blue',
            'Tanker': 'darkblue',
            'Fishing': 'green',
            'Passenger': 'purple'
        }
        track_count = 0
        for feature in ship_geojson['features']:
            if feature['geometry']['type'] == 'LineString':
                track_count += 1
                coords = feature['geometry']['coordinates']
                vessel_name = feature['properties']['vessel_name']
                vessel_type = feature['properties']['vessel_type']
                lons = [coord[0] for coord in coords]
                lats = [coord[1] for coord in coords]

                # Transform to 0-360 if using central_longitude=180
                if use_360:
                    lons = [lon + 360 if lon < 0 else lon for lon in lons]

                print(f"   Debug: Plotting ship track #{track_count} {vessel_name}: {len(coords)} points, lons={lons[:3]}...{lons[-3:]}, lats={lats[:3]}...{lats[-3:]} (use_360={use_360})")

                track_color = feature['properties'].get('track_color', vessel_colors.get(vessel_type, 'blue'))

                # Add track with geodetic transformation
                ax.plot(lons, lats, 
                       color=track_color,
                       linewidth=2, alpha=0.8, 
                       transform=ccrs.Geodetic(),
                       label=f'{vessel_name}')

                print(f"   Added ship track #{track_count}: {vessel_name} in {track_color}")
        
        print(f"   Total ship tracks plotted: {track_count}")

        elif feature['geometry']['type'] == 'Point':
                coords = feature['geometry']['coordinates']
                props = feature['properties']
                vessel_name = props['vessel_name']
                vessel_type = props['vessel_type']
                track_color = props.get('track_color', vessel_colors.get(vessel_type, 'blue'))
                lon = coords[0]
                lat = coords[1]

                # Transform to 0-360 if using central_longitude=180
                if use_360:
                    lon = lon + 360 if lon < 0 else lon

                print(f"   Debug: Plotting ship point {vessel_name}: lon={lon}, lat={lat} (use_360={use_360})")

                # Add point marker
                ax.scatter(lon, lat, 
                          c=track_color,
                          s=20, alpha=0.7, 
                          transform=ccrs.Geodetic(),
                          zorder=5)

    def add_storm_track(self, storm_geojson, ax=None):
        """
        Add tropical cyclone track to the map.
        Args:
            storm_geojson (dict): GeoJSON data for storm track
            ax: matplotlib axes (uses self.ax if None)
        """
        import cartopy.crs as ccrs
        if ax is None:
            ax = self.ax

        # Check if we're using central_longitude=180 (dateline crossing case)
        use_360 = hasattr(ax.projection, 'central_longitude') and ax.projection.central_longitude == 180

        if not storm_geojson or 'features' not in storm_geojson:
            print("No valid storm data to add to map")
            return
        for feature in storm_geojson['features']:
            if feature['geometry']['type'] == 'LineString':
                coords = feature['geometry']['coordinates']
                storm_name = feature['properties']['storm_name']
                year = feature['properties']['year']
                lons = [coord[0] for coord in coords]
                lats = [coord[1] for coord in coords]

                # Transform to 0-360 if using central_longitude=180
                if use_360:
                    lons = [lon + 360 if lon < 0 else lon for lon in lons]

                print(f"   Debug: Plotting storm track {storm_name}: lons={lons[:3]}...{lons[-3:]}, lats={lats[:3]}...{lats[-3:]} (use_360={use_360})")
                ax.plot(lons, lats, color='red', linewidth=3, alpha=0.9, 
                       linestyle='-', label=f'{storm_name} ({year})', transform=ccrs.Geodetic())
            elif feature['geometry']['type'] == 'Point':
                coords = feature['geometry']['coordinates']
                props = feature['properties']
                wind_speed = props['wind_speed']
                intensity_info = determine_storm_intensity(wind_speed)
                marker_size = intensity_info['size']
                color = intensity_info['color']
                marker = intensity_info['marker']
                lon, lat = coords[0], coords[1]

                # Transform to 0-360 if using central_longitude=180
                if use_360:
                    lon = lon + 360 if lon < 0 else lon

                print(f"   Debug: Plotting storm point {props['storm_name']}: lon={lon}, lat={lat} (use_360={use_360})")
                ax.scatter(lon, lat, c=color, s=marker_size, marker=marker,
                          edgecolors='black', linewidth=2, alpha=0.9, zorder=6, transform=ccrs.Geodetic())

    def add_legend(self, ax=None):
        """
        Add a custom legend to the map.

        Args:
            ax: matplotlib axes (uses self.ax if None)
        """
        if ax is None:
            ax = self.ax

        # Create legend handles
        from matplotlib.lines import Line2D
        from matplotlib.patches import Patch

        legend_elements = [
            Line2D([0], [0], color='red', lw=3, label='Storm Track'),
            Line2D([0], [0], color='blue', lw=2, label='Ship Track'),
            Line2D([0], [0], marker='o', color='red', markersize=8, 
                   label='Hurricane (≥74 mph)', linestyle=''),
            Line2D([0], [0], marker='o', color='orange', markersize=8, 
                   label='Tropical Storm (39-73 mph)', linestyle=''),
            Line2D([0], [0], marker='o', color='yellow', markersize=8, 
                   label='Tropical Depression (<39 mph)', linestyle=''),
            Line2D([0], [0], marker='s', color='blue', markersize=8, 
                   label='Ship Position', linestyle='')
        ]

        # Use configuration for legend positioning
        legend_position = config.LEGEND_CORNER_POSITIONS[config.LEGEND_POSITION]['matplotlib']
        ax.legend(handles=legend_elements, loc=legend_position, 
                fontsize=config.LEGEND_FONTSIZE, framealpha=config.LEGEND_FRAME_ALPHA)

    def add_title_and_info(self, title="Tropical Cyclone and Ship Track Analysis", ax=None):
        """
        Add title and information to the map.

        Args:
            title (str): Map title
            ax: matplotlib axes (uses self.ax if None)
        """
        if ax is None:
            ax = self.ax

        # Add main title
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

        # Add subtitle with date
        current_date = datetime.now().strftime("%B %Y")
        ax.text(0.5, 0.02, f"Data Source: SeaVision CSV, NOAA Best Track | Generated: {current_date}", 
                transform=ax.transAxes, ha='center', fontsize=10, 
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

    def save_map(self, output_file="output/tropical_cyclone_map_static.png", 
                 dpi=300, bbox_inches='tight'):
        """
        Save the map to a high-quality image file.

        Args:
            output_file (str): Output file path
            dpi (int): Resolution for high-quality output
            bbox_inches (str): Bounding box setting

        Returns:
            str: Path to the saved file
        """
        try:
            import os
            # Ensure output directory exists (only if there's a directory path)
            dir_path = os.path.dirname(output_file)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            # Save the map
            self.fig.savefig(output_file, dpi=dpi, bbox_inches=bbox_inches, 
                           facecolor='white', edgecolor='none')
            print(f"Static map saved to {output_file}")
            return output_file
        except Exception as e:
            print(f"Error saving map: {e}")
            return None

    def create_complete_static_map(self, ship_geojson=None, storm_geojson=None, 
                                  output_file="output/tropical_cyclone_map_static.png", bounds=None):
        """
        Create a complete static map with all features.
        Longitude System Consistency:
        - Always use the original data in [-180, 180] longitude range.
        - Use geodetic transformation for all plotting to ensure correct great-circle lines.
        - Use safe extent for dateline crossing to ensure all data is visible.
        """
        # Calculate bounds from data if not provided
        if bounds is None:
            bounds = self.calculate_bounds_from_data(ship_geojson, storm_geojson)
            print(f"   Auto-calculated map bounds: {bounds}")
        # Create base map with calculated bounds
        self.create_base_map(bounds=bounds)
        # Add ship tracks if available
        if ship_geojson:
            print(f"   Debug: Adding ship tracks with geodetic transformation")
            self.add_ship_tracks(ship_geojson)
        # Add storm track if available
        if storm_geojson:
            print(f"   Debug: Adding storm track with geodetic transformation")
            self.add_storm_track(storm_geojson)
        # Add legend and title
        self.add_legend()
        self.add_title_and_info()
        # Save the map
        return self.save_map(output_file)