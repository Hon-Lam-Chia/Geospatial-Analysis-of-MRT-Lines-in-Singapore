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
SGmap = gpd.read_file('MasterPlan2019PlanningAreaBoundaryNoSea.geojson')


#2) Create Map and Barplot of Average Monthly Household Income by Planning Area
SGincome = pd.read_csv("ResidentHouseholdsbyPlanningAreaofResidenceandMonthlyHouseholdIncomefromWorkCensusOfPopulation2020.csv")

MidIncomeRange = {'Below_1_000': 500,
                '1_000_1_999': 1500,
                '2_000_2_999': 2500,
                '3_000_3_999': 3500,
                '4_000_4_999': 4500,
                '5_000_5_999': 5500,
                '6_000_6_999': 6500,
                '7_000_7_999': 7500,
                '8_000_8_999': 8500,
                '9_000_9_999': 9500,
                '10_000_10_999': 10500,
                '11_000_11_999': 11500,
                '12_000_12_999': 12500,
                '13_000_13_999': 13500,
                '14_000_14_999': 14500,
                '15_000_17_499': 16250,
                '17_500_19_999': 18750,
                 '20_000andOver': 22000}

def total_estimated_income(row):
    total_income = 0
    for income_range, midpoint in MidIncomeRange.items():
        if row[income_range] > 0:
            total_income += row[income_range] * midpoint
    return total_income

SGincome['TotalEstimatedIncome'] = SGincome.apply(total_estimated_income, axis=1)

SGincome['AvgIncome'] = (SGincome['TotalEstimatedIncome'] / SGincome['Total']).round(2)


# Make all planning area name uppercase to be merged on flat_df on PLN_AREA_N later
SGincome['Number'] = SGincome['Number'].str.upper()




# Load your GeoJSON file (or string)
with open('MasterPlan2019PlanningAreaBoundaryNoSea.geojson') as f:
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
flat_df = pd.concat([gdf.drop(columns=["Description"]), desc_df], axis=1)


# Merge the income data with the flat_df GeoDataFrame
SGincomebyPA = flat_df.merge(SGincome, left_on='PLN_AREA_N', right_on='Number', how='left')

# Filter out rows where AvgIncome is NaN, we will use this as a separate Map to overlay on the main map
#dfmissing = SGincomebyPA[SGincomebyPA['AvgIncome'].isna()]
#dfmissing["IncomeInfo"] = "No data"
dfmissing = SGincomebyPA[SGincomebyPA['AvgIncome'].isna()].copy()
dfmissing["IncomeInfo"] = "No data"

#print(dfmissing['PLN_AREA_N'].unique())  # Check which Planning Areas have no income data

