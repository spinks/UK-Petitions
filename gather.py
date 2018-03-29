# Imports
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
import requests
import os
import json
import time
import zipfile
import zlib
import urllib.request

# Download ZIP Files and Directory of Petitions

# Petition Directory
urllib.request.urlretrieve('https://petition.parliament.uk/archived/petitions.csv?parliament=1&state=published',
                           'published-petitions-2015–2017.csv')

# Map Shapefiles
# Download
urllib.request.urlretrieve('http://geoportal1-ons.opendata.arcgis.com/datasets/48d0b49ff7ec4ad0a4f7f8188f6143e8_3.zip',
                           'constituencies_super_generalised_shapefile.zip')
# Unzip
with zipfile.ZipFile('constituencies_super_generalised_shapefile.zip', 'r') as zip_ref:
    zip_ref.extractall('constituencies_super_generalised_shapefile')


# Map Hexfiles
urllib.request.urlretrieve('http://www.thedataschool.co.uk/wp-content/uploads/2016/02/2015-UK-General-Election-Hexbin-Data.xlsx',
                           '2015-UK-General-Election-Hexbin-Data.xlsx')

# Population Data
urllib.request.urlretrieve('http://data.parliament.uk/resources/constituencystatistics/Population-by-age.xlsx',
                           'Population-by-age.xlsx')

# EU Referendum Data
urllib.request.urlretrieve('https://secondreading.parliament.uk/wp-content/uploads/2017/02/eureferendum_constitunecy.xlsx',
                           'eureferendum_constitunecy.xlsx')


# Downloading of Petition Data (can take around 2 hours)

# Read in directory
petition_list = pd.read_csv('published-petitions-2015–2017.csv')

# Set up outfile and download urls
filename = 'petitions_json.txt'
json_add = '.json'

all_petitions = []

count = 0
start = time.time()

for petition_url in petition_list['URL'].tolist():
    response = requests.get(petition_url + json_add).json()
    all_petitions.append(response)

    count += 1
    if count % 250 == 0:
        time.sleep(5)
        print('{} requests reached in {} s sleeping for 5s'.format(
            count, time.time() - start))


with open(filename, mode='w') as file:
    json.dump(all_petitions, file)
    print('Finished Writing JSON file, {} files saved'.format(len(all_petitions)))

# Make compressed version of petition_json.txt
zipfile.ZipFile('petitions_json.txt.zip', 'w',
                zipfile.ZIP_DEFLATED).write('petitions_json.txt')

# Read in and clean
petitions = pd.read_json('petitions_json.txt')
petition_data = json_normalize(petitions['data'])
petition_data.columns = petition_data.columns.str.replace('attributes.', '')

# Extract Constituency Data
constituency_data = []

for index, row in petition_data.iterrows():
    for entry in range(len(row['signatures_by_constituency'])):
        constituency_info = (row['signatures_by_constituency'][entry]['name'],
                             row['signatures_by_constituency'][entry]['mp'],
                             row['signatures_by_constituency'][entry]['ons_code'])
        if constituency_info not in constituency_data:
            constituency_data.append(constituency_info)

constituency_data = pd.DataFrame(
    constituency_data, columns=('name', 'mp', 'ons_code'))

# Votes by Constituency Data

votes_by_constituency_data = petition_data[['id']].copy()

for code in constituency_data['ons_code'].values.tolist():
    votes_by_constituency_data[code] = np.nan

# Read petition json and flatten into counts (can take around 10 min)
count = 0
start = time.time()

for index, row in petition_data.iterrows():
    for entry in range(len(row['signatures_by_constituency'])):
        constituency_signature_info = (row['signatures_by_constituency'][entry]['ons_code'],
                                       row['signatures_by_constituency'][entry]['signature_count'])
        votes_by_constituency_data.loc[index,
                                       constituency_signature_info[0]] = constituency_signature_info[1]

    count += 1
    if count % 500 == 0:
        print(count, time.time() - start, 's')


# Export raw petition_data and clean constituency_data
constituency_data.to_csv('constituency_data.csv')
petition_data.to_csv('petition_data.csv')

# Restructure votes_by_constituency_data
petition_data.loc[:, ['created_at', 'closed_at']] = petition_data.loc[:, [
    'created_at', 'closed_at']].apply(pd.to_datetime)

# Create dict of id for each month and replace id in votes_by_constituency_data with the month
month_dict = petition_data.set_index('created_at').groupby(
    pd.Grouper(freq='M'))['id'].apply(list).to_dict()
month_dict = {val: key for key in month_dict for val in month_dict[key]}

votes_by_constituency_data['id'].replace(month_dict, inplace=True)

# Renaming and fixing data type
votes_by_constituency_data = votes_by_constituency_data.rename(
    columns={'id': 'created_at_month'})
votes_by_constituency_data['created_at_month'] = pd.to_datetime(
    votes_by_constituency_data['created_at_month'])
votes_by_constituency_data = votes_by_constituency_data.set_index('created_at_month')\
                                                       .groupby(pd.Grouper(freq='M')).sum()

# Transpose and stack
votes_by_constituency_data = votes_by_constituency_data.transpose()
votes_by_constituency_data.index.names = ['ons_code']

votes_by_constituency_data = votes_by_constituency_data.stack()
votes_by_constituency_data.name = 'vote_count'
votes_by_constituency_data = votes_by_constituency_data.reset_index().set_index('ons_code')

# Save cleaned file
votes_by_constituency_data.to_csv('votes_by_constituency_data.csv')


# Clean population data
population_data = pd.read_excel('Population-by-age.xlsx', 'Data')
population_data = population_data[[
    'ONSConstID', 'RegionName', 'PopTotalConstNum']].copy()
population_data.to_csv('population_data.csv')


# Clean eu referendum data
eu = pd.read_excel('eureferendum_constitunecy.xlsx', 'DATA')
eu.columns = ['ons_code', 'constituency', 'ch_leave_estimate',
              'result_known', 'known_leave', 'leave_figure']
eu = eu.iloc[7:]
eu[['ons_code', 'leave_figure']].to_csv('eu_referendum_data.csv')


# Create custom region selector csv
custom_region_selector = {'Region': ['South West', 'South East', 'London',
                                     'Wales', 'West Midlands', 'East Midlands',
                                     'East of England', 'North West', 'Yorkshire and The Humber',
                                     'Northern Ireland', 'North East', 'Scotland'],
                          'x': [2, 3, 4, 2, 3, 4, 5, 3, 4, 1, 4, 3],
                          'y': [1, 1, 1, 2, 2, 2, 2, 3, 3, 4, 4, 5]}
custom_region_selector = pd.DataFrame(
    data=custom_region_selector).set_index('Region')
custom_region_selector.to_csv('custom_region_selector.csv')
