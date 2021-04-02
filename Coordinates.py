import googlemaps
import pandas as pd
import re

# This is where we have to put API key from Google Maps
# Just for git
key = 'Add new API Key'
gmaps = googlemaps.Client(key)

# Reading Excel data provided by Dante
df = pd.read_excel('UC_210312060608.xlsx')

# This function will get UC from that long uc colums
def uc(i):
    return re.search('-(.+?)#', i).group(1).strip()

df['uc'] = df['Nombre de la UC'].apply(uc)
#df['query'] = df['uc'] + " " + df['Institución'] + " " + df['Entidad Federativa']
df['query'] = df['Institución'] + " " + df['Entidad Federativa']

df2 = df.drop_duplicates('query', keep='first')[['query']]

# This function will get required details using google maps API
def place_coord(i):
    try:
        details = gmaps.places(i)
        return details['results'][0]['geometry']['location']
    except:
        return 'No Info Found'

# This will send 1100+ queries to google maps. Will take almost 15-20 mins
df2['data'] = df2['query'].apply(place_coord)

df3 = df.merge(df2, how='inner', on='query')

# Saving file to the CSV File
df3.to_csv('UC with Coords.csv', index = False, encoding = 'utf-8-sig')
