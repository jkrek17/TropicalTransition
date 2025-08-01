import pandas as pd
import json
import geopandas as gpd
from shapely.geometry import Point, LineString
from datetime import datetime
import numpy as np
import os
import sys
from .utils import save_geojson, determine_storm_intensity

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class DataProcessor:
    """Handles processing of ship track and storm data for mapping applications."""
    
    def __init__(self):
        self.ship_data = None
        self.storm_data = None
        self.nhc_downloader = None
    
    def get_nhc_downloader(self):
        """Get or create NHC data downloader instance."""
        if self.nhc_downloader is None:
            from .nhc_data_downloader import NHCDataDownloader
            self.nhc_downloader = NHCDataDownloader(basin=config.STORM_BASIN)
        return self.nhc_downloader
    
    def load_storm_data_from_config(self):
        """
        Load storm data based on configuration settings.
        
        Returns:
            dict: GeoJSON feature collection for storm track, or None if not found
        """
        storm_name = config.STORM_NAME
        storm_year = config.STORM_YEAR
        storm_basin = config.STORM_BASIN
        
        print(f"🌪️ Loading storm data: {storm_name} ({storm_year}) from {storm_basin} basin")
        
        # Check if we should auto-download data
        if config.AUTO_DOWNLOAD_STORM_DATA:
            try:
                downloader = self.get_nhc_downloader()
                
                # Download and process storm data
                storm_geojson = downloader.download_and_process_storm(storm_name, storm_year)
                
                if storm_geojson:
                    print(f"✅ Successfully loaded {storm_name} ({storm_year}) from NOAA data")
                    return storm_geojson
                else:
                    print(f"⚠️  Could not find {storm_name} ({storm_year}) in NOAA data")
                    
            except Exception as e:
                print(f"❌ Error downloading storm data: {e}")
        
        # Fallback to sample data if configured
        if config.FALLBACK_TO_SAMPLE_DATA:
            print("📝 Using sample storm data as fallback")
            storm_geojson = self.create_sample_storm_data(storm_name, storm_year)
            
            # Save sample data with proper filename
            if storm_geojson:
                output_file = f"output/{storm_name.lower()}_{storm_year}_track.geojson"
                self.save_geojson(storm_geojson, output_file)
                print(f"💾 Saved sample track data to: {output_file}")
            
            return storm_geojson
        
        return None
    
    def search_storms_by_year(self, year):
        """
        Search for all storms in a given year.
        
        Args:
            year (int): Year to search for storms
            
        Returns:
            list: List of storm information dictionaries
        """
        try:
            downloader = self.get_nhc_downloader()
            
            # Download data if not already done
            if not downloader.raw_data:
                if not downloader.download_hurdat2_data():
                    return []
            
            # Parse data if not already done
            if not downloader.processed_storms:
                if not downloader.parse_hurdat2_data():
                    return []
            
            # Get storms for the specified year
            storms = downloader.list_storms_by_year(year)
            return storms
            
        except Exception as e:
            print(f"❌ Error searching storms for year {year}: {e}")
            return []
    
    def get_basin_bounds(self, basin=None):
        """
        Get map bounds for a specific basin.
        
        Args:
            basin (str, optional): Basin name. If None, uses config.STORM_BASIN
            
        Returns:
            tuple: (lon_min, lon_max, lat_min, lat_max)
        """
        if basin is None:
            basin = config.STORM_BASIN
        
        if basin in config.BASIN_SETTINGS:
            return config.BASIN_SETTINGS[basin]["bounds"]
        else:
            # Default to Atlantic bounds
            return config.BASIN_SETTINGS["Atlantic"]["bounds"]
    
    def get_basin_center(self, basin=None):
        """
        Get map center for a specific basin.
        
        Args:
            basin (str, optional): Basin name. If None, uses config.STORM_BASIN
            
        Returns:
            list: [latitude, longitude]
        """
        if basin is None:
            basin = config.STORM_BASIN
        
        if basin in config.BASIN_SETTINGS:
            return config.BASIN_SETTINGS[basin]["center"]
        else:
            # Default to Atlantic center
            return config.BASIN_SETTINGS["Atlantic"]["center"]
    
    def load_ship_data_from_csv(self, csv_file_path):
        """
        Load ship track data from SeaVision CSV file.
        
        Args:
            csv_file_path (str): Path to the CSV file containing ship data
            
        Returns:
            pandas.DataFrame: Processed ship data with geometry
        """
        try:
            # Read CSV file
            df = pd.read_csv(csv_file_path)
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Create geometry points from latitude and longitude
            geometry = [Point(lon, lat) for lon, lat in zip(df['longitude'], df['latitude'])]
            
            # Create GeoDataFrame
            gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
            
            # Add vessel-specific information
            gdf['vessel_id'] = gdf['vessel_name'].astype('category').cat.codes
            
            self.ship_data = gdf
            print(f"Loaded {len(gdf)} ship track points from {csv_file_path}")
            return gdf
            
        except Exception as e:
            print(f"Error loading ship data: {e}")
            return None
    
    def load_real_ship_data_from_csv(self, csv_file_path):
        """
        Load real ship track data from AIS CSV file.
        
        Args:
            csv_file_path (str): Path to the CSV file containing real ship data
            
        Returns:
            pandas.DataFrame: Processed ship data with geometry
        """
        try:
            # Read CSV file
            df = pd.read_csv(csv_file_path)
            
            # Convert TimeOfFix to datetime
            df['timestamp'] = pd.to_datetime(df['TimeOfFix'])
            
            # Rename columns to match our expected format
            df = df.rename(columns={
                'SOG': 'speed_knots',
                'Heading': 'heading_degrees'
            })
            
            # Add vessel information (using MMSI as vessel name for now)
            df['vessel_name'] = f"Vessel {df['MMSI'].iloc[0]}"
            df['vessel_type'] = 'Cargo'  # Default type
            
            # Create geometry points from latitude and longitude
            geometry = [Point(lon, lat) for lon, lat in zip(df['Longitude'], df['Latitude'])]
            
            # Create GeoDataFrame
            gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
            
            # Add vessel-specific information
            gdf['vessel_id'] = gdf['MMSI'].astype('category').cat.codes
            
            self.ship_data = gdf
            print(f"Loaded {len(gdf)} real ship track points from {csv_file_path}")
            print(f"Vessel MMSI: {df['MMSI'].iloc[0]}")
            print(f"Track duration: {df['timestamp'].min()} to {df['timestamp'].max()}")
            print(f"Track range: {df['Latitude'].min():.3f}°N to {df['Latitude'].max():.3f}°N, "
                  f"{df['Longitude'].min():.3f}°W to {df['Longitude'].max():.3f}°W")
            return gdf
            
        except Exception as e:
            print(f"Error loading real ship data: {e}")
            return None

    def load_multiple_ship_files_from_directory(self, data_dir="data"):
        """
        Load multiple ship track files from a directory.
        
        Args:
            data_dir (str): Directory containing ship track CSV files
            
        Returns:
            pandas.DataFrame: Combined ship data from all files
        """
        import glob
        import random
        
        all_ship_data = []
        
        # Find all CSV files in the data directory
        csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
        
        if not csv_files:
            print(f"No CSV files found in {data_dir} directory")
            return None
        
        print(f"Found {len(csv_files)} CSV files to process:")
        
        # Generate random colors for each file
        colors = self._generate_random_colors(len(csv_files))
        
        for i, csv_file in enumerate(csv_files):
            print(f"  Processing: {csv_file}")
            
            try:
                # Try to load as real ship data first
                # Handle files that start with "sep=," by skipping that line
                try:
                    df = pd.read_csv(csv_file)
                except:
                    # If that fails, try skipping the first line (in case of sep= header)
                    df = pd.read_csv(csv_file, skiprows=1)
                
                # Clean column names (remove any whitespace)
                df.columns = df.columns.str.strip()
                
                # Check if it's real ship data format (has MMSI, TimeOfFix, etc.)
                if 'MMSI' in df.columns and 'TimeOfFix' in df.columns:
                    # Real ship data format
                    df['timestamp'] = pd.to_datetime(df['TimeOfFix'])
                    df = df.rename(columns={
                        'SOG': 'speed_knots',
                        'Heading': 'heading_degrees'
                    })
                    df['vessel_name'] = f"Vessel {df['MMSI'].iloc[0]}"
                    df['vessel_type'] = 'Cargo'
                    geometry = [Point(lon, lat) for lon, lat in zip(df['Longitude'], df['Latitude'])]
                    
                elif 'MMSI' in df.columns and 'TimeOfFix' in df.columns and 'Longitude' in df.columns and 'Latitude' in df.columns:
                    # Real AIS data format with TimeOfFix
                    df['timestamp'] = pd.to_datetime(df['TimeOfFix'], format='%Y %b %d %H:%M:%S UTC', errors='coerce')
                    
                    # If that fails, try a more flexible parsing
                    if df['timestamp'].isna().all():
                        df['timestamp'] = pd.to_datetime(df['TimeOfFix'], errors='coerce')
                    
                    # If still failing, create default timestamps
                    if df['timestamp'].isna().all():
                        df['timestamp'] = pd.to_datetime('2022-01-01 00:00:00')
                    
                    # Rename columns to match our expected format
                    if 'SOG' in df.columns:
                        df = df.rename(columns={'SOG': 'speed_knots'})
                    if 'Heading' in df.columns:
                        df = df.rename(columns={'Heading': 'heading_degrees'})
                    
                    df['vessel_name'] = f"Vessel {df['MMSI'].iloc[0]}"
                    df['vessel_type'] = 'Cargo'
                    geometry = [Point(lon, lat) for lon, lat in zip(df['Longitude'], df['Latitude'])]
                    
                elif 'MMSI' in df.columns and any(col in df.columns for col in ['Longitude', 'Latitude', 'longitude', 'latitude']):
                    # Alternative real ship data format
                    if 'BaseDateTime' in df.columns:
                        df['timestamp'] = pd.to_datetime(df['BaseDateTime'])
                    elif 'DateTime' in df.columns:
                        df['timestamp'] = pd.to_datetime(df['DateTime'])
                    else:
                        # Create a default timestamp if none exists
                        df['timestamp'] = pd.to_datetime('2022-01-01 00:00:00')
                    
                    # Handle different longitude/latitude column names
                    if 'Longitude' in df.columns and 'Latitude' in df.columns:
                        lon_col, lat_col = 'Longitude', 'Latitude'
                    elif 'longitude' in df.columns and 'latitude' in df.columns:
                        lon_col, lat_col = 'longitude', 'latitude'
                    elif 'LON' in df.columns and 'LAT' in df.columns:
                        lon_col, lat_col = 'LON', 'LAT'
                    else:
                        print(f"    Skipping {csv_file}: Could not find longitude/latitude columns")
                        continue
                    
                    # Rename columns to match our expected format
                    if 'SOG' in df.columns:
                        df = df.rename(columns={'SOG': 'speed_knots'})
                    if 'Heading' in df.columns:
                        df = df.rename(columns={'Heading': 'heading_degrees'})
                    if 'COG' in df.columns:
                        df = df.rename(columns={'COG': 'heading_degrees'})
                    
                    df['vessel_name'] = f"Vessel {df['MMSI'].iloc[0]}"
                    df['vessel_type'] = 'Cargo'
                    geometry = [Point(lon, lat) for lon, lat in zip(df[lon_col], df[lat_col])]
                    
                elif 'vessel_name' in df.columns and 'timestamp' in df.columns:
                    # Sample ship data format
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    geometry = [Point(lon, lat) for lon, lat in zip(df['longitude'], df['latitude'])]
                    
                else:
                    print(f"    Skipping {csv_file}: Unknown format")
                    continue
                
                # Create GeoDataFrame
                gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
                
                # Add unique color for this file
                gdf['track_color'] = colors[i]
                
                # Add file source
                gdf['source_file'] = os.path.basename(csv_file)
                
                # Add unique file index to help with grouping
                gdf['file_index'] = i
                
                all_ship_data.append(gdf)
                print(f"    Loaded {len(gdf)} points from {csv_file}")
                
            except Exception as e:
                print(f"    Error loading {csv_file}: {e}")
                continue
        
        if not all_ship_data:
            print("No valid ship data files were loaded")
            return None
        
        # Combine all ship data
        combined_data = pd.concat(all_ship_data, ignore_index=True)
        
        self.ship_data = combined_data
        print(f"\nTotal loaded: {len(combined_data)} ship track points from {len(all_ship_data)} files")
        
        return combined_data

    def _generate_random_colors(self, num_colors):
        """
        Generate a list of random colors for ship tracks.
        
        Args:
            num_colors (int): Number of colors to generate
            
        Returns:
            list: List of color strings
        """
        import random
        
        # Base colors to ensure good visibility
        base_colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
            '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57',
            '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3', '#ff9f43'
        ]
        
        colors = []
        
        for i in range(num_colors):
            if i < len(base_colors):
                colors.append(base_colors[i])
            else:
                # Generate random colors for additional files
                r = random.randint(50, 255)
                g = random.randint(50, 255)
                b = random.randint(50, 255)
                colors.append(f'#{r:02x}{g:02x}{b:02x}')
        
        return colors
    
    def create_ship_tracks_geojson(self, ship_data=None):
        """
        Create GeoJSON features for ship tracks.
        
        Args:
            ship_data (GeoDataFrame, optional): Ship data to process
            
        Returns:
            dict: GeoJSON feature collection for ship tracks
        """
        if ship_data is None:
            ship_data = self.ship_data
            
        if ship_data is None:
            print("No ship data available")
            return None
        
        features = []
        
        # Group by vessel to create track lines - use source_file + vessel identifier for unique tracks
        if 'vessel_name' in ship_data.columns and 'source_file' in ship_data.columns:
            # Create unique vessel identifier combining source file and vessel name
            ship_data['unique_vessel_id'] = ship_data['source_file'] + '_' + ship_data['vessel_name'].astype(str)
            vessel_groups = ship_data.groupby('unique_vessel_id')
        elif 'MMSI' in ship_data.columns and 'source_file' in ship_data.columns:
            # For real data, group by source file + MMSI
            ship_data['unique_vessel_id'] = ship_data['source_file'] + '_' + ship_data['MMSI'].astype(str)
            vessel_groups = ship_data.groupby('unique_vessel_id')
        elif 'vessel_name' in ship_data.columns:
            vessel_groups = ship_data.groupby('vessel_name')
        else:
            # For real data, group by MMSI
            vessel_groups = ship_data.groupby('MMSI')
        
        for vessel_id, vessel_data in vessel_groups:
            vessel_data = vessel_data.sort_values('timestamp')
            
            # Create line geometry for track
            coords = [[point.x, point.y] for point in vessel_data.geometry]
            line_geometry = {
                "type": "LineString",
                "coordinates": coords
            }
            
            # Get vessel name for display
            if 'vessel_name' in vessel_data.columns:
                vessel_name = vessel_data['vessel_name'].iloc[0]
                # If we have source file info, include it for clarity
                if 'source_file' in vessel_data.columns:
                    source_file = vessel_data['source_file'].iloc[0]
                    vessel_name = f"{vessel_name} ({source_file})"
            else:
                vessel_name = f"Vessel {vessel_id}"
            
            # Get vessel type and color
            vessel_type = vessel_data.get('vessel_type', 'Unknown').iloc[0]
            track_color = vessel_data.get('track_color', '#1f77b4').iloc[0]  # Default blue
            source_file = vessel_data.get('source_file', 'unknown').iloc[0]
            
            # Create feature for track line
            track_feature = {
                "type": "Feature",
                "geometry": line_geometry,
                "properties": {
                    "vessel_name": vessel_name,
                    "vessel_type": vessel_type,
                    "track_type": "ship_track",
                    "track_color": track_color,
                    "source_file": source_file
                }
            }
            features.append(track_feature)
            
            # Create point features for each position
            for idx, row in vessel_data.iterrows():
                # Get speed and heading
                speed = row.get('speed_knots', 0)
                heading = row.get('heading_degrees', 0)
                
                point_feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [row.geometry.x, row.geometry.y]
                    },
                    "properties": {
                        "vessel_name": vessel_name,
                        "vessel_type": vessel_type,
                        "speed_knots": speed,
                        "heading_degrees": heading,
                        "timestamp": row['timestamp'].isoformat(),
                        "point_type": "ship_position",
                        "track_color": track_color,
                        "source_file": source_file
                    }
                }
                features.append(point_feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        return geojson
    
    def create_sample_storm_data(self, storm_name=None, storm_year=None):
        """
        Create sample storm track data for the specified storm.
        This would typically come from NOAA's best track data.
        
        Args:
            storm_name (str): Name of the storm (defaults to config setting)
            storm_year (int): Year of the storm (defaults to config setting)
        
        Returns:
            dict: GeoJSON feature collection for storm track
        """
        # Use config defaults if not provided
        if storm_name is None:
            storm_name = config.STORM_NAME
        if storm_year is None:
            storm_year = config.STORM_YEAR
            
        # Sample data for a generic tropical storm
        # Format: [datetime, lat, lon, wind_speed, pressure, storm_type]
        # This creates a realistic storm track based on the provided year
        base_date = f"{storm_year}-10-11"
        sample_data = [
            [f"{base_date} 06:00:00", 32.5, -72.0, 35, 1008, "Subtropical Storm"],
            [f"{base_date} 12:00:00", 32.8, -71.5, 40, 1005, "Subtropical Storm"],
            [f"{base_date} 18:00:00", 33.2, -71.0, 45, 1002, "Subtropical Storm"],
            [f"{storm_year}-10-12 00:00:00", 33.8, -70.5, 50, 999, "Tropical Storm"],
            [f"{storm_year}-10-12 06:00:00", 34.5, -70.0, 55, 995, "Tropical Storm"],
            [f"{storm_year}-10-12 12:00:00", 35.2, -69.5, 60, 990, "Tropical Storm"],
            [f"{storm_year}-10-12 18:00:00", 36.0, -69.0, 65, 985, "Tropical Storm"],
            [f"{storm_year}-10-13 00:00:00", 36.8, -68.5, 70, 980, "Tropical Storm"],
            [f"{storm_year}-10-13 06:00:00", 37.5, -68.0, 65, 985, "Tropical Storm"],
            [f"{storm_year}-10-13 12:00:00", 38.2, -67.5, 60, 990, "Tropical Storm"],
            [f"{storm_year}-10-13 18:00:00", 39.0, -67.0, 55, 995, "Tropical Storm"],
            [f"{storm_year}-10-14 00:00:00", 39.8, -66.5, 50, 999, "Tropical Storm"],
            [f"{storm_year}-10-14 06:00:00", 40.5, -66.0, 45, 1002, "Tropical Storm"],
            [f"{storm_year}-10-14 12:00:00", 41.2, -65.5, 40, 1005, "Tropical Storm"],
            [f"{storm_year}-10-14 18:00:00", 42.0, -65.0, 35, 1008, "Tropical Storm"],
        ]
        
        # Convert to DataFrame
        df = pd.DataFrame(sample_data, columns=['datetime', 'latitude', 'longitude', 'wind_speed', 'pressure', 'storm_type'])
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # Create geometry
        geometry = [Point(lon, lat) for lon, lat in zip(df['longitude'], df['latitude'])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
        
        self.storm_data = gdf
        
        # Create GeoJSON features
        features = []
        
        # Create track line
        coords = [[point.x, point.y] for point in gdf.geometry]
        line_geometry = {
            "type": "LineString",
            "coordinates": coords
        }
        
        track_feature = {
            "type": "Feature",
            "geometry": line_geometry,
            "properties": {
                "storm_name": storm_name,
                "year": storm_year,
                "track_type": "storm_track"
            }
        }
        features.append(track_feature)
        
        # Create point features for each position
        for idx, row in gdf.iterrows():
            # Use shared utility for storm intensity
            intensity_info = determine_storm_intensity(row['wind_speed'])
            
            point_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [row.geometry.x, row.geometry.y]
                },
                "properties": {
                    "storm_name": storm_name,
                    "datetime": row['datetime'].isoformat(),
                    "wind_speed": row['wind_speed'],
                    "pressure": row['pressure'],
                    "storm_type": row['storm_type'],
                    "color": intensity_info['color'],
                    "point_type": "storm_position"
                }
            }
            features.append(point_feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        return geojson
    
    def save_geojson(self, geojson_data, output_file):
        """
        Save GeoJSON data to file.
        
        Args:
            geojson_data (dict): GeoJSON feature collection
            output_file (str): Output file path
        """
        return save_geojson(geojson_data, output_file)
    
    def get_western_atlantic_bounds(self):
        """
        Get the bounding box for the Western Atlantic Ocean.
        
        Returns:
            tuple: (min_lat, max_lat, min_lon, max_lon)
        """
        # Western Atlantic bounds (roughly from Florida to Newfoundland)
        return (20.0, 45.0, -85.0, -50.0) 