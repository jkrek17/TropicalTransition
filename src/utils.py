"""
Shared utilities for the Tropical Cyclone and Ship Track Visualization Project.

This module contains common functionality used across multiple modules.
"""

import json
import os
from typing import Optional, Tuple, Dict, Any

def parse_coordinate(coord_str: str, coord_type: str) -> Optional[float]:
    """
    Parse coordinate string from HURDAT2 format.
    
    Args:
        coord_str (str): Coordinate string (e.g., "325N", "720W")
        coord_type (str): Type of coordinate ('lat' or 'lon')
        
    Returns:
        Optional[float]: Parsed coordinate value or None if invalid
    """
    if not coord_str or coord_str == '-999':
        return None
    
    # Remove any whitespace
    coord_str = coord_str.strip()
    
    # Extract numeric part and direction
    if coord_type == 'lat':
        # Latitude: ends with N or S
        if coord_str.endswith('N'):
            return float(coord_str[:-1])
        elif coord_str.endswith('S'):
            return -float(coord_str[:-1])
    elif coord_type == 'lon':
        # Longitude: ends with E or W
        if coord_str.endswith('E'):
            return float(coord_str[:-1])
        elif coord_str.endswith('W'):
            return -float(coord_str[:-1])
    
    return None

def determine_storm_intensity(wind_speed: int) -> Dict[str, Any]:
    """
    Determine storm intensity based on wind speed.
    
    Args:
        wind_speed (int): Wind speed in mph
        
    Returns:
        Dict[str, Any]: Intensity information including color, size, and label
    """
    if wind_speed >= 74:
        return {
            'color': 'red',
            'size': 100,
            'marker': 'o',
            'label': 'Hurricane (≥74 mph)',
            'intensity': 'Hurricane'
        }
    elif wind_speed >= 39:
        return {
            'color': 'orange',
            'size': 80,
            'marker': 'o',
            'label': 'Tropical Storm (39-73 mph)',
            'intensity': 'Tropical Storm'
        }
    else:
        return {
            'color': 'yellow',
            'size': 60,
            'marker': 'o',
            'label': 'Tropical Depression (<39 mph)',
            'intensity': 'Tropical Depression'
        }

def save_geojson(geojson_data: Dict[str, Any], output_file: str) -> bool:
    """
    Save GeoJSON data to file.
    
    Args:
        geojson_data (Dict[str, Any]): GeoJSON data to save
        output_file (str): Output file path
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure output directory exists (only if there's a directory path)
        dir_path = os.path.dirname(output_file)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(geojson_data, f, indent=2)
        
        print(f"GeoJSON saved to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error saving GeoJSON: {e}")
        return False

def load_geojson(input_file: str) -> Optional[Dict[str, Any]]:
    """
    Load GeoJSON data from file.
    
    Args:
        input_file (str): Input file path
        
    Returns:
        Optional[Dict[str, Any]]: GeoJSON data or None if failed
    """
    try:
        with open(input_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading GeoJSON: {e}")
        return None

def calculate_bounds_from_coordinates(coordinates: list, padding: float = 5.0) -> Tuple[float, float, float, float]:
    """
    Calculate map bounds from a list of coordinates.
    
    Args:
        coordinates (list): List of [lon, lat] coordinates
        padding (float): Padding in degrees around data
        
    Returns:
        Tuple[float, float, float, float]: (lon_min, lon_max, lat_min, lat_max)
    """
    if not coordinates:
        return (-85.0, -50.0, 15.0, 50.0)  # Default Western Atlantic bounds
    
    lons = [coord[0] for coord in coordinates]
    lats = [coord[1] for coord in coordinates]
    
    lon_min, lon_max = min(lons), max(lons)
    lat_min, lat_max = min(lats), max(lats)
    
    # Add padding
    lon_min -= padding
    lon_max += padding
    lat_min -= padding
    lat_max += padding
    
    return (lon_min, lon_max, lat_min, lat_max)

def format_coordinate(coord: float, coord_type: str) -> str:
    """
    Format coordinate for display.
    
    Args:
        coord (float): Coordinate value
        coord_type (str): Type of coordinate ('lat' or 'lon')
        
    Returns:
        str: Formatted coordinate string
    """
    if coord_type == 'lat':
        direction = 'N' if coord >= 0 else 'S'
        return f"{abs(coord):.1f}°{direction}"
    else:  # lon
        direction = 'E' if coord >= 0 else 'W'
        return f"{abs(coord):.1f}°{direction}"

def detect_dateline_crossing(coordinates: list) -> bool:
    """
    Detect if a list of [lon, lat] coordinates crosses the dateline.
    Returns True if any jump in longitude between consecutive points is > 180°.
    """
    lons = [coord[0] for coord in coordinates]
    for i in range(1, len(lons)):
        if abs(lons[i] - lons[i-1]) > 180:
            return True
    return False

def to_360_longitude(coordinates: list) -> list:
    """
    Convert all longitudes in a list of [lon, lat] to 0–360 system.
    """
    return [[lon if lon >= 0 else lon + 360, lat] for lon, lat in coordinates]

def transform_geojson_to_360(geojson: dict) -> dict:
    """
    If any feature crosses the dateline, convert all longitudes in the GeoJSON to 0–360.
    Works for both LineString and Point geometries.
    """
    if not geojson or 'features' not in geojson:
        return geojson
    # Gather all coordinates
    all_coords = []
    for feature in geojson['features']:
        geom = feature['geometry']
        if geom['type'] == 'LineString':
            all_coords.extend(geom['coordinates'])
        elif geom['type'] == 'Point':
            all_coords.append(geom['coordinates'])
    # Detect dateline crossing
    if not detect_dateline_crossing(all_coords):
        return geojson  # No transformation needed
    # Transform all features
    new_features = []
    for feature in geojson['features']:
        geom = feature['geometry']
        new_geom = dict(geom)
        if geom['type'] == 'LineString':
            new_geom['coordinates'] = to_360_longitude(geom['coordinates'])
        elif geom['type'] == 'Point':
            lon, lat = geom['coordinates']
            new_geom['coordinates'] = [lon if lon >= 0 else lon + 360, lat]
        new_feature = dict(feature)
        new_feature['geometry'] = new_geom
        new_features.append(new_feature)
    new_geojson = dict(geojson)
    new_geojson['features'] = new_features
    return new_geojson 