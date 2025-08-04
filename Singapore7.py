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


import requests
'''
url = "https://datamall2.mytransport.sg/ltaodataservice/PV/Train?Date=202504"
headers = {
    "AccountKey": "GyW5uODVTLKbIlEsE7nxbw==",
    "Accept": "application/json"
}

r = requests.get(url, headers=headers)
data = r.json()
print(data)


link = data['value'][0]['Link']
print(link)

import requests, zipfile, io, os

response = requests.get(link)
if response.status_code == 200:
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        os.makedirs("farecard_data", exist_ok=True)
        z.extractall("farecard_data")
        print("Extracted files:", z.namelist())
else:
    print(f"Download failed with status code {response.status_code}")


files = os.listdir("farecard_data")
csv_files = [f for f in files if f.endswith(".csv")]


df = pd.read_csv(f"farecard_data/{csv_files[0]}")
'''

df = pd.read_csv("RidershipbyTrainStation.csv")



unique_count = df['PT_CODE'].nunique()
#print(unique_count)
mrt_stations = df['PT_CODE'].unique()
#print(mrt_stations)

#print(df[(df['PT_CODE']=="EW1") &  (df['DAY_TYPE']=="WEEKDAY")])
#print(df[(df['PT_CODE']=="EW1") &  (df['DAY_TYPE']=="WEEKENDS/HOLIDAY")])

morningrushhour=(df[(df['PT_CODE'] == "EW1") &
         (df['DAY_TYPE'] == "WEEKDAY") &
         (df['TIME_PER_HOUR'] >= 7) &
         (df['TIME_PER_HOUR'] <= 9)])

eveningrushhour=(df[(df['PT_CODE'] == "EW1") &
         (df['DAY_TYPE'] == "WEEKDAY") &
         (df['TIME_PER_HOUR'] >= 17) &
         (df['TIME_PER_HOUR'] <= 20)])
#print(eveningrushhour)


rushhour_data = []

for ST in mrt_stations:
    morning_tapin = df[
        (df['PT_CODE'] == ST) &
        (df['DAY_TYPE'] == "WEEKDAY") &
        (df['TIME_PER_HOUR'] >= 7) &
        (df['TIME_PER_HOUR'] <= 9)]['TOTAL_TAP_IN_VOLUME'].sum()
    
    morning_tapout = df[
        (df['PT_CODE'] == ST) &
        (df['DAY_TYPE'] == "WEEKDAY") &
        (df['TIME_PER_HOUR'] >= 7) &
        (df['TIME_PER_HOUR'] <= 9)]['TOTAL_TAP_OUT_VOLUME'].sum()

    evening_tapin = df[
        (df['PT_CODE'] == ST) &
        (df['DAY_TYPE'] == "WEEKDAY") &
        (df['TIME_PER_HOUR'] >= 17) &
        (df['TIME_PER_HOUR'] <= 20)]['TOTAL_TAP_IN_VOLUME'].sum()

    evening_tapout = df[
        (df['PT_CODE'] == ST) &
        (df['DAY_TYPE'] == "WEEKDAY") &
        (df['TIME_PER_HOUR'] >= 17) &
        (df['TIME_PER_HOUR'] <= 20)]['TOTAL_TAP_OUT_VOLUME'].sum()
    
    rushhour_data.append({
        'Train Station': ST,
        'Average Morning Tap In': morning_tapin,
        'Average Morning Tap Out': morning_tapout,
        'Average Evening Tap In': evening_tapin,
        'Average Evening Tap Out': evening_tapout

    })

rushhour = pd.DataFrame(rushhour_data)


rushhour['Morning_OutIn_Ratio'] = rushhour['Average Morning Tap Out'] / rushhour['Average Morning Tap In']
rushhour['Evening_OutIn_Ratio'] = rushhour['Average Evening Tap Out'] / rushhour['Average Evening Tap In']
    
#print(rushhour[['Train Station', 'Morning_OutIn_Ratio']].sort_values("Morning_OutIn_Ratio", ascending=False))
#print(rushhour[['Train Station', 'Evening_OutIn_Ratio']].sort_values('Evening_OutIn_Ratio', ascending=False))

#print(rushhour)

## merge rushhour dataset (with station codes like "CC4/DT15") with your SGTrainStationInfo GeoDataFrame (which has individual codes like "CC4", "DT15").
# Step 1: Create a list of codes
rushhour['Train Station'] = rushhour['Train Station'].str.split('/')

# Step 2: Explode into multiple rows, one per code
rushhour_exploded = rushhour.explode('Train Station').reset_index(drop=True)
rushhour_exploded.rename(columns={'Train Station': 'SingleCode'}, inplace=True)





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

## Print out the stations with interchange in their name
#print(SGmrtstations[SGmrtstations["NAME"].str.contains("Interchange", case=False, na=False)])

## Remove interchange from the name so we can merge with the code dataset
SGmrtstations["NAME"] = SGmrtstations["NAME"].str.replace(r"\binterchange\b", "", case=False, regex=True).str.strip()
#print(SGmrtstations[SGmrtstations["NAME"].str.contains("Interchange", case=False, na=False)])


