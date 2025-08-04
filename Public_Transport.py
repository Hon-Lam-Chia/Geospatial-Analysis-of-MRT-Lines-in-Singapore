import pandas as pd
import numpy as np
import requests 
import pprintpp as pp

# Fetching and processing Bus Routes data
'''
url_br = "https://datamall2.mytransport.sg/ltaodataservice/BusRoutes"
headers_br = {"AccountKey": "GyW5uODVTLKbIlEsE7nxbw=="}
response = requests.get(url_br, headers=headers_br)
data = response.json()
df1 = pd.DataFrame(data['value'])
df1.to_csv('BusRoutes.csv', index=False)
'''
# Fetching and processing Station Crowd Density data
'''
url_scd = "https://datamall2.mytransport.sg/ltaodataservice/PCDRealTime?TrainLine=EWL"
headers_scd = {"AccountKey": "GyW5uODVTLKbIlEsE7nxbw=="}
response2 = requests.get(url_scd, headers=headers_scd)
data2 = response2.json()
df2 = pd.DataFrame(data2['value'])
df2.to_csv('StationCrowdDensity.csv', index=False)
'''

# Fetching and processing Station Crowd Density Forecast data
'''
url_scdf = "https://datamall2.mytransport.sg/ltaodataservice/PCDForecast?TrainLine=EWL"
headers_scdf = {"AccountKey": "GyW5uODVTLKbIlEsE7nxbw=="}
response3 = requests.get(url_scdf, headers=headers_scdf)
data3 = response3.json()
stations_data = data3['value'][0]['Stations']

# Flatten the structure
records = []
for station in stations_data:
    station_name = station['Station']
    for interval in station['Interval']:
        records.append({
            'Station': station_name,
            'Datetime': interval['Start'],
            'CrowdLevel': interval['CrowdLevel']
        })

# Create DataFrame
df3 = pd.DataFrame(records)

# Optional: Convert datetime column to proper datetime format
df3['Datetime'] = pd.to_datetime(df3['Datetime'])

df3.to_csv('StationCrowdDensityForecast1.csv', index=False)
'''