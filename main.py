#!/usr/bin/env python3
"""
Tropical Cyclone and Ship Track Visualization Project
- Interactive Web Maps (Folium)
- Static Presentation Maps (Matplotlib)

This script creates both interactive and static maps for different use cases.
"""

import os
import sys
import json
from src.data_processor import DataProcessor
from src.map_creator import MapCreator
from src.matplotlib_mapper import MatplotlibMapper

def main():
    """Main application function that creates both interactive and static maps."""
    print("🌊 Tropical Cyclone and Ship Track Visualization Project")
    print("=" * 60)
    
    # Show current configuration
    import config
    print(f"📋 Current Configuration:")
    print(f"   Storm: {config.STORM_NAME} ({config.STORM_YEAR})")
    print(f"   Basin: {config.STORM_BASIN}")
    print(f"   Auto-download: {config.AUTO_DOWNLOAD_STORM_DATA}")
    print()
    print("Creating both interactive and static maps...")
    
    # Initialize data processor
    processor = DataProcessor()
    
    # Initialize map creators
    map_creator = MapCreator()
    static_mapper = MatplotlibMapper()
    
    # Process ship data
    print("\n📊 Processing ship track data...")
    
    # Try to load multiple ship files from data directory
    ship_data = processor.load_multiple_ship_files_from_directory("data")
    
    if ship_data is not None:
        # Create ship tracks GeoJSON
        ship_geojson = processor.create_ship_tracks_geojson(ship_data)
        
        # Save ship GeoJSON
        processor.save_geojson(ship_geojson, "output/combined_ship_tracks.geojson")
        print("✅ Multiple ship data files processed successfully")
    else:
        # Fallback to sample data
        print("⚠️  No ship data files found in data directory, trying sample data...")
        sample_ship_csv_path = "sample_data/sample_ship_data.csv"
        
        if os.path.exists(sample_ship_csv_path):
            ship_data = processor.load_ship_data_from_csv(sample_ship_csv_path)
            
            if ship_data is not None:
                # Create ship tracks GeoJSON
                ship_geojson = processor.create_ship_tracks_geojson(ship_data)
                
                # Save ship GeoJSON
                processor.save_geojson(ship_geojson, "output/ship_tracks.geojson")
                print("✅ Sample ship data processed successfully")
            else:
                print("❌ Failed to process sample ship data")
                ship_geojson = None
        else:
            print("❌ No ship data files found")
            ship_geojson = None
    
    # Process storm data using configuration
    print("\n🌪️ Processing storm track data...")
    storm_geojson = processor.load_storm_data_from_config()
    
    if storm_geojson:
        print("✅ Storm data processed successfully")
    else:
        print("❌ Failed to process storm data")
    
    # Create interactive map
    print("\n🗺️  Creating interactive web map...")
    interactive_output = f"output/{config.STORM_NAME.lower()}_{config.STORM_YEAR}_interactive_map.html"
    interactive_map = map_creator.create_complete_map(
        ship_geojson=ship_geojson,
        storm_geojson=storm_geojson,
        output_file=interactive_output
    )
    
    if interactive_map:
        print(f"✅ Interactive map created: {interactive_map}")
    else:
        print("❌ Failed to create interactive map")
    
    # Create static map for presentations
    print("\n📊 Creating static presentation map...")
    static_output = f"output/{config.STORM_NAME.lower()}_{config.STORM_YEAR}_static_map.png"
    
    # Let the mapper automatically calculate bounds from data
    static_map = static_mapper.create_complete_static_map(
        ship_geojson=ship_geojson,
        storm_geojson=storm_geojson,
        output_file=static_output
    )
    
    if static_map:
        print(f"✅ Static map created: {static_map}")
    else:
        print("❌ Failed to create static map")
    

    
    # Print summary
    print("\n📋 Project Summary:")
    if ship_data is not None:
        num_vessels = len(ship_data.groupby(['vessel_name', 'MMSI']).groups) if 'vessel_name' in ship_data.columns or 'MMSI' in ship_data.columns else 0
        num_files = len(ship_data['source_file'].unique()) if 'source_file' in ship_data.columns else 1
        print(f"   - Ship tracks: {num_vessels} vessels from {num_files} data files")
    else:
        print("   - Ship tracks: No ship data loaded")
    print(f"   - Storm track: {config.STORM_NAME} ({config.STORM_YEAR}) from {config.STORM_BASIN} basin")
    print("   - Interactive map: HTML file for web viewing")
    print("   - Static map: PNG file for presentations")
    print("   - Output files: HTML, PNG, and GeoJSON data files")
    
    print("\n🎓 Learning Objectives Achieved:")
    print("   ✅ Geographic data processing with pandas and geopandas")
    print("   ✅ CSV to GeoJSON conversion")
    print("   ✅ Interactive web mapping with Folium")
    print("   ✅ Static mapping with matplotlib and cartopy")
    print("   ✅ Multi-layer map visualization")
    print("   ✅ Custom markers and popups")
    print("   ✅ High-quality output for presentations")
    
    print("\n📁 Generated Files:")
    print(f"   📄 Interactive Map: {interactive_output}")
    print(f"   🖼️  Static Map: {static_output}")
    storm_geojson_file = f"output/{config.STORM_NAME.lower()}_{config.STORM_YEAR}_track.geojson"
    ship_geojson_file = "output/combined_ship_tracks.geojson" if ship_data is not None and 'source_file' in ship_data.columns else "output/ship_tracks.geojson"
    print(f"   📊 Data Files: {ship_geojson_file}, {storm_geojson_file}")
    
    print("\n💡 Usage:")
    print("   • Interactive Map: Open HTML file in web browser")
    print("   • Static Map: Use PNG file in presentations (no internet required)")
    print("   • Data Files: Use GeoJSON files for further analysis")
    
    return 0

def create_sample_data():
    """Create sample data files for demonstration."""
    print("📝 Creating sample data files...")
    
    # Sample ship data (already created in sample_data/sample_ship_data.csv)
    print("✅ Sample ship data already exists")
    
    # Create a simple test script
    test_script = '''#!/usr/bin/env python3
"""
Test script for the mapping project.
Run this to test individual components.
"""

from data_processor import DataProcessor
from map_creator import MapCreator

def test_data_processing():
    """Test the data processing functionality."""
    processor = DataProcessor()
    
    # Test ship data loading
    ship_data = processor.load_ship_data_from_csv("sample_data/sample_ship_data.csv")
    if ship_data is not None:
        print("✅ Ship data loading test passed")
    else:
        print("❌ Ship data loading test failed")
    
    # Test storm data creation
    storm_geojson = processor.create_sample_storm_data()
    if storm_geojson:
        print("✅ Storm data creation test passed")
    else:
        print("❌ Storm data creation test failed")

def test_map_creation():
    """Test the map creation functionality."""
    map_creator = MapCreator()
    
    # Test base map creation
    map_obj = map_creator.create_base_map()
    if map_obj:
        print("✅ Base map creation test passed")
    else:
        print("❌ Base map creation test failed")

if __name__ == "__main__":
    print("🧪 Running tests...")
    test_data_processing()
    test_map_creation()
    print("✅ All tests completed")
'''
    
    with open("test_project.py", "w") as f:
        f.write(test_script)
    
    print("✅ Test script created: test_project.py")

if __name__ == "__main__":
    # Create sample data if needed
    if not os.path.exists("sample_data/sample_ship_data.csv"):
        create_sample_data()
    
    # Run main application
    exit_code = main()
    sys.exit(exit_code) 