## 88, JALAN BESAR -> BENDEMEER
SGmrtstations.loc[88, 'NAME'] = 'BENDEMEER'

## 76, "" -> DOWNTOWN
SGmrtstations.loc[76, 'NAME'] = 'DOWNTOWN'

## 83, RIVER VALLEY -> FORT CANNING
SGmrtstations.loc[83, 'NAME'] = 'FORT CANNING'

## 194, JELEPANG -> JELAPANG
SGmrtstations.loc[194, 'NAME'] = 'JELAPANG'

## 53, ONE NORTH -> ONE-NORTH
SGmrtstations.loc[53, 'NAME'] = 'ONE-NORTH'

## 102, SUM KEE -> SAM KEE
SGmrtstations.loc[102, 'NAME'] = 'SAM KEE'

## 188 CHOA CHU KANG -> TEN MILE JUNCTION
SGmrtstations.loc[188, 'NAME'] = 'TEN MILE JUNCTION'

## 202 "" -> ORCHARD BOULEVARD
SGmrtstations.loc[202, 'NAME'] = 'ORCHARD BOULEVARD'

## 232 "" -> ORCHARD BOULEVARD
SGmrtstations.loc[232, 'NAME'] = 'WOODLANDS NORTH'

## 96 "" -> MAXWELL
SGmrtstations.loc[96, 'NAME'] = 'MAXWELL'

leftdf = sorted(list(SGmrtstations["NAME"].unique()))
#print(leftdf)


STcode_name = pd.read_excel("Train Station Codes and Chinese Names.xls")


STcode_name['mrt_station_english'] = STcode_name['mrt_station_english'].str.upper().str.strip()
rightdf = sorted(list(STcode_name['mrt_station_english'].unique()))
#print(rightdf)

right_not_in_left = [i for i in rightdf if i not in leftdf]
#print((right_not_in_left))
## To check which is still not in left df Eg: ['DOWNTOWN', 'FORT CANNING', 'JELAPANG', 'ONE-NORTH', 'SAM KEE', 'TEN MILE JUNCTION'] is still not in the df

#print(SGmrtstations["NAME"])




SGTrainStationInfo = SGmrtstations.merge(STcode_name, left_on="NAME", right_on="mrt_station_english", how="left")

#print(SGTrainStationInfo[SGTrainStationInfo["mrt_station_english"].isna()]['NAME'])
# remove all unopened stations (Cross Island Line, Jurong Regional Line etc)

SGTrainStationInfo = SGTrainStationInfo.dropna(subset=["mrt_station_english"])
SGTrainStationInfo.drop(columns=['GRND_LEVEL', 'INC_CRC', 'FMEL_UPD_D'], inplace=True)
#print(SGTrainStationInfo[SGTrainStationInfo['stn_code']=="DT15"])
#print(SGTrainStationInfo[SGTrainStationInfo['stn_code']=="CC4"])



############ Cleaned Full Train Station Dataset!! #########################3
merged = rushhour_exploded.merge(
    SGTrainStationInfo,
    left_on='SingleCode',
    right_on='stn_code',
    how='left'
)

merged['Total_Morning_Taps'] = merged['Average Morning Tap In'] + merged['Average Morning Tap Out']
merged['Total_Evening_Taps'] = merged['Average Evening Tap In'] + merged['Average Evening Tap Out']
merged['Total_Day_Taps'] = (merged['Average Morning Tap In'] + merged['Average Morning Tap Out'] + merged['Average Evening Tap In'] + merged['Average Evening Tap Out'])

print(merged)

merged.to_csv('Complete MRT Data.csv')

merged = gpd.GeoDataFrame(merged, geometry='geometry')


merged['lon'] = merged.geometry.centroid.x
merged['lat'] = merged.geometry.centroid.y

## visualize Morning Out/In Ratio as color, and tap-ins as marker size:
fig = px.scatter_mapbox(
    merged,
    lat='lat',
    lon='lon',
    size='Average Morning Tap In',
    color='Morning_OutIn_Ratio',
    hover_name='mrt_station_english',
    hover_data={
        'SingleCode': True,
        'Average Morning Tap In': True,
        'Average Morning Tap Out': True,
        'Morning_OutIn_Ratio': ':.2f',
        'lon': False,
        'lat': False
    },
    color_continuous_scale='RdBu',
    size_max=30,
    zoom=11,
    height=700
)

fig.update_layout(
    mapbox_style='carto-positron',
    title='📍 Singapore MRT Morning Rush Hour Analysis',
    margin={"r":0,"t":40,"l":0,"b":0}
)

#fig.show()



'''
What You Visualize	| Use As...    |	When To Use It
--------------------+--------------+---------------------------------------------------------
Tap-Ins (Morning)	|Marker size   | To find residential-origin stations
Tap-Outs (Morning)	|Marker size   |To highlight destination/business hubs
Tap-Out/Tap-In Ratio|Marker color  |To classify residential ↔ business station roles
Total Flow(In + Out)|Marker size   |To show station importance regardless of direction
'''