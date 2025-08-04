import pandas as pd
import numpy as np
import plotly.express as px
import geopandas as gpd
import matplotlib.pyplot as plt
import json
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = 'browser'
from shapely.geometry import LineString


#1) Load the GeoJSON file
SGbusstops = gpd.read_file('BusStopLocation_Apr2025/BusStop.shp')

#print(SGbusstops)

SGbusstops = SGbusstops.to_crs("EPSG:4326")
figbusstop  = px.scatter_map(SGbusstops,
                        lat=SGbusstops.geometry.y,
                        lon=SGbusstops.geometry.x,
                        hover_name="LOC_DESC",
                        hover_data=["BUS_STOP_N"],
                        title="Bus Stops in Singapore",
                        labels={"LOC_DESC": "Bus Stop Name", "BUS_STOP_N": "Bus Stop Number"},
                        color_discrete_sequence=["blue"],
                        center={"lat": 1.3521, "lon": 103.8198}, 
                        zoom=10,
                        height=600,
                        map_style = 'carto-positron')


#figbusstop.show()


## For combining mrt stations and mrt lines map
fig = go.Figure()

#1) Load the GeoJSON file

with open('MasterPlan2019RailStationlayerGEOJSON.geojson') as f:
    data = json.load(f)

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame.from_features(data["features"])

# parse HTML in Description 
from bs4 import BeautifulSoup

def extract_attributes(description_html):
    soup = BeautifulSoup(description_html, "html.parser")
    rows = soup.find_all("tr")[1:]  # skip header row
    attributes = {}
    for row in rows:
        cols = row.find_all(["th", "td"])
        if len(cols) == 2:
            key = cols[0].text.strip()
            val = cols[1].text.strip()
            attributes[key] = val
    return attributes

# Apply the extraction
desc_df = gdf["Description"].apply(extract_attributes).apply(pd.Series)

# Merge with main DataFrame
SGmrtstations = pd.concat([gdf.drop(columns=["Description"]), desc_df], axis=1)
#print(SGmrtstations)



figstation  = px.choropleth_map(
    SGmrtstations,
    geojson=SGmrtstations.geometry,
    locations= SGmrtstations.index,
    color_discrete_sequence=["blue"],
    hover_name="NAME",
    hover_data=["RAIL_TYPE"],
    title="Bus Stops in Singapore",
    labels={"NAME": "Station Name", "RAIL_TYPE": "Rail Type"},
    center={"lat": 1.3521, "lon": 103.8198}, 
    zoom=10,
    opacity=0.6,
    height=800,
    map_style = 'carto-positron')





## mrt lines
with open('routes.citymapper.json', 'r', encoding='utf-8') as f:
    data = json.load(f)


lines = []

for route in data['routes']:
    route_name = route['name']
    color = route['color']
    for pattern in route.get('patterns', []):
        pattern_name = pattern['name']
        path = pattern['path']
        if path:
            line = LineString([(lon, lat) for lat, lon in path])  # careful: (lon, lat)
            lines.append({
                "route": route_name,
                "pattern": pattern_name,
                "color": color,
                "geometry": line
            })

SGmaproute = gpd.GeoDataFrame(lines, crs="EPSG:4326")  # WGS84 for lat/lon




# First, convert LineString geometry into separate lon/lat lists
SGmaproute["lon"] = SGmaproute.geometry.apply(lambda x: list(x.coords.xy[0]))
SGmaproute["lat"] = SGmaproute.geometry.apply(lambda x: list(x.coords.xy[1]))

exploded_rows = []

for _, row in SGmaproute.iterrows():
    df = pd.DataFrame({
        "route": row["route"],
        "pattern": row["pattern"],
        "lon": row["lon"],
        "lat": row["lat"]
    })
    exploded_rows.append(df)

SGmaproute_exploded = pd.concat(exploded_rows, ignore_index=True)

# Add a line_group id so each line is drawn properly
SGmaproute_exploded["line_id"] = SGmaproute_exploded["route"] + " | " + SGmaproute_exploded["pattern"]

color_map = {
    "CC": "#fa9e0d",  # Circle Line
    "NS": "#d42e12",  # North South Line
    "NE": "#9900aa",  # North East Line
    "DT": "#005ec4",  # Downtown Line
    "EW": "#009645",  # East West Line
    "TE": "#784008",  # Thomson-East Coast Line
    "PGLRT (East)": "#748477",
    "PGLRT (West)": "#748477",
    "SKLRT (West)": "#748477",
    "SKLRT (East)":"#748477"
}

figmrtroute = px.line_map(
    SGmaproute_exploded,
    lat="lat",
    lon="lon",
    color="route",
    color_discrete_map=color_map,
    line_group="line_id",
    hover_name="pattern",
    hover_data=["route"],
    title="MRT Routes in Singapore",
    labels={"route": "Route Name", "pattern": "Pattern Name"},
    center={"lat": 1.3521, "lon": 103.8198},
    zoom=10,
    height=800,
    map_style="carto-positron"
)

fig = go.Figure(data = [*figstation.data, *figmrtroute.data])
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                  map_center={"lat": 1.3521, "lon": 103.8198},
                  map_zoom=10.5)
fig.show()

