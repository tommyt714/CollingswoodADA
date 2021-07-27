import pandas as pd
import googlemaps as gm

f_path = r"C:\Users\tthompson\Documents\CollingswoodADA\RampDataLog.xlsm"
colls = pd.read_excel(f_path, sheet_name="data")

colls.Compliance.value_counts() / len(colls)

[" ".join(a.split()) for a in colls.iloc[8].Notes.split(",")]

api_key = "AIzaSyCIEkEPJdT6JPBn-igNOxm2lc83I9BJI8Y"
gmaps = gm.Client(key=api_key)
address_test = "1010 Emerald Ave, Haddon Township, NJ 08108"
geocode_test = gmaps.geocode(address_test)

lat = geocode_test[0]["geometry"]["location"]["lat"]
lng = geocode_test[0]["geometry"]["location"]["lng"]

# ALTERNATIVELY #

import requests

url_boil = 'https://maps.googleapis.com/maps/api/geocode/json?address='
url_add = 'Fern+Ave+%26+Burrwood+Ave,+Haddon+Township,+NJ'
#url_add = '1010+Emerald+Avenue,+Haddon+Township,+NJ'
url_test = url_boil + url_add
url_test += '&key=' + api_key

response = requests.get(url_test)
resp_json = response.json()

lat = resp_json['results'][0]['geometry']['location']['lat']
lng = resp_json['results'][0]['geometry']['location']['lng']

# ALTERNATIVELY #

# use Nominatim and GeoPandas for geocoding
