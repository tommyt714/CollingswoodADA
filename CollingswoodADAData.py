import numpy as np
import pandas as pd
import geopandas as gpd
import math
import requests

from geopandas.tools import geocode
import folium
from folium.plugins import MarkerCluster

agent = "my_colls_app"

ramp_path = '../input/rampdatalog/RampDataLog.xlsm' # originally hosted on Kaggle
ramp_df = pd.read_excel(ramp_path, sheet_name='data')

# Rename cross street columns to shorten and get rid of spaces
ramp_df.rename(columns={'Cross Street 1': 'CS_1', 'Cross Street 2': 'CS_2'}, inplace=True)

for col in ramp_df.columns.tolist()[:-1]:
    print(ramp_df[col].unique())
    
# "NE" appears twice; one with leading whitespace
ramp_df.replace(' NE', 'NE', inplace=True) #correct instance
ramp_df.Notes.fillna('None', inplace=True) #fill blank notes fields

# Combine cross streets into one intersection, if applicable
def cs_comb_str(cs1, cs2):
    """
    Take an intersection's cross streets as arguments and return
    a string of the complete location
    """
    
    inter = ""
    suffixes = ['Ave', 'Ln', 'Terr']
    
    if 'btw' in cs1:
        inter = cs1.split('btw')[0] + 'Ave btw ' + cs2
    elif type(cs2) != str:
        inter = cs1
    elif '(' in cs2:
        inter = cs1 + ' Ave and ' + cs2.split()[0] + ' Ave ' + cs2.split()[1]
    else:
        if not any([suf in cs1 for suf in suffixes]):
            cs1 += ' Ave'
        
        if (not any([suf in cs2 for suf in suffixes]) and
            not any([landmark in cs2 for landmark in ['alleyway', 'exit']]) and
            len(cs2.split()[-1]) > 1):
            cs2 += ' Ave'
        
        inter = ' and '.join([cs1, cs2])
        
    return inter

ramp_df['Inter'] = ramp_df.apply(lambda row: cs_comb_str(row['CS_1'], row['CS_2']), axis=1)

api_key = "" # exclude for security reasons

lat = []
long = []

url_boiler = 'https://maps.googleapis.com/maps/api/geocode/json?address='
unusual_phrases = ['btw', '\(', 'alleyway', 'exit']

for intersection in ramp_df.Inter:
    if not any([phrase in intersection for phrase in unusual_phrases]):
        url_address = '+'.join(intersection.split()) + ',+Collingswood,+NJ'
        url_complete = url_boiler + url_address + '&key=' + api_key
       
        response = requests.get(url_complete)
        resp_json = response.json()
        
        lat.append(resp_json['results'][0]['geometry']['location']['lat'])
        long.append(resp_json['results'][0]['geometry']['location']['lng'])
    else:
        lat.append(np.nan)
        long.append(np.nan)

cols = ramp_df.columns.tolist()
cols = cols[:3] + cols[-2:] + cols[3:-2]
ramp_df = ramp_df[cols]

def geo_short(location):
    """
    Take address, cross-street, etc. and return geocoded point at which
    lat/long can conveniently accessed.  Uses Nominatim.
    """
    pt = geocode(location, provider="nominatim", user_agent=agent)
    return pt.geometry.iloc[0]
  
def basemap_with_buffer(location, buffer_radius_miles):
    centerpoint = geo_short(location)
    basemap = folium.Map(location=[centerpoint.y, centerpoint.x], tiles="openstreetmap", zoom_start=15)
    
    buffer_radius_meters = buffer_radius_miles * 5280 / 3.28084 # miles to feet to meters
    basemap_buffer = folium.Circle(location=[centerpoint.y, centerpoint.x],
                                   radius=buffer_radius_meters).add_to(basemap)
    
    return basemap

patco_address = "100 Lees Ave, Collingswood, NJ 08108"
patco_base = basemap_with_buffer(patco_address, 0.5)
patco_base

patco_base = basemap_with_buffer(patco_address, 0.5)

for i, location in ramp_df.iterrows():
    if not np.isnan(location.Lat) and not np.isnan(location.Long):
        folium.Marker(location=[location.Lat, location.Long],tooltip=location.Inter).add_to(patco_base)

patco_base

patco_base = basemap_with_buffer(patco_address, 0.5)
marker_cluster = folium.plugins.MarkerCluster()

for i, location in ramp_df.iterrows():
    if not np.isnan(location.Lat) and not np.isnan(location.Long):
        marker_cluster.add_child(folium.Marker([location.Lat, location.Long], tooltip=location.Inter))

patco_base.add_child(marker_cluster)
patco_base

patco_base = basemap_with_buffer(patco_address, 0.5)

for i, location in ramp_df.iterrows():
    if not np.isnan(location.Lat) and not np.isnan(location.Long):
        color = "green" if location.Compliance == "Y" else "red"
        folium.Circle(location=[location.Lat, location.Long], radius=10,
                      color=color, tooltip=location.Inter).add_to(patco_base)

patco_base

patco_base = basemap_with_buffer(patco_address, 0.5)

# Hard-code certain latitudes/longitudes for locations that got incorrected geocoded
for i, location in ramp_df.iterrows():
    if not np.isnan(location.Lat) and not np.isnan(location.Long) and location.Compliance == "N":
        color = "green" if location.Compliance == "Y" else "red"
        if location.CS_1 == "Park":
            if location.CS_2 == "Cuthbert":
                lat = 39.9103431
                lng = -75.0586094
            elif location.CS_2 == "Ogden":
                lat = 39.9109968
                lng = -75.0606443
            elif location.CS_2 == "Conard":
                lat = 39.9115682
                lng = -75.062489
        elif location.CS_1 == "Laurel" and location.CS_2 == "Lincoln":
            lat = 39.9201176
            lng = -75.0627509
        elif location.CS_1 == "Cuthbert" and location.CS_2 == "Lindisfarne":
            lat = 39.9121536
            lng = -75.0576633
        else:
            lat = location.Lat
            lng = location.Long
                
        folium.Circle(location=[lat, lng], radius=10,
                      color=color, tooltip=location.Inter).add_to(patco_base)

patco_base
