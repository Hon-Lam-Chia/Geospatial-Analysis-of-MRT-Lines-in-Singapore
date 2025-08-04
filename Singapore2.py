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
#Worldmap = gpd.read_file('worldcountrymap.geo.json')
Worldmap = gpd.read_file('world.geojson')
print(Worldmap.head())
'''
Worldmap['sovereignt'] = Worldmap['sovereignt'].str.strip()
Worldmap.iloc[80, 3] = 'Hong Kong'
Worldmap.iloc[90, 3] = 'Macau'
Worldmap.iloc[34, 3] = 'British Virgin Islands'
Worldmap.iloc[36, 3] = 'Cayman Islands'
Worldmap.iloc[37, 3] = 'Bermuda'
'''
figworld = px.choropleth_map(
    Worldmap,
    geojson=Worldmap.geometry,
    locations= Worldmap.index,
    hover_name='NAME_LONG',
    center={"lat": 30, "lon": 0},
    zoom=1.5,
    opacity=0.6,
    height=600,
    map_style = 'carto-positron')

figworld.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
figworld.show()


'''
# 2) Foreign Investment in Singapore by Country
SGforeigninvestment = pd.read_csv('Singapore Portfolio Investment Liabilities By Source Economy And Instrument.csv', skiprows=10, nrows=34)
SGforeigninvestment.rename(columns = {'Data Series': 'Country'}, inplace=True)
SGforeigninvestment['Country'] = SGforeigninvestment['Country'].str.strip()
#print(SGforeigninvestment['Country'].unique())
print(SGforeigninvestment)


SGforeigninvestment.loc[SGforeigninvestment['Country']=="Mainland China", "Country"] = "China"
SGforeigninvestment.loc[SGforeigninvestment['Country']=="Republic Of Korea", "Country"] = "South Korea"

SGforeigninvestmentcountries = SGforeigninvestment[SGforeigninvestment['Country'].isin(Worldmap['sovereignt'])].copy()
SGFIdf = SGforeigninvestmentcountries.merge(Worldmap, left_on='Country', right_on='sovereignt', how='left')
#print(SGFIdf)
#print(SGforeigninvestment[~SGforeigninvestment['Country'].isin(Worldmap['sovereignt'])]['Country'])
#print(SGforeigninvestmentcountries)
countriesmissing = Worldmap[~Worldmap['sovereignt'].isin(SGforeigninvestmentcountries['Country'])].copy()
'''

'''
fig = go.Figure()
figdata = px.choropleth_map(
    SGforeigninvestmentcountries,
    geojson=SGincomebyPA.geometry,
    locations= SGincomebyPA.index,
    color = "AvgIncome",
    color_continuous_scale=px.colors.sequential.Plasma,
    hover_name="PLN_AREA_N",
    center={"lat": 1.3521, "lon": 103.8198}, 
    zoom=10,
    opacity=0.6,
    height=600,
    map_style = 'carto-positron')


figNA = px.choropleth_map(
    dfmissing,
    geojson=dfmissing.geometry,
    locations= dfmissing.index,
    color_discrete_sequence=["grey"],
    hover_name="PLN_AREA_N",
    hover_data="IncomeInfo",
    center={"lat": 1.3521, "lon": 103.8198}, 
    zoom=10,
    opacity=0.6,
    height=600,
    map_style = 'carto-positron')

fig = go.Figure(data = [*figdata.data, *figNA.data])
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                  map_center={"lat": 1.3521, "lon": 103.8198},
                  map_zoom=10.5)
fig.show()
'''