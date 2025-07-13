#!/usr/bin/env python3
"""
NHC Hurricane Data Downloader

Downloads real hurricane track data from NOAA's National Hurricane Center
HURDAT2 database for Atlantic hurricanes.
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime
import os
import re
import sys
from io import StringIO
from .utils import parse_coordinate

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class NHCDataDownloader:
    """Downloads and processes hurricane track data from NOAA NHC."""
    
    def __init__(self, basin="Atlantic"):
        # Set up basin-specific configuration
        self.basin = basin
        self.basin_config = config.BASIN_SETTINGS.get(basin, config.BASIN_SETTINGS["Atlantic"])
        self.hurdat2_url = self.basin_config["data_url"]
        self.data_file = self.basin_config["data_file"]
        self.data_dir = "data"
        self.raw_data = None
        self.processed_storms = {}
    
    def download_hurdat2_data(self):
        """Download the HURDAT2 database file."""
        if not self.hurdat2_url:
            print(f"❌ No HURDAT2 data URL available for {self.basin} basin")
            return False
            
        print(f"📥 Downloading HURDAT2 {self.basin} hurricane database...")
        
        try:
            # Create data directory if it doesn't exist
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Download the data
            response = requests.get(self.hurdat2_url, timeout=30)
            response.raise_for_status()
            
            # Save raw data
            raw_file = os.path.join(self.data_dir, self.data_file)
            with open(raw_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            self.raw_data = response.text
            print(f"✅ Downloaded HURDAT2 {self.basin} data ({len(response.text)} characters)")
            print(f"📁 Saved to: {raw_file}")
            
            return True
            
        except requests.RequestException as e:
            print(f"❌ Error downloading HURDAT2 data: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def parse_hurdat2_data(self):
        """Parse the HURDAT2 data format."""
        if not self.raw_data:
            print("❌ No data to parse. Download data first.")
            return False
        
        print("🔍 Parsing HURDAT2 data...")
        
        lines = self.raw_data.strip().split('\n')
        current_storm = None
        storm_data = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a header line (storm identifier)
            if line.count(',') >= 2 and re.match(r'^[A-Z]{2}\d{6}$', line.split(',')[0]):
                # This is a header line
                parts = [p.strip() for p in line.split(',')]
                storm_id = parts[0]
                storm_name = parts[1]
                num_entries = int(parts[2]) if parts[2].strip() else 0
                
                # Save previous storm if exists
                if current_storm and storm_data:
                    self.processed_storms[current_storm['id']] = {
                        'info': current_storm,
                        'track': storm_data.copy()
                    }
                
                # Start new storm
                current_storm = {
                    'id': storm_id,
                    'name': storm_name,
                    'num_entries': num_entries,
                    'year': int(storm_id[4:8])
                }
                storm_data = []
                
            else:
                # This is a track data line
                if current_storm:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 7:
                        try:
                            track_point = {
                                'date': parts[0],
                                'time': parts[1],
                                'record_identifier': parts[2],
                                'status': parts[3],
                                'latitude': self._parse_coordinate(parts[4], 'lat'),
                                'longitude': self._parse_coordinate(parts[5], 'lon'),
                                'max_wind': int(parts[6]) if parts[6] != '-999' else None,
                                'min_pressure': int(parts[7]) if len(parts) > 7 and parts[7] != '-999' else None
                            }
                            storm_data.append(track_point)
                        except (ValueError, IndexError) as e:
                            print(f"⚠️  Skipping malformed line: {line[:50]}...")
        
        # Save last storm
        if current_storm and storm_data:
            self.processed_storms[current_storm['id']] = {
                'info': current_storm,
                'track': storm_data.copy()
            }
        
        print(f"✅ Parsed {len(self.processed_storms)} storms from HURDAT2 data")
        return True
    
    def _parse_coordinate(self, coord_str, coord_type):
        """Parse coordinate string from HURDAT2 format."""
        return parse_coordinate(coord_str, coord_type)
    
    def find_storm_by_name_year(self, name, year):
        """Find a storm by name and year."""
        name_upper = name.upper()
        
        for storm_id, storm_data in self.processed_storms.items():
            if (storm_data['info']['year'] == year and 
                storm_data['info']['name'].upper() == name_upper):
                return storm_id, storm_data
        
        return None, None
    
    def get_storm_geojson(self, storm_id, storm_data):
        """Convert storm data to GeoJSON format."""
        if not storm_data or 'track' not in storm_data:
            return None
        
        features = []
        track_coords = []
        
        # Process track points
        for point in storm_data['track']:
            if point['latitude'] is not None and point['longitude'] is not None:
                coords = [point['longitude'], point['latitude']]
                track_coords.append(coords)
                
                # Determine storm intensity color
                wind_speed = point['max_wind'] if point['max_wind'] else 0
                if wind_speed >= 74:
                    color = "#FF0000"  # Red for hurricane
                    intensity = "Hurricane"
                elif wind_speed >= 39:
                    color = "#FFA500"  # Orange for tropical storm
                    intensity = "Tropical Storm"
                else:
                    color = "#FFFF00"  # Yellow for tropical depression
                    intensity = "Tropical Depression"
                
                # Create point feature
                point_feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": coords
                    },
                    "properties": {
                        "storm_name": storm_data['info']['name'],
                        "storm_id": storm_id,
                        "datetime": f"{point['date']} {point['time']}",
                        "status": point['status'],
                        "wind_speed": wind_speed,
                        "pressure": point['min_pressure'],
                        "intensity": intensity,
                        "color": color,
                        "point_type": "storm_position"
                    }
                }
                features.append(point_feature)
        
        # Create track line feature
        if len(track_coords) >= 2:
            line_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": track_coords
                },
                "properties": {
                    "storm_name": storm_data['info']['name'],
                    "storm_id": storm_id,
                    "year": storm_data['info']['year'],
                    "track_type": "storm_track"
                }
            }
            features.append(line_feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        return geojson
    
    def download_and_process_storm(self, storm_name, year):
        """Download HURDAT2 data and extract specific storm."""
        print(f"🌪️ Searching for {storm_name} ({year})...")
        
        # Download data if not already done
        if not self.raw_data:
            if not self.download_hurdat2_data():
                return None
        
        # Parse data if not already done
        if not self.processed_storms:
            if not self.parse_hurdat2_data():
                return None
        
        # Find the storm
        storm_id, storm_data = self.find_storm_by_name_year(storm_name, year)
        
        if not storm_id:
            print(f"❌ Storm '{storm_name}' not found in {year}")
            # List available storms for that year
            year_storms = [s for s in self.processed_storms.values() if s['info']['year'] == year]
            if year_storms:
                print(f"Available storms in {year}:")
                for s in year_storms[:10]:  # Show first 10
                    print(f"   - {s['info']['name']} ({s['info']['id']})")
            return None
        
        print(f"✅ Found {storm_name} ({year}): {storm_id}")
        print(f"   Track points: {len(storm_data['track'])}")
        
        # Convert to GeoJSON
        geojson = self.get_storm_geojson(storm_id, storm_data)
        
        # Save to file
        output_file = f"output/{storm_name.lower()}_{year}_track.geojson"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        import json
        with open(output_file, 'w') as f:
            json.dump(geojson, f, indent=2)
        
        print(f"💾 Saved track data to: {output_file}")
        
        return geojson
    
    def list_storms_by_year(self, year):
        """List all storms for a given year."""
        if not self.processed_storms:
            print("❌ No storm data loaded. Download and parse data first.")
            return []
        
        year_storms = []
        for storm_id, storm_data in self.processed_storms.items():
            if storm_data['info']['year'] == year:
                year_storms.append({
                    'id': storm_id,
                    'name': storm_data['info']['name'],
                    'points': len(storm_data['track'])
                })
        
        return sorted(year_storms, key=lambda x: x['id'])

def main():
    """Main function to download and process hurricane data."""
    # Use config settings for storm selection
    storm_name = config.STORM_NAME
    storm_year = config.STORM_YEAR
    storm_basin = config.STORM_BASIN
    
    print(f"🔍 Looking for {storm_name} ({storm_year}) in {storm_basin} basin...")
    
    # Create downloader for the specified basin
    downloader = NHCDataDownloader(basin=storm_basin)
    
    # Try to find the configured storm
    storm_geojson = downloader.download_and_process_storm(storm_name, storm_year)
    
    if not storm_geojson:
        print(f"\n🔍 {storm_name} not found. Let's see what storms are available in {storm_year}...")
        
        # Show available storms for the year
        storms_year = downloader.list_storms_by_year(storm_year)
        print(f"\n📊 Found {len(storms_year)} storms in {storm_year}:")
        for storm in storms_year:
            print(f"   - {storm['name']} ({storm['id']}) - {storm['points']} points")
        
        # Try to get the first available storm as fallback
        if storms_year:
            fallback_storm = storms_year[0]
            print(f"\n🌪️ Using {fallback_storm['name']} as fallback...")
            storm_geojson = downloader.download_and_process_storm(fallback_storm['name'], storm_year)
            
    return storm_geojson

if __name__ == "__main__":
    result = main()
    if result:
        print("\n✅ Successfully downloaded real NHC hurricane track data!")
    else:
        print("\n❌ Failed to download hurricane data.") 