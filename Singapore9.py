import pandas as pd
import numpy as np
import plotly.express as px
import geopandas as gpd
import matplotlib.pyplot as plt
import json
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = 'browser'
from shapely import wkt
from geopy.distance import geodesic


gdf = pd.read_csv('SGsubzones.csv')
gdf["geometry"] = gdf["geometry"].apply(wkt.loads)

## Convert WKT strings to actual Polygon geometries
SGsubzones = gpd.GeoDataFrame(gdf, geometry="geometry", crs="EPSG:3414")

# Centroids of subzones
SGsubzones["centroid"] = SGsubzones.geometry.centroid
SGsubzones["lat"] = SGsubzones.centroid.y
SGsubzones["lon"] = SGsubzones.centroid.x
#print(SGsubzones)




# Import MRT Station data
gdf1  = pd.read_csv("Complete MRT Data.csv")
gdf1["geometry"] = gdf1["geometry"].apply(wkt.loads)
SGmrtstations = gpd.GeoDataFrame(gdf1, geometry="geometry", crs="EPSG:3414")
#print(SGmrtstations)

# Centroids of mrt stations
SGmrtstations["centroid"] = SGmrtstations.geometry.centroid
SGmrtstations["lat"] = SGmrtstations.centroid.y
SGmrtstations["lon"] = SGmrtstations.centroid.x

# Coordinates of mrt
#mrt_coords = SGmrtstations[["lat", "lon"]].values
#print(mrt_coords)

mrt_coords = list(zip(SGmrtstations["NAME"],SGmrtstations["stn_code"], SGmrtstations["lat"], SGmrtstations["lon"]))

# nearest_mrt_distance() calculates the shortest distance (in km) between a given subzone's centroid and the list of MRT station coordinates.
## geodesic measures the real-world (spherical) distance between two GPS points.
def nearest_mrt_info(row, mrt_coords):
    subzone_coord = (row["lat"], row["lon"])
    # Calculate distances and keep name & code
    distances = [(name,code, geodesic(subzone_coord, (lat, lon)).km) for name, code, lat, lon in mrt_coords]
    # Find the MRT with the minimum distance
    nearest_station, stn_code, min_distance = min(distances, key=lambda x: x[2])
    return pd.Series([nearest_station, stn_code, min_distance])

SGsubzones[["nearest_mrt__station_name", "station_code", "dist_to_nearest_mrt_km"]] = SGsubzones.apply(
    nearest_mrt_info, axis=1, args=(mrt_coords,)
)

SGdistomrt = SGsubzones.sort_values(by="dist_to_nearest_mrt_km", ascending=False)
#print(SGdistomrt)


SGdistomrttop30 = SGdistomrt.sort_values("dist_to_nearest_mrt_km", ascending=False).head(30)
#print(SGdistomrttop30)
#SGpopdenbyPAsorted = SGpopdenbyPAsorted[~(SGpopdenbyPAsorted["dist_to_nearest_mrt_km"].isna())]


figSGdistomrttop30 = px.bar(SGdistomrttop30, y='SUBZONE_N', x="dist_to_nearest_mrt_km", color="dist_to_nearest_mrt_km",
                color_continuous_scale=px.colors.sequential.Viridis,
                title='Distance to the Nearest MRT Station from the Centre of each Subzones',
                hover_name='SUBZONE_N',
                labels={"dist_to_nearest_mrt_km": 'Distance to Nearest MRT'},
                height=1200)
#figSGdistomrttop30.show()  




























print(SGdistomrt.columns)
figSZ = px.choropleth_map(
    SGdistomrt,
    geojson=SGdistomrt.geometry,
    locations= SGdistomrt.index,
    hover_name="SUBZONE_N",
    hover_data={
        'dist_to_nearest_mrt_km': True,
        'nearest_mrt__station_name': True,
        'station_code': True},
    color = 'dist_to_nearest_mrt_km',
    color_continuous_scale=px.colors.sequential.YlOrRd,
    center={"lat": 1.3521, "lon": 103.8198}, 
    zoom=10,
    opacity=0.6,
    height=600,
    map_style = 'carto-positron')

figSZ.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#figSZ.show()