fig = go.Figure()
figdata = px.choropleth_map(
    SGincomebyPA,
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

SGincomebyPAsorted = SGincomebyPA.sort_values(by='AvgIncome', ascending=False)
SGincomebyPAsorted = SGincomebyPAsorted [~(SGincomebyPAsorted['AvgIncome'].isna())]

figbar = px.bar(SGincomebyPAsorted, x='PLN_AREA_N', y='AvgIncome', color='AvgIncome',
                color_continuous_scale=px.colors.sequential.Plasma,
                title='Average Monthly Household Income by Planning Area',
                labels={'AvgIncome': 'Average Income', 'PLN_AREA_N': 'Planning Area'},
                height=600)
#figbar.show()


# 3) Create Map and Barplot of Population Density by Planning Area

# Calculate Land Area in km2 of each planning area
gdf = gpd.read_file("MP14_PLNG_AREA_NO_SEA_PL.shp").to_crs(epsg=3414)
gdf["area_km2"] = gdf.geometry.area / 1e6
land_area = gdf[['PLN_AREA_N', 'area_km2']]
#print(land_area)

SGpop = pd.read_csv("ResidentPopulationbyPlanningAreaSubzoneofResidenceEthnicGroupandSexCensusofPopulation2020.csv")

SGpop['Total_Total'] = SGpop['Total_Total'].str.replace('-', '0').astype(int)
#print(SGpop[SGpop['Number']=="Central Water Catchment - Total"]) # check whether '-' is replaced with '0' correctly


SGPApop = SGpop[SGpop["Number"].str.contains("Total")]

#SGPApop['PlanningArea'] = SGPApop['Number'].str.split('-').str[0].str.upper().str.strip()
#SGPApop['PlanningArea'] = SGPApop['Number'].str.strip(to_strip=' - Total').str.upper()

SGPApop['PlanningArea'] = SGPApop['Number'].str.replace(r'\s*-\s*Total', '', regex=True).str.upper().str.strip()
#print(SGPApop['PlanningArea'].unique()) # check Planning Area names
#print(len(SGPApop['PlanningArea'].unique())) # check Planning Area number

# Merge population data with the GeoDataFrame
SGpoparea = land_area.merge(SGPApop, left_on='PLN_AREA_N', right_on='PlanningArea', how='left')



SGpopbyPA = flat_df.merge(SGpoparea, left_on='PLN_AREA_N', right_on='PlanningArea', how='left')
SGpopbyPA.rename(columns={'Total_Total': 'Total Population'}, inplace=True)

SGpopbyPA.drop(columns=['PLN_AREA_N_x', 'PLN_AREA_C', 'CA_IND', 'REGION_N', 'REGION_C', 'INC_CRC', 'FMEL_UPD_D', 'Number', 'Total_Males', 'Total_Females', 'Chinese_Total', 'Chinese_Males', 'Chinese_Females', 'Malays_Total', 'Malays_Males', 'Malays_Females', 'Indians_Total', 'Indians_Males', 'Indians_Females', 'Others_Total', 'Others_Males', 'Others_Females'], inplace=True)
#print(SGpopbyPA) 
#print(SGpopbyPA['PlanningArea'].unique()) # check Planning Area names
#print(len(SGpopbyPA['PlanningArea'].unique())) # check Planning Area names

# Plot Population by Planning Area
figpop = px.choropleth_map(
    SGpopbyPA,
    geojson=SGpopbyPA.geometry,
    locations= SGpopbyPA.index,
    color = 'Total Population',
    color_continuous_scale=px.colors.sequential.YlOrRd,
    hover_name='PlanningArea',
    center={"lat": 1.3521, "lon": 103.8198}, 
    zoom=10,
    opacity=0.6,
    height=600,
    map_style = 'carto-positron')

figpop.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#figpop.show()


SGpopbyPAsorted = SGpopbyPA.sort_values(by='Total Population', ascending=False)
SGpopbyPAsorted = SGpopbyPAsorted[~(SGpopbyPAsorted['Total Population'].isna())]
figpopbar = px.bar(SGpopbyPAsorted, x='PlanningArea', y='Total Population', color='Total Population',
                color_continuous_scale=px.colors.sequential.YlOrRd,
                title='Total Resident Population by Planning Area',
                labels={'Total Population': 'Resident Population', 'PlanningArea': 'Planning Area'},
                height=600)
#figpopbar.show()   

#Compute and Map Population Density
SGpopbyPA['PopulationDensity'] = (SGpopbyPA['Total Population'] / SGpopbyPA['area_km2']).round(2)

figpopden = px.choropleth_map(
    SGpopbyPA,
    geojson=SGpopbyPA.geometry,
    locations= SGpopbyPA.index,
    color = 'PopulationDensity',
    color_continuous_scale=px.colors.sequential.Viridis,
    hover_name='PlanningArea',
    center={"lat": 1.3521, "lon": 103.8198}, 
    zoom=10,
    opacity=0.6,
    height=600,
    map_style = 'carto-positron')

figpopden.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#figpopden.show()

SGpopdenbyPAsorted = SGpopbyPA.sort_values(by='PopulationDensity', ascending=False)
SGpopdenbyPAsorted = SGpopdenbyPAsorted[~(SGpopdenbyPAsorted['PopulationDensity'].isna())]


figpopdenbar = px.bar(SGpopdenbyPAsorted, x='PlanningArea', y='PopulationDensity', color='PopulationDensity',
                color_continuous_scale=px.colors.sequential.Viridis,
                title='Population Density by Planning Area',
                labels={'PopulationDensity': 'Population Density (people/km²)', 'PlanningArea': 'Planning Area'},
                height=600)
#figpopdenbar.show()   


