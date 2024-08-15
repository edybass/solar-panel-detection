"""
Geospatial Analysis Module for Solar Panel Detection
Integrates detection results with geographic information systems
"""

import geopandas as gpd
import folium
from shapely.geometry import Point, Polygon
import rasterio
from rasterio.transform import from_origin
import numpy as np
from typing import List, Dict, Tuple
import json


class GeoAnalyzer:
    """Analyze solar panel detections in geographic context."""

    def __init__(self):
        self.crs = 'EPSG:4326'  # WGS84

    def create_solar_map(self, detection_results: List[Dict], 
                        output_path: str = 'solar_map.html') -> folium.Map:
        """
        Create an interactive map of solar panel detections.

        Args:
            detection_results: List of detection results with GPS coordinates
            output_path: Path to save the HTML map

        Returns:
            Folium map object
        """
        # Initialize map
        if detection_results:
            first_result = detection_results[0]
            center_lat = first_result.get('latitude', 37.7749)
            center_lon = first_result.get('longitude', -122.4194)
        else:
            center_lat, center_lon = 37.7749, -122.4194

        solar_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles='OpenStreetMap'
        )

        # Add detection markers
        for result in detection_results:
            if 'latitude' in result and 'longitude' in result:
                # Create popup info
                popup_text = f"""
                <b>Solar Installation</b><br>
                Panels: {result['panel_count']}<br>
                Power: {result['estimated_kwh']:.1f} kWh<br>
                Area: {result['total_area_sqm']:.1f} m²<br>
                Date: {result['timestamp'][:10]}
                """

                # Determine marker color based on size
                if result['panel_count'] > 100:
                    color = 'red'  # Large installation
                elif result['panel_count'] > 20:
                    color = 'orange'  # Medium installation
                else:
                    color = 'green'  # Small installation

                folium.Marker(
                    location=[result['latitude'], result['longitude']],
                    popup=folium.Popup(popup_text, max_width=300),
                    icon=folium.Icon(color=color, icon='sun', prefix='fa')
                ).add_to(solar_map)

        # Add layer control
        folium.LayerControl().add_to(solar_map)

        # Save map
        solar_map.save(output_path)
        return solar_map

    def analyze_solar_density(self, detection_results: List[Dict], 
                             grid_size: float = 0.01) -> gpd.GeoDataFrame:
        """
        Analyze solar panel density across a geographic area.

        Args:
            detection_results: List of detection results
            grid_size: Size of grid cells in degrees

        Returns:
            GeoDataFrame with density analysis
        """
        # Create points from detection results
        points = []
        for result in detection_results:
            if 'latitude' in result and 'longitude' in result:
                point = Point(result['longitude'], result['latitude'])
                points.append({
                    'geometry': point,
                    'panel_count': result['panel_count'],
                    'power_kwh': result['estimated_kwh']
                })

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(points, crs=self.crs)

        # Create grid for density analysis
        minx, miny, maxx, maxy = gdf.total_bounds

        # Generate grid cells
        grid_cells = []
        x = minx
        while x < maxx:
            y = miny
            while y < maxy:
                cell = Polygon([
                    (x, y),
                    (x + grid_size, y),
                    (x + grid_size, y + grid_size),
                    (x, y + grid_size)
                ])
                grid_cells.append(cell)
                y += grid_size
            x += grid_size

        # Create grid GeoDataFrame
        grid_gdf = gpd.GeoDataFrame({'geometry': grid_cells}, crs=self.crs)

        # Calculate density for each grid cell
        grid_gdf['panel_count'] = 0
        grid_gdf['total_power'] = 0.0

        for idx, cell in grid_gdf.iterrows():
            # Find points within this cell
            within = gdf[gdf.within(cell.geometry)]
            grid_gdf.at[idx, 'panel_count'] = within['panel_count'].sum()
            grid_gdf.at[idx, 'total_power'] = within['power_kwh'].sum()

        # Calculate density metrics
        grid_gdf['panel_density'] = grid_gdf['panel_count'] / (grid_size ** 2)
        grid_gdf['power_density'] = grid_gdf['total_power'] / (grid_size ** 2)

        return grid_gdf

    def extract_coordinates_from_image(self, image_path: str) -> Dict:
        """
        Extract GPS coordinates from georeferenced image.

        Args:
            image_path: Path to georeferenced image (GeoTIFF)

        Returns:
            Dictionary with coordinate information
        """
        try:
            with rasterio.open(image_path) as src:
                # Get bounds
                bounds = src.bounds

                # Get center coordinates
                center_x = (bounds.left + bounds.right) / 2
                center_y = (bounds.top + bounds.bottom) / 2

                # Transform to lat/lon if needed
                if src.crs != 'EPSG:4326':
                    import pyproj
                    transformer = pyproj.Transformer.from_crs(
                        src.crs, 'EPSG:4326', always_xy=True
                    )
                    lon, lat = transformer.transform(center_x, center_y)
                else:
                    lon, lat = center_x, center_y

                return {
                    'latitude': lat,
                    'longitude': lon,
                    'bounds': {
                        'north': bounds.top,
                        'south': bounds.bottom,
                        'east': bounds.right,
                        'west': bounds.left
                    },
                    'crs': str(src.crs),
                    'resolution': src.res
                }
        except Exception as e:
            # Return None if image is not georeferenced
            return None

    def calculate_solar_potential(self, latitude: float, panel_area_sqm: float,
                                 efficiency: float = 0.20) -> Dict:
        """
        Calculate solar energy potential based on location.

        Args:
            latitude: Latitude of the location
            panel_area_sqm: Total panel area in square meters
            efficiency: Panel efficiency (default 20%)

        Returns:
            Dictionary with solar potential metrics
        """
        # Simplified solar irradiance calculation
        # In production, this would use actual solar radiation data

        # Average solar irradiance (kWh/m²/day) by latitude
        if abs(latitude) < 23.5:  # Tropical
            avg_irradiance = 5.5
        elif abs(latitude) < 35:  # Subtropical
            avg_irradiance = 5.0
        elif abs(latitude) < 50:  # Temperate
            avg_irradiance = 4.0
        else:  # Polar
            avg_irradiance = 2.5

        # Calculate daily and annual production
        daily_production = panel_area_sqm * avg_irradiance * efficiency
        annual_production = daily_production * 365

        # CO2 offset (assuming 0.5 kg CO2 per kWh)
        co2_offset_annual = annual_production * 0.5

        return {
            'daily_production_kwh': daily_production,
            'monthly_production_kwh': daily_production * 30,
            'annual_production_kwh': annual_production,
            'co2_offset_kg_annual': co2_offset_annual,
            'trees_equivalent': co2_offset_annual / 21.77  # kg CO2 per tree per year
        }
