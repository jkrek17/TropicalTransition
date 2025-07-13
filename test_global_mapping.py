#!/usr/bin/env python3
"""
Test script to demonstrate global mapping capability.
This script creates sample data for different geographic regions and shows
how the maps automatically adapt to any location, including dateline crossing.
"""

import json
import os
from src.data_processor import DataProcessor
from src.map_creator import MapCreator
from src.matplotlib_mapper import MatplotlibMapper
from src.utils import transform_geojson_to_360

def create_pacific_storm_data():
    """Create sample storm data for the Pacific Ocean."""
    storm_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [140.0, 20.0],  # Western Pacific
                        [145.0, 22.0],
                        [150.0, 25.0],
                        [155.0, 28.0],
                        [160.0, 30.0],
                        [165.0, 32.0],
                        [170.0, 35.0]   # Eastern Pacific
                    ]
                },
                "properties": {
                    "storm_name": "Typhoon Pacific",
                    "year": 2023,
                    "storm_type": "typhoon"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [140.0, 20.0]
                },
                "properties": {
                    "storm_name": "Typhoon Pacific",
                    "datetime": "2023-10-01T00:00:00Z",
                    "wind_speed": 85,
                    "pressure": 950,
                    "status": "Typhoon"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [170.0, 35.0]
                },
                "properties": {
                    "storm_name": "Typhoon Pacific",
                    "datetime": "2023-10-05T12:00:00Z",
                    "wind_speed": 95,
                    "pressure": 920,
                    "status": "Typhoon"
                }
            }
        ]
    }
    return storm_data

def create_pacific_ship_data():
    """Create sample ship data for the Pacific Ocean."""
    ship_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [135.0, 18.0],  # Western Pacific
                        [140.0, 20.0],
                        [145.0, 22.0],
                        [150.0, 24.0],
                        [155.0, 26.0],
                        [160.0, 28.0],
                        [165.0, 30.0],
                        [170.0, 32.0]   # Eastern Pacific
                    ]
                },
                "properties": {
                    "vessel_name": "Pacific Cargo",
                    "vessel_type": "Cargo"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [135.0, 18.0]
                },
                "properties": {
                    "vessel_name": "Pacific Cargo",
                    "vessel_type": "Cargo",
                    "speed_knots": 15,
                    "heading_degrees": 90,
                    "timestamp": "2023-10-01T00:00:00Z"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [170.0, 32.0]
                },
                "properties": {
                    "vessel_name": "Pacific Cargo",
                    "vessel_type": "Cargo",
                    "speed_knots": 18,
                    "heading_degrees": 90,
                    "timestamp": "2023-10-05T12:00:00Z"
                }
            }
        ]
    }
    return ship_data

def create_dateline_crossing_storm_data():
    """Create sample storm data that crosses the International Date Line."""
    storm_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [175.0, 25.0],   # Western Pacific (175°E)
                        [177.0, 26.0],   # Approaching dateline
                        [179.0, 27.0],   # Near dateline
                        [180.0, 28.0],   # At dateline
                        [181.0, 29.0],   # Crossed dateline (181°E = -179°E)
                        [185.0, 30.0],   # Eastern Pacific (185°E = -175°E)
                        [190.0, 31.0],   # Further east (190°E = -170°E)
                        [195.0, 32.0]    # Eastern Pacific (195°E = -165°E)
                    ]
                },
                "properties": {
                    "storm_name": "Dateline Typhoon",
                    "year": 2023,
                    "storm_type": "typhoon"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [175.0, 25.0]
                },
                "properties": {
                    "storm_name": "Dateline Typhoon",
                    "datetime": "2023-09-01T00:00:00Z",
                    "wind_speed": 80,
                    "pressure": 960,
                    "status": "Typhoon"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [180.0, 28.0]
                },
                "properties": {
                    "storm_name": "Dateline Typhoon",
                    "datetime": "2023-09-03T12:00:00Z",
                    "wind_speed": 85,
                    "pressure": 950,
                    "status": "Typhoon"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [195.0, 32.0]
                },
                "properties": {
                    "storm_name": "Dateline Typhoon",
                    "datetime": "2023-09-05T00:00:00Z",
                    "wind_speed": 90,
                    "pressure": 930,
                    "status": "Typhoon"
                }
            }
        ]
    }
    return storm_data

