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



with open("MasterPlan2019LandUselayer.geojson") as f:
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
landuse = pd.concat([gdf.drop(columns=["Description"]), desc_df], axis=1)


landuse.to_csv("landuse.csv")

figdata = px.choropleth_map(
    landuse,
    geojson=landuse.geometry,
    locations= landuse.index,
    color = "LU_DESC",
    hover_name="LU_DESC",
    center={"lat": 1.3521, "lon": 103.8198}, 
    zoom=10,
    opacity=0.6,
    height=600,
    map_style = 'carto-positron')

figdata.show()