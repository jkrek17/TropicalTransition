import folium
from folium import plugins
import json
import os
import sys
from src.utils import transform_geojson_to_360, detect_dateline_crossing

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Longitude System Logic for Interactive Maps (Folium):
# -------------------------------------------------------------
# If dateline crossing is detected (track crosses ±180°):
#   - All data (ship and storm) is transformed to 0–360 longitude for bounds/center calculations.
#   - Folium/Leaflet.js can handle 0-360° coordinates directly - no conversion needed!
# If no dateline crossing:
#   - All data and plotting use standard -180–180 longitude.
# The transformation is applied once before plotting, and all plotting uses the correct system for Folium.

class MapCreator:
    """Creates interactive web maps for tropical cyclone and ship track visualization."""
    
    def __init__(self):
        self.map_obj = None
        self.western_atlantic_bounds = (20.0, 45.0, -85.0, -50.0)
    
    def calculate_map_center_and_zoom(self, ship_geojson=None, storm_geojson=None):
        """
        Calculate optimal center coordinates and zoom level from data.
        
        Args:
            ship_geojson (dict): GeoJSON data for ship tracks
            storm_geojson (dict): GeoJSON data for storm track
            
        Returns:
            tuple: (center_lat, center_lon, zoom_start)
        """
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
            # Detect dateline crossing
            dateline_crossing = (min(all_lons) < 0 and max(all_lons) > 0) or (min(all_lons) < 180 and max(all_lons) > 180)
            
            if dateline_crossing:
                print(f"   Debug: Dateline crossing detected in interactive map data")
                # For dateline crossing with 0-360 data, calculate center in 0-360 system
                # Folium can handle 0-360° coordinates directly
                center_lon = (min(all_lons) + max(all_lons)) / 2
                center_lat = (min(all_lats) + max(all_lats)) / 2
                
                # Calculate zoom level based on 0-360 extent
                lon_range_0360 = max(all_lons) - min(all_lons)
                lat_range = max(all_lats) - min(all_lats)
                max_range = max(lon_range_0360, lat_range)
                
                print(f"   Debug: Dateline crossing map center: ({center_lat}, {center_lon}), range: {max_range}, all_lons: {all_lons[:5]}..., all_lats: {all_lats[:5]}...")
            else:
                # Standard calculation for non-dateline crossing data
                center_lon = (min(all_lons) + max(all_lons)) / 2
                center_lat = (min(all_lats) + max(all_lats)) / 2
                
                # Calculate zoom level based on data extent
                lon_range = max(all_lons) - min(all_lons)
                lat_range = max(all_lats) - min(all_lats)
                max_range = max(lon_range, lat_range)
                
                print(f"   Debug: Standard map center: ({center_lat}, {center_lon}), range: {max_range}")
            
            # Determine zoom level based on extent
            if max_range > 100:
                zoom_start = 3  # Very wide view
            elif max_range > 50:
                zoom_start = 4
            elif max_range > 20:
                zoom_start = 5
            elif max_range > 10:
                zoom_start = 6
            elif max_range > 5:
                zoom_start = 7
            elif max_range > 2:
                zoom_start = 8
            else:
                zoom_start = 9  # Close view
                
            return center_lat, center_lon, zoom_start
        
        # Default values if no data - use basin-specific settings
        basin_center = config.BASIN_SETTINGS[config.STORM_BASIN]["center"]
        basin_zoom = config.BASIN_SETTINGS[config.STORM_BASIN]["zoom"]
        return basin_center[0], basin_center[1], basin_zoom
    
    def create_base_map(self, center_lat=None, center_lon=None, zoom_start=None):
        """
        Create a base map centered on the configured basin.
        
        Args:
            center_lat (float): Center latitude (uses basin default if None)
            center_lon (float): Center longitude (uses basin default if None)
            zoom_start (int): Initial zoom level (uses basin default if None)
            
        Returns:
            folium.Map: Base map object
        """
        # Use basin-specific defaults if not provided
        if center_lat is None or center_lon is None or zoom_start is None:
            basin_center = config.BASIN_SETTINGS[config.STORM_BASIN]["center"]
            basin_zoom = config.BASIN_SETTINGS[config.STORM_BASIN]["zoom"]
            center_lat = center_lat or basin_center[0]
            center_lon = center_lon or basin_center[1]
            zoom_start = zoom_start or basin_zoom
        
        # Create base map with modern tile layer
        self.map_obj = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_start,
            tiles='CartoDB positron',  # Clean, modern background
            control_scale=True
        )
        
        # Add additional tile layers
        folium.TileLayer(
            tiles='CartoDB dark_matter',
            name='Dark Theme',
            overlay=False,
            control=True
        ).add_to(self.map_obj)
        
        folium.TileLayer(
            tiles='OpenStreetMap',
            name='OpenStreetMap',
            overlay=False,
            control=True
        ).add_to(self.map_obj)
        
        folium.TileLayer(
            tiles='https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png',
            attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>.',
            name='Terrain',
            overlay=False,
            control=True
        ).add_to(self.map_obj)
        
        return self.map_obj
    
    def add_ship_tracks(self, ship_geojson, layer_name="Ship Tracks"):
        """
        Add ship tracks to the map.
        
        Args:
            ship_geojson (dict): GeoJSON data for ship tracks
            layer_name (str): Name for the layer control
        """
        if not ship_geojson or 'features' not in ship_geojson:
            print("No valid ship data to add to map")
            return
        
        # Create a feature group for ship data
        ship_layer = folium.FeatureGroup(name=layer_name)
        
        for feature in ship_geojson['features']:
            if feature['geometry']['type'] == 'LineString':
                # Add ship track lines
                # GeoJSON uses [lon, lat] but Folium expects [lat, lon]
                coords = feature['geometry']['coordinates']
                
                # Detect if this track crosses the dateline
                track_lons = [coord[0] for coord in coords]
                dateline_crossing = (min(track_lons) < 0 and max(track_lons) > 0) or (min(track_lons) < 180 and max(track_lons) > 180)
                
                if dateline_crossing:
                    print(f"   Debug: Ship track crosses dateline, using 0-360° coordinates directly")
                    # For dateline crossing with 0-360 data, Folium can handle it directly
                    # No conversion needed - use 0-360° coordinates as-is
                    folium_coords = []
                    for coord in coords:
                        lon, lat = coord
                        # Use 0-360° coordinates directly - Folium handles them perfectly
                        folium_coords.append([lat, lon])
                    print(f'DEBUG: Initial folium_coords for {feature["properties"]["vessel_name"]}: {folium_coords[:5]}...')
                    
                    folium_coords = self._adjust_lons_for_shortest_path(folium_coords)
                    print(f'DEBUG: Adjusted folium_coords for {feature["properties"]["vessel_name"]}: {folium_coords[:5]}...')
                    
                    vessel_name = feature['properties']['vessel_name']
                    vessel_type = feature['properties']['vessel_type']
                    
                    # Create popup content
                    start_lat, start_lon = folium_coords[0][0], folium_coords[0][1]
                    end_lat, end_lon = folium_coords[-1][0], folium_coords[-1][1]
                    # Display coordinates in 0-360° format (the actual coordinates being used)
                    start_lon_disp = start_lon
                    end_lon_disp = end_lon
                    popup_content = f"""
                    <div style="width: 200px;">
                        <h4>🚢 {vessel_name}</h4>
                        <p><strong>Type:</strong> {vessel_type}</p>
                        <p><strong>Track:</strong> Ship Route (Crosses Dateline)</p>
                        <p><strong>Coordinates:</strong> {len(folium_coords)} points</p>
                        <p><strong>Start:</strong> {start_lon_disp:.4f}°E, {start_lat:.4f}°N</p>
                        <p><strong>End:</strong> {end_lon_disp:.4f}°E, {end_lat:.4f}°N</p>
                    </div>
                    """
                    
                    # Get track color
                    track_color = feature['properties'].get('track_color', 'blue')
                    
                    # Add track line (single continuous line)
                    folium.PolyLine(
                        locations=folium_coords,
                        color=track_color,
                        weight=3,
                        opacity=0.8,
                        popup=folium.Popup(popup_content, max_width=300),
                        no_clip=True
                    ).add_to(ship_layer)
                else:
                    # Standard handling for non-dateline crossing tracks
                    folium_coords = []
                    for coord in coords:
                        lon, lat = coord
                        # Use coordinates directly - Folium handles both -180/+180 and 0-360° systems
                        folium_coords.append([lat, lon])
                    print(f'DEBUG: Initial folium_coords for {feature["properties"]["vessel_name"]}: {folium_coords[:5]}...')
                    
                    folium_coords = self._adjust_lons_for_shortest_path(folium_coords)
                    print(f'DEBUG: Adjusted folium_coords for {feature["properties"]["vessel_name"]}: {folium_coords[:5]}...')
                    
                    vessel_name = feature['properties']['vessel_name']
                    vessel_type = feature['properties']['vessel_type']
                    
                    # Create popup content
                    start_lat, start_lon = folium_coords[0][0], folium_coords[0][1]
                    end_lat, end_lon = folium_coords[-1][0], folium_coords[-1][1]
                    # Display coordinates as they are (consistent with data format)
                    start_lon_disp = start_lon
                    end_lon_disp = end_lon
                    popup_content = f"""
                    <div style="width: 200px;">
                        <h4>🚢 {vessel_name}</h4>
                        <p><strong>Type:</strong> {vessel_type}</p>
                        <p><strong>Track:</strong> Ship Route</p>
                        <p><strong>Coordinates:</strong> {len(folium_coords)} points</p>
                        <p><strong>Start:</strong> {start_lon_disp:.4f}°E, {start_lat:.4f}°N</p>
                        <p><strong>End:</strong> {end_lon_disp:.4f}°E, {end_lat:.4f}°N</p>
                    </div>
                    """
                    
                    # Get track color
                    track_color = feature['properties'].get('track_color', 'blue')
                    
                    # Add track line
                    folium.PolyLine(
                        locations=folium_coords,
                        color=track_color,
                        weight=3,
                        opacity=0.8,
                        popup=folium.Popup(popup_content, max_width=300),
                        no_clip=True
                    ).add_to(ship_layer)
            
            elif feature['geometry']['type'] == 'Point':
                # Add ship position markers
                # GeoJSON uses [lon, lat] but Folium expects [lat, lon]
                coords = feature['geometry']['coordinates']
                lon, lat = coords
                # Convert 0-360 to -180 to 180 for Folium
                if lon > 180:
                    lon = lon - 360
                folium_coords = [lat, lon]
                
                props = feature['properties']
                
                # Create popup content
                lon_disp = lon + 360 if lon < 0 else lon
                popup_content = f"""
                <div style="width: 200px;">
                    <h4>🚢 {props['vessel_name']}</h4>
                    <p><strong>Type:</strong> {props['vessel_type']}</p>
                    <p><strong>Speed:</strong> {props['speed_knots']} knots</p>
                    <p><strong>Heading:</strong> {props['heading_degrees']}°</p>
                    <p><strong>Time:</strong> {props['timestamp'][:19]}</p>
                    <p><strong>Position:</strong> {lon_disp:.4f}°E, {lat:.4f}°N</p>
                </div>
                """
                
                # Create custom ship icon
                ship_icon = folium.Icon(
                    color='blue',
                    icon='ship',
                    prefix='fa'
                )
                
                # Add ship marker
                folium.Marker(
                    location=folium_coords,
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=ship_icon,
                    tooltip=f"🚢 {props['vessel_name']}"
                ).add_to(ship_layer)
        
        ship_layer.add_to(self.map_obj)
    
    def add_storm_track(self, storm_geojson, layer_name="Storm Track"):
        """
        Add tropical cyclone track to the map.
        
        Args:
            storm_geojson (dict): GeoJSON data for storm track
            layer_name (str): Name for the layer control
        """
        if not storm_geojson or 'features' not in storm_geojson:
            print("No valid storm data to add to map")
            return
        
        # Create a feature group for storm data
        storm_layer = folium.FeatureGroup(name=layer_name)
        
        for feature in storm_geojson['features']:
            if feature['geometry']['type'] == 'LineString':
                # Add storm track line
                # GeoJSON uses [lon, lat] but Folium expects [lat, lon]
                coords = feature['geometry']['coordinates']
                
                # Detect if this track crosses the dateline
                track_lons = [coord[0] for coord in coords]
                dateline_crossing = (min(track_lons) < 0 and max(track_lons) > 0) or (min(track_lons) < 180 and max(track_lons) > 180)
                
                if dateline_crossing:
                    print(f"   Debug: Storm track crosses dateline, handling for Folium")
                    # For dateline crossing with 0-360 data, we need to handle this differently
                    # Keep the data in 0-360 format but adjust for Folium display
                    folium_coords = []
                    for coord in coords:
                        lon, lat = coord
                        # Use 0-360° coordinates directly - Folium handles them perfectly
                        folium_coords.append([lat, lon])
                    print(f'DEBUG: Initial folium_coords for {feature["properties"]["storm_name"]}: {folium_coords[:5]}...')
                    
                    folium_coords = self._adjust_lons_for_shortest_path(folium_coords)
                    print(f'DEBUG: Adjusted folium_coords for {feature["properties"]["storm_name"]}: {folium_coords[:5]}...')
                    
                    storm_name = feature['properties']['storm_name']
                    year = feature['properties']['year']
                    
                    # Create popup content
                    start_lat, start_lon = folium_coords[0][0], folium_coords[0][1]
                    end_lat, end_lon = folium_coords[-1][0], folium_coords[-1][1]
                    # Display coordinates in 0-360° format (the actual coordinates being used)
                    start_lon_disp = start_lon
                    end_lon_disp = end_lon
                    popup_content = f"""
                    <div style="width: 200px;">
                        <h4>🌪️ {storm_name} ({year})</h4>
                        <p><strong>Track:</strong> Storm Path (Crosses Dateline)</p>
                        <p><strong>Type:</strong> Tropical Storm</p>
                        <p><strong>Coordinates:</strong> {len(folium_coords)} points</p>
                        <p><strong>Start:</strong> {start_lon_disp:.4f}°E, {start_lat:.4f}°N</p>
                        <p><strong>End:</strong> {end_lon_disp:.4f}°E, {end_lat:.4f}°N</p>
                    </div>
                    """
                    
                    # Add track line (single continuous line)
                    folium.PolyLine(
                        locations=folium_coords,
                        color='red',
                        weight=4,
                        opacity=0.9,
                        popup=folium.Popup(popup_content, max_width=300),
                        no_clip=True
                    ).add_to(storm_layer)
                else:
                    # Standard handling for non-dateline crossing tracks
                    folium_coords = []
                    for coord in coords:
                        lon, lat = coord
                        # Use coordinates directly - Folium handles both -180/+180 and 0-360° systems
                        folium_coords.append([lat, lon])
                    print(f'DEBUG: Initial folium_coords for {feature["properties"]["storm_name"]}: {folium_coords[:5]}...')
                    
                    folium_coords = self._adjust_lons_for_shortest_path(folium_coords)
                    print(f'DEBUG: Adjusted folium_coords for {feature["properties"]["storm_name"]}: {folium_coords[:5]}...')
                    
                    storm_name = feature['properties']['storm_name']
                    year = feature['properties']['year']
                    
                    # Create popup content
                    start_lat, start_lon = folium_coords[0][0], folium_coords[0][1]
                    end_lat, end_lon = folium_coords[-1][0], folium_coords[-1][1]
                    # Display coordinates as they are (consistent with data format)
                    start_lon_disp = start_lon
                    end_lon_disp = end_lon
                    popup_content = f"""
                    <div style="width: 200px;">
                        <h4>🌪️ {storm_name} ({year})</h4>
                        <p><strong>Track:</strong> Storm Path</p>
                        <p><strong>Type:</strong> Tropical Storm</p>
                        <p><strong>Coordinates:</strong> {len(folium_coords)} points</p>
                        <p><strong>Start:</strong> {start_lon_disp:.4f}°E, {start_lat:.4f}°N</p>
                        <p><strong>End:</strong> {end_lon_disp:.4f}°E, {end_lat:.4f}°N</p>
                    </div>
                    """
                    
                    # Add track line with storm styling
                    folium.PolyLine(
                        locations=folium_coords,
                        color='red',
                        weight=4,
                        opacity=0.9,
                        popup=folium.Popup(popup_content, max_width=300),
                        no_clip=True
                    ).add_to(storm_layer)
            
            elif feature['geometry']['type'] == 'Point':
                # Add storm position markers
                # GeoJSON uses [lon, lat] but Folium expects [lat, lon]
                coords = feature['geometry']['coordinates']
                lon, lat = coords
                # Use coordinates directly - Folium handles both -180/+180 and 0-360° systems
                folium_coords = [lat, lon]
                
                props = feature['properties']
                
                # Create popup content
                lon_disp = lon
                popup_content = f"""
                <div style="width: 200px;">
                    <h4>🌪️ {props['storm_name']} ({props.get('year', '')})</h4>
                    <p><strong>Wind:</strong> {props.get('wind_speed', '')} mph</p>
                    <p><strong>Pressure:</strong> {props.get('pressure', '')} mb</p>
                    <p><strong>Status:</strong> {props.get('status', '')}</p>
                    <p><strong>Time:</strong> {props.get('datetime', '')}</p>
                    <p><strong>Position:</strong> {lon_disp:.4f}°E, {lat:.4f}°N</p>
                </div>
                """
                
                # Determine icon color based on storm intensity
                if props['wind_speed'] >= 74:
                    icon_color = 'red'  # Hurricane
                    icon_name = 'tornado'
                elif props['wind_speed'] >= 39:
                    icon_color = 'orange'  # Tropical Storm
                    icon_name = 'cloud-rain'
                else:
                    icon_color = 'yellow'  # Tropical Depression
                    icon_name = 'cloud'
                
                # Create custom storm icon
                storm_icon = folium.Icon(
                    color=icon_color,
                    icon=icon_name,
                    prefix='fa'
                )
                
                # Add storm marker
                folium.Marker(
                    location=folium_coords,
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=storm_icon,
                    tooltip=f"🌪️ {props['storm_name']}"
                ).add_to(storm_layer)
        
        storm_layer.add_to(self.map_obj)
    
    def add_legend(self):
        """Add a custom legend to the map using configuration settings."""
        # Get legend position from configuration
        legend_pos = config.LEGEND_CORNER_POSITIONS[config.LEGEND_POSITION]['folium']
        
        # Build position style string
        position_style = f"position: fixed; width: 200px; height: 200px; "
        position_style += f"background-color: white; border:2px solid grey; z-index:9999; "
        position_style += f"font-size:{config.LEGEND_FONTSIZE}px; padding: 10px; "
        
        # Add corner positioning
        for pos, value in legend_pos.items():
            position_style += f"{pos}: {value}; "
        
        legend_html = f'''
        <div style="{position_style}">
        <h4>Map Legend</h4>
        <p><i class="fa fa-ship" style="color:blue"></i> Ship Position</p>
        <p><i class="fa fa-minus" style="color:blue"></i> Ship Track</p>
        <p><i class="fa fa-tornado" style="color:red"></i> Hurricane</p>
        <p><i class="fa fa-cloud-rain" style="color:orange"></i> Tropical Storm</p>
        <p><i class="fa fa-cloud" style="color:yellow"></i> Tropical Depression</p>
        <p><i class="fa fa-minus" style="color:red"></i> Storm Track</p>
        </div>
        '''
        
        self.map_obj.get_root().html.add_child(folium.Element(legend_html))
    
    def add_measurement_tools(self):
        """Add measurement tools to the map."""
        # Add measure control
        measure = plugins.MeasureControl(
            position='topleft',
            primary_length_unit='miles',
            secondary_length_unit='kilometers',
            primary_area_unit='sqmiles',
            secondary_area_unit='acres'
        )
        self.map_obj.add_child(measure)
    
    def add_fullscreen_button(self):
        """Add fullscreen button to the map."""
        plugins.Fullscreen(
            position='topleft',
            title='Expand me',
            title_cancel='Exit me',
            force_separate_button=True
        ).add_to(self.map_obj)
    
    def add_minimap(self):
        """Add a minimap to the main map."""
        minimap = plugins.MiniMap(
            tile_layer='CartoDB positron',
            position='bottomright',
            width=150,
            height=150,
            collapsed_width=25,
            collapsed_height=25
        )
        self.map_obj.add_child(minimap)
    
    def add_coordinate_readout(self):
        """Add a coordinate readout to the map."""
        # Create HTML for coordinate display
        coordinate_html = '''
        <div id="coordinate-display" style="position: fixed; 
                    top: 10px; right: 10px; width: 200px; height: 100px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px; font-family: monospace;">
        <h4>Coordinates</h4>
        <p>Click on map to see coordinates</p>
        <p id="lat-lon">Lat: --, Lon: --</p>
        </div>
        '''
        
        # Add JavaScript for coordinate tracking
        coordinate_js = '''
        <script>
        var map = document.querySelector('#map');
        var coordDisplay = document.getElementById('lat-lon');
        
        map.addEventListener('click', function(e) {
            var lat = e.latlng.lat.toFixed(4);
            var lon = e.latlng.lng.toFixed(4);
            coordDisplay.innerHTML = 'Lat: ' + lat + ', Lon: ' + lon;
        });
        </script>
        '''
        
        # Add the coordinate display to the map
        self.map_obj.get_root().html.add_child(folium.Element(coordinate_html))
        self.map_obj.get_root().html.add_child(folium.Element(coordinate_js))
    
    def save_map(self, output_file="output/tropical_cyclone_map.html"):
        """
        Save the map to an HTML file.
        
        Args:
            output_file (str): Output file path
        """
        try:
            # Ensure output directory exists (only if there's a directory path)
            dir_path = os.path.dirname(output_file)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            # Save the map
            self.map_obj.save(output_file)
            print(f"Map saved to {output_file}")
            return output_file
        except Exception as e:
            print(f"Error saving map: {e}")
            return None
    
    def create_complete_map(self, ship_geojson=None, storm_geojson=None, output_file="output/tropical_cyclone_map.html"):
        """
        Create a complete interactive map with all features.
        
        Longitude System Consistency:
        - If dateline crossing is detected, all data is transformed to 0–360 for bounds/center calculations.
        - Folium/Leaflet.js handles 0-360° coordinates directly - no conversion needed.
        - Otherwise, all data and plotting use -180–180.
        The transformation is applied ONCE here, and all plotting uses the correct system for Folium.
        """
        use_360 = False
        all_coords = []
        for geo in [ship_geojson, storm_geojson]:
            if geo and 'features' in geo:
                for feature in geo['features']:
                    geom = feature['geometry']
                    if geom['type'] == 'LineString':
                        all_coords.extend(geom['coordinates'])
                    elif geom['type'] == 'Point':
                        all_coords.append(geom['coordinates'])
        if detect_dateline_crossing(all_coords):
            use_360 = True
            if ship_geojson:
                ship_geojson = transform_geojson_to_360(ship_geojson)
                print(f'DEBUG: Transformed ship_geojson to 0-360: {ship_geojson}')
            if storm_geojson:
                storm_geojson = transform_geojson_to_360(storm_geojson)
                print(f'DEBUG: Transformed storm_geojson to 0-360: {storm_geojson}')
        # Calculate map center and zoom
        center_lat, center_lon, zoom_start = self.calculate_map_center_and_zoom(ship_geojson, storm_geojson)
        self.create_base_map(center_lat=center_lat, center_lon=center_lon, zoom_start=zoom_start)
        # Add ship tracks if available
        if ship_geojson:
            self.add_ship_tracks(ship_geojson)
        # Add storm track if available
        if storm_geojson:
            self.add_storm_track(storm_geojson)
        # Add legend, tools, etc. (if implemented)
        self.add_legend()
        self.add_measurement_tools()
        self.add_fullscreen_button()
        self.add_minimap()
        self.add_coordinate_readout()
        # Save the map
        return self.save_map(output_file)
    
    def _adjust_lons_for_shortest_path(self, coords):
        if not coords:
            return []
        adjusted = [coords[0]]
        for lat, lon in coords[1:]:
            prev_lon = adjusted[-1][1]
            candidates = [lon - 360, lon, lon + 360]
            best_lon = min(candidates, key=lambda c: abs(c - prev_lon))
            adjusted.append([lat, best_lon])
        return adjusted 