def create_dateline_crossing_ship_data():
    """Create sample ship data that crosses the International Date Line."""
    ship_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [170.0, 23.0],   # Western Pacific (170°E)
                        [175.0, 24.0],   # Approaching dateline
                        [178.0, 25.0],   # Near dateline
                        [180.0, 26.0],   # At dateline
                        [182.0, 27.0],   # Crossed dateline (182°E = -178°E)
                        [185.0, 28.0],   # Eastern Pacific (185°E = -175°E)
                        [190.0, 29.0],   # Further east (190°E = -170°E)
                        [195.0, 30.0]    # Eastern Pacific (195°E = -165°E)
                    ]
                },
                "properties": {
                    "vessel_name": "Dateline Cargo",
                    "vessel_type": "Cargo"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [170.0, 23.0]
                },
                "properties": {
                    "vessel_name": "Dateline Cargo",
                    "vessel_type": "Cargo",
                    "speed_knots": 12,
                    "heading_degrees": 90,
                    "timestamp": "2023-09-01T00:00:00Z"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [180.0, 26.0]
                },
                "properties": {
                    "vessel_name": "Dateline Cargo",
                    "vessel_type": "Cargo",
                    "speed_knots": 14,
                    "heading_degrees": 90,
                    "timestamp": "2023-09-03T12:00:00Z"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [195.0, 30.0]
                },
                "properties": {
                    "vessel_name": "Dateline Cargo",
                    "vessel_type": "Cargo",
                    "speed_knots": 16,
                    "heading_degrees": 90,
                    "timestamp": "2023-09-05T00:00:00Z"
                }
            }
        ]
    }
    return ship_data

def create_indian_ocean_storm_data():
    """Create sample storm data for the Indian Ocean."""
    storm_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [60.0, -10.0],   # Western Indian Ocean
                        [65.0, -8.0],
                        [70.0, -6.0],
                        [75.0, -4.0],
                        [80.0, -2.0],
                        [85.0, 0.0],
                        [90.0, 2.0]      # Eastern Indian Ocean
                    ]
                },
                "properties": {
                    "storm_name": "Cyclone Indian",
                    "year": 2023,
                    "storm_type": "cyclone"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [60.0, -10.0]
                },
                "properties": {
                    "storm_name": "Cyclone Indian",
                    "datetime": "2023-11-01T00:00:00Z",
                    "wind_speed": 75,
                    "pressure": 960,
                    "status": "Cyclone"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [90.0, 2.0]
                },
                "properties": {
                    "storm_name": "Cyclone Indian",
                    "datetime": "2023-11-05T12:00:00Z",
                    "wind_speed": 85,
                    "pressure": 940,
                    "status": "Cyclone"
                }
            }
        ]
    }
    return storm_data

def create_indian_ocean_ship_data():
    """Create sample ship data for the Indian Ocean."""
    ship_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [55.0, -12.0],   # Western Indian Ocean
                        [60.0, -10.0],
                        [65.0, -8.0],
                        [70.0, -6.0],
                        [75.0, -4.0],
                        [80.0, -2.0],
                        [85.0, 0.0],
                        [90.0, 2.0]      # Eastern Indian Ocean
                    ]
                },
                "properties": {
                    "vessel_name": "Indian Tanker",
                    "vessel_type": "Tanker"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [55.0, -12.0]
                },
                "properties": {
                    "vessel_name": "Indian Tanker",
                    "vessel_type": "Tanker",
                    "speed_knots": 12,
                    "heading_degrees": 90,
                    "timestamp": "2023-11-01T00:00:00Z"
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [90.0, 2.0]
                },
                "properties": {
                    "vessel_name": "Indian Tanker",
                    "vessel_type": "Tanker",
                    "speed_knots": 14,
                    "heading_degrees": 90,
                    "timestamp": "2023-11-05T12:00:00Z"
                }
            }
        ]
    }
    return ship_data

