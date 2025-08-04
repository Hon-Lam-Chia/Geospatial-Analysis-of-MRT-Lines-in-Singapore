import pandas as pd
import numpy as np
import plotly.express as px
import geopandas as gpd
import matplotlib.pyplot as plt
import json
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = 'browser'


#1) Load the GeoJSON file
SGsubzone = gpd.read_file('SGsubzone.geojson')
#print(SGsubzone .head())

# Load your GeoJSON file (or string)
with open('SGsubzone.geojson') as f:
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
SGsubzone = pd.concat([gdf.drop(columns=["Description"]), desc_df], axis=1)



# 1) General Subzone Map
figSZ = px.choropleth_map(
    SGsubzone,
    geojson=SGsubzone.geometry,
    locations= SGsubzone.index,
    hover_name="SUBZONE_N",
    center={"lat": 1.3521, "lon": 103.8198}, 
    zoom=10,
    opacity=0.6,
    height=600,
    map_style = 'carto-positron')

figSZ.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#figSZ.show()


# 2) Population by Subzone
SZpop = pd.read_csv('ResidentPopulationbyPlanningAreaSubzoneofResidenceEthnicGroupandSexCensusofPopulation2020.csv')

SZpop.drop(columns=['Total_Males', 'Total_Females',
       'Chinese_Total', 'Chinese_Males', 'Chinese_Females', 'Malays_Total',
       'Malays_Males', 'Malays_Females', 'Indians_Total', 'Indians_Males',
       'Indians_Females', 'Others_Total', 'Others_Males', 'Others_Females'], inplace=True)

SZpop = SZpop.rename(columns={'Number': 'Planning Area Subzone', 'Total_Total': 'Total Resident Population'})
SZpop['Planning Area Subzone'] = SZpop['Planning Area Subzone'].str.strip().str.upper()
#print(SZpop['Planning Area Subzone'])
#print(SGsubzone)
PlanningAreapop = SZpop[~SZpop['Planning Area Subzone'].isin(SGsubzone['SUBZONE_N'])]
Subzonespop = SZpop[SZpop['Planning Area Subzone'].isin(SGsubzone['SUBZONE_N'])]

SubzonespopGEO = SGsubzone.merge(Subzonespop, left_on='SUBZONE_N', right_on='Planning Area Subzone', how='left')
#print(SubzonespopGEO.head())
SubzonespopGEO['geometry'] = SubzonespopGEO['geometry'].simplify(tolerance=0.0005, preserve_topology=True)


figSZpop = px.choropleth_map(
    SubzonespopGEO,
    geojson=SubzonespopGEO.geometry,
    locations= 'SUBZONE_N',
    hover_name='Planning Area Subzone',
    color='Total Resident Population',
    color_continuous_scale=px.colors.sequential.YlOrRd,
    center={"lat": 1.3521, "lon": 103.8198}, 
    zoom=10,
    opacity=0.6,
    height=600,
    map_style = 'carto-positron')

figSZpop.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
figSZpop.show()

