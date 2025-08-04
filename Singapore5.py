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



gdf = gpd.read_file("MP14_PLNG_AREA_NO_SEA_PL.shp").to_crs(epsg=3414)
gdf["area_km2"] = gdf.geometry.area / 10**6
land_area = gdf[['PLN_AREA_N', 'area_km2','geometry']]
land_area = land_area.to_crs(epsg=4326)





#1) Load the GeoJSON file
SGWorkbyPA = pd.read_csv('EmployedResidentsAged15YearsandOverbyPlanningAreaofWorkplaceandUsualModeofTransporttoWorkCensusofPopulation2020.csv')

# Convert columns to numeric
SGWorkbyPA[['MRT_LRTOnly','MRT_LRTandPublicBusOnly', 'OthercombinationsofMRT_LRTorPublicBus']] = SGWorkbyPA[['MRT_LRTOnly','MRT_LRTandPublicBusOnly', 'OthercombinationsofMRT_LRTorPublicBus']].replace("-", 0).astype(int)

df_Workingpop = SGWorkbyPA[['Number', 'Total']].copy()
df_Workingpop["Number"] = df_Workingpop["Number"].str.upper().str.strip()


df_Workingpopdense = land_area.merge(df_Workingpop, left_on='PLN_AREA_N', right_on="Number", how="left")
#print(df_Workingpopdense)
df_Workingpopdense["Working Population Density"] = (df_Workingpopdense["Total"] / df_Workingpopdense["area_km2"]).round(2)
dfmissing = df_Workingpopdense[df_Workingpopdense['Total'].isna()].copy()
dfmissing["Total"] = 0
dfmissing["Working Population Density"] = 0
dfmissing["Working Population Density Info"] = "No data"


fig1 = go.Figure()
figdata1 = px.choropleth_map(
    df_Workingpopdense,
    geojson=df_Workingpopdense.geometry,
    locations= df_Workingpopdense.index,
    color = "Working Population Density",
    color_continuous_scale=px.colors.sequential.Viridis,
    hover_name="PLN_AREA_N",
    center={"lat": 1.3521, "lon": 103.8198}, 
    zoom=10,
    opacity=0.6,
    height=600,
    map_style = 'carto-positron')


figNA1 = px.choropleth_map(
    dfmissing,
    geojson=dfmissing.geometry,
    locations= dfmissing.index,
    color_discrete_sequence=["grey"],
    hover_name="PLN_AREA_N",
    hover_data="Working Population Density Info",
    center={"lat": 1.3521, "lon": 103.8198}, 
    zoom=10,
    opacity=0.6,
    height=600,
    map_style = 'carto-positron')

figWPD = go.Figure(data = [*figdata1.data, *figNA1.data])
figWPD.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                  map_center={"lat": 1.3521, "lon": 103.8198},
                  map_zoom=10)
#figWPD.show()





df_mrt = SGWorkbyPA[['Number', 'Total', 'MRT_LRTOnly','MRT_LRTandPublicBusOnly', 'OthercombinationsofMRT_LRTorPublicBus']]

# Sum up all mrt users

def total_mrt_users(row):
    total_user = 0
    total_user += row['MRT_LRTOnly']
    total_user += row['MRT_LRTandPublicBusOnly']
    total_user += row['OthercombinationsofMRT_LRTorPublicBus']
    return total_user

df_mrt['Total MRT User'] = df_mrt.apply(total_mrt_users, axis=1)


df_mrt["Ratio_of_MRT_Users"] = (df_mrt['Total MRT User'] / df_mrt['Total']).round(3)
df_mrt["Number"] = df_mrt["Number"].str.upper().str.strip()

df_mrt_ratio = land_area.merge(df_mrt, left_on='PLN_AREA_N', right_on="Number", how="left")
#print(df_mrt_ratio)



dfmissingmrt = df_mrt_ratio[df_mrt_ratio['Total MRT User'].isna()].copy()
dfmissingmrt["Total MRT User"] = 0
dfmissingmrt["Ratio_of_MRT_Users"] = 0
dfmissingmrt["Ratio_of_MRT_Users Info"] = "No data"

print(dfmissingmrt)

fig2 = go.Figure()
figdata2 = px.choropleth_map(
    df_mrt_ratio,
    geojson=df_mrt_ratio.geometry,
    locations= df_mrt_ratio.index,
    color = "Ratio_of_MRT_Users",
    color_continuous_scale=px.colors.sequential.Bluered,
    hover_name="PLN_AREA_N",
    center={"lat": 1.3521, "lon": 103.8198}, 
    zoom=10,
    opacity=0.6,
    height=600,
    map_style = 'carto-positron')


figNA2 = px.choropleth_map(
    dfmissingmrt,
    geojson=dfmissingmrt.geometry,
    locations= dfmissingmrt.index,
    color_discrete_sequence=["grey"],
    hover_name="PLN_AREA_N",
    hover_data="Ratio_of_MRT_Users Info",
    center={"lat": 1.3521, "lon": 103.8198}, 
    zoom=10,
    opacity=0.6,
    height=600,
    map_style = 'carto-positron')

figMRTr = go.Figure(data = [*figdata2.data, *figNA2.data])
figMRTr.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                  map_center={"lat": 1.3521, "lon": 103.8198},
                  map_zoom=10)
figMRTr.show()