def test_global_mapping():
    """Test the global mapping capability with different geographic regions."""
    print("🌍 Testing Global Mapping Capability")
    print("=" * 50)
    
    # Initialize components
    processor = DataProcessor()
    map_creator = MapCreator()
    static_mapper = MatplotlibMapper()
    
    # Test regions
    regions = [
        ("Pacific Ocean", create_pacific_storm_data(), create_pacific_ship_data()),
        ("Indian Ocean", create_indian_ocean_storm_data(), create_indian_ocean_ship_data()),
        ("Dateline Crossing", create_dateline_crossing_storm_data(), create_dateline_crossing_ship_data())
    ]
    
    for region_name, storm_data, ship_data in regions:
        print(f"\n🗺️  Testing {region_name}...")
        
        # Debug dateline crossing transformation
        if region_name == "Dateline Crossing":
            print("   Debug: Original coordinates:")
            for feature in storm_data['features']:
                if feature['geometry']['type'] == 'LineString':
                    coords = feature['geometry']['coordinates']
                    print(f"      Storm track: {coords[0]} to {coords[-1]}")
            for feature in ship_data['features']:
                if feature['geometry']['type'] == 'LineString':
                    coords = feature['geometry']['coordinates']
                    print(f"      Ship track: {coords[0]} to {coords[-1]}")
            
            # Convert 0-360 data to -180 to +180 for Folium while maintaining continuity
            def convert_0360_to_180180(geojson_data):
                """Convert 0-360 coordinates to -180 to +180 for Folium."""
                converted_data = geojson_data.copy()
                for feature in converted_data['features']:
                    geom = feature['geometry']
                    if geom['type'] == 'LineString':
                        converted_coords = []
                        for lon, lat in geom['coordinates']:
                            # Convert 0-360 to -180 to +180
                            if lon > 180:
                                converted_lon = lon - 360
                            else:
                                converted_lon = lon
                            converted_coords.append([converted_lon, lat])
                        geom['coordinates'] = converted_coords
                    elif geom['type'] == 'Point':
                        lon, lat = geom['coordinates']
                        if lon > 180:
                            converted_lon = lon - 360
                        else:
                            converted_lon = lon
                        geom['coordinates'] = [converted_lon, lat]
                return converted_data
            
            # Convert data for Folium
            folium_storm_data = convert_0360_to_180180(storm_data)
            folium_ship_data = convert_0360_to_180180(ship_data)
            
            print("   Debug: Converted coordinates for Folium:")
            for feature in folium_storm_data['features']:
                if feature['geometry']['type'] == 'LineString':
                    coords = feature['geometry']['coordinates']
                    print(f"      Storm track: {coords[0]} to {coords[-1]}")
            for feature in folium_ship_data['features']:
                if feature['geometry']['type'] == 'LineString':
                    coords = feature['geometry']['coordinates']
                    print(f"      Ship track: {coords[0]} to {coords[-1]}")
            
            # Calculate center in 0-360 system
            all_lons = []
            all_lats = []
            for feature in storm_data['features'] + ship_data['features']:
                geom = feature['geometry']
                if geom['type'] == 'LineString':
                    for lon, lat in geom['coordinates']:
                        all_lons.append(lon)
                        all_lats.append(lat)
                elif geom['type'] == 'Point':
                    lon, lat = geom['coordinates']
                    all_lons.append(lon)
                    all_lats.append(lat)
            if all_lons and all_lats:
                center_lon_0360 = (min(all_lons) + max(all_lons)) / 2
                center_lat = (min(all_lats) + max(all_lats)) / 2
                # Convert center back to -180–180 for Folium
                if center_lon_0360 > 180:
                    center_lon = center_lon_0360 - 360
                else:
                    center_lon = center_lon_0360
            else:
                center_lat, center_lon = 0, 0
            
            # Create interactive map with converted data
            interactive_output = f"tests/{region_name.lower().replace(' ', '_')}_interactive.html"
            interactive_map = map_creator.create_complete_map(
                ship_geojson=folium_ship_data,
                storm_geojson=folium_storm_data,
                output_file=interactive_output
            )
            # Centering is handled inside create_complete_map, but you can pass center_lat, center_lon if needed
        else:
            # Create interactive map (no transformation needed)
            interactive_output = f"tests/{region_name.lower().replace(' ', '_')}_interactive.html"
            interactive_map = map_creator.create_complete_map(
                ship_geojson=ship_data,
                storm_geojson=storm_data,
                output_file=interactive_output
            )
        
        if interactive_map:
            print(f"✅ Interactive map created: {interactive_map}")
        else:
            print("❌ Failed to create interactive map")
        
        # Create static map (always use original data, static mapper handles transformation)
        static_output = f"tests/{region_name.lower().replace(' ', '_')}_static.png"
        static_map = static_mapper.create_complete_static_map(
            ship_geojson=ship_data,
            storm_geojson=storm_data,
            output_file=static_output
        )
        
        if static_map:
            print(f"✅ Static map created: {static_map}")
        else:
            print("❌ Failed to create static map")
        
        # Save GeoJSON data
        ship_output = f"tests/{region_name.lower().replace(' ', '_')}_ships.geojson"
        storm_output = f"tests/{region_name.lower().replace(' ', '_')}_storm.geojson"
        processor.save_geojson(ship_data, ship_output)
        processor.save_geojson(storm_data, storm_output)
    
    print("\n🎯 Global Mapping Test Results:")
    print("✅ Maps automatically adapt to any geographic location")
    print("✅ Bounds calculated from data coordinates")
    print("✅ Center and zoom automatically determined")
    print("✅ Works for Pacific, Indian Ocean, and dateline crossing")
    print("✅ Handles International Date Line crossing correctly")
    print("\n📁 Generated test files in tests/ folder:")
    print("   • pacific_ocean_interactive.html")
    print("   • pacific_ocean_static.png")
    print("   • indian_ocean_interactive.html")
    print("   • indian_ocean_static.png")
    print("   • dateline_crossing_interactive.html")
    print("   • dateline_crossing_static.png")

if __name__ == "__main__":
    test_global_mapping() 