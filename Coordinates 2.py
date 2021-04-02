import pandas as pd
import googlemaps

df = pd.read_csv('UC with Coords.csv')

df2 = df.drop_duplicates('query')
df3 = df2[df2['data'] == 'No Info Found']

# This is to get state full names from codes
mex = pd.read_html(
    'https://en.wikipedia.org/wiki/Template:Mexico_State-Abbreviation_Codes')
mex = mex[0]

df4 = df3.merge(mex, how='inner', left_on='Entidad Federativa',
                right_on='3-letter code(ISO 3166-2:MX)')
df4['query2'] = df4['Institución'] + " " + df4['Name of federative entity']


key = 'AIzaSyBhLdCLNcL8MAoiPOQNmddMzAM9N3-a6dU'
gmaps = googlemaps.Client(key)

# Defining functions


def place_coord(i):
    try:
        details = gmaps.places(i)
        return details['results'][0]['geometry']['location']
    except:
        return 'No Info Found'


def place_coord2(i):
    try:
        details = gmaps.geocode(i)
        return details[0]['geometry']['location']
    except:
        return 'No Info Found'


# First running of scrapper
df4['data2'] = df4['query2'].apply(place_coord)

# Next query
df4['query3'] = df4['query2'] + " " + df4['Conventionalabbreviation']

# Second scrapper
df4['data3'] = df4['query3'].apply(place_coord2)

# Another query
df4['query4'] = df4['Siglas de la Institución'] + " " + \
    df4['Name of federative entity'] + " " + df4['Conventionalabbreviation']
#df4['data_temp'] = df4['data3']
df5 = df4[(df4['data2'] == 'No Info Found') & (
    df4['data3'] == 'No Info Found')][['query4']]

# Third scrapper
df5['data5'] = df5['query4'].apply(place_coord2)

# Merging back dataests
merged = df5.merge(df4, how='right', on='query4')[
    ['Name of federative entity', 'Conventionalabbreviation', 'query', 'query2', 'query3', 'query4', 'data', 'data2', 'data3', 'data5']]
merged.loc[merged['data3'] == 'No Info Found', 'data3'] = merged['data2']
merged.loc[merged['data3'] == 'No Info Found', 'data3'] = merged['data5']
merged.drop(['data', 'data2', 'data5'], 1, inplace=True)

#merged2 = df2.merge(merged,how='left',on='query')[['query','query2','query3','query4','data','data3']]
merged2 = df2.merge(merged, how='left', on='query')
merged2.loc[merged2['data'] == 'No Info Found', 'data'] = merged2['data3']
# without edomex
df_w_edomex = merged2[merged2['Entidad Federativa'] != 'MX-MEX']

# Correction for edomex
edomex = merged2[merged2['Entidad Federativa'] == 'MX-MEX']
edomex['query5'] = edomex['Siglas de la Institución'] + \
    " " + edomex['Institución'] + " " + "Edomex"
edomex['data5'] = edomex['query5'].apply(place_coord2)
edomex.loc[edomex['data5'] != 'No Info Found', 'data'] = edomex['data5']
edomex.drop(['query5', 'data5'], axis=1, inplace=True)

merged3 = df_w_edomex.append(edomex)[['query', 'data']]

df_f = df.drop('data', 1).merge(merged3, how='inner', on='query')

df_f.to_csv('UC with Coords_Updated.csv', index=False, encoding='utf-8-sig')
