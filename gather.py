# api test
import pandas as pd
import io
import time
import requests
import zipfile
import zlib
import urllib.request

urllib.request.urlretrieve('http://geoportal1-ons.opendata.arcgis.com/datasets/48d0b49ff7ec4ad0a4f7f8188f6143e8_3.zip',
                           'constituencies_super_generalised_shapefile.zip')
with zipfile.ZipFile('constituencies_super_generalised_shapefile.zip', 'r') as zip_ref:
    zip_ref.extractall('constituencies_super_generalised_shapefile')

petition_list = pd.read_csv(
    'https://petition.parliament.uk/archived/petitions.csv?parliament=1&state=published')
url_list = petition_list['URL'].tolist()

count, start = 0, time.time()
signatures, mp, errors = [], [], []

for petition_url in url_list:
    try:
        response = pd.read_json(petition_url + '.json')
        response = pd.DataFrame.from_dict(response.iloc[0, 0], orient='index')
        created_at = response.loc['created_at', 0]
        response = pd.DataFrame.from_dict(
            response.loc['signatures_by_constituency', 0])
        response['created'] = created_at

        signatures.extend(
            response[['ons_code', 'signature_count', 'created']].values.tolist())
        mp.extend(
            response[['ons_code', 'name', 'mp']].values.tolist())
    except:
        errors.append(petition_url)

    count += 1
    if count % 250 == 0:
        print('{} files reached in {} s sleeping for 10s'.format(
            count, time.time() - start))
        time.sleep(10)

signatures = pd.DataFrame(
    signatures, columns=['ons_code', 'signature_count', 'date'])
signatures['date'] = pd.to_datetime(signatures['date'])
signatures = signatures.set_index('date').groupby(
    [pd.TimeGrouper(freq='M'), 'ons_code']).sum().reset_index().sort_values(['ons_code', 'date'])
signatures['date'] = signatures.date.dt.to_period('M')

mp = pd.DataFrame(mp, columns=['ons_code', 'constituency', 'mp']).drop_duplicates(
    'ons_code', keep='last')
mp = mp.replace('Ynys M?n', 'Ynys Mon')

population = pd.read_excel(
    'http://data.parliament.uk/resources/constituencystatistics/Population-by-age.xlsx', 'Data')
population = population[['ONSConstID', 'RegionName', 'PopTotalConstNum']].rename(
    columns={'ONSConstID': 'ons_code', 'RegionName': 'region', 'PopTotalConstNum': 'population'})

eu = pd.read_excel(
    'https://secondreading.parliament.uk/wp-content/uploads/2017/02/eureferendum_constitunecy.xlsx', 'DATA')
eu.columns = ['ons_code', 'constituency', 'ch_leave_estimate',
              'result_known', 'known_leave', 'leave_figure']
eu = eu.loc[:, ['ons_code', 'leave_figure']].iloc[7:]
eu['stay_figure'] = 1 - eu['leave_figure']
eu = eu.drop('leave_figure', axis=1)

hex = pd.read_json(
    'https://odileeds.org/projects/hexmaps/maps/constituencies.hexjson')
hex = hex.merge(hex['hexes'].apply(pd.Series),
                left_index=True, right_index=True).reset_index()
hex = hex.rename(columns={'index': 'ons_code', 'q': 'hex_x', 'r': 'hex_y'}).loc[:, [
    'ons_code', 'hex_x', 'hex_y']]

region_selector = {'region': ['South West', 'South East', 'London',
                              'Wales', 'West Midlands', 'East Midlands',
                              'East of England', 'North West', 'Yorkshire and The Humber',
                              'Northern Ireland', 'North East', 'Scotland'],
                   'region_x': [2, 3, 4, 2, 3, 4, 5, 3, 4, 1, 4, 3],
                   'region_y': [1, 1, 1, 2, 2, 2, 2, 3, 3, 4, 4, 5]}
region_selector = pd.DataFrame(data=region_selector)

master = signatures.copy()
master = master.merge(mp, how='left', on='ons_code')
master = master.merge(population, how='left', on='ons_code')
master = master.merge(eu, how='left', on='ons_code')
master = master.merge(hex, how='left', on='ons_code')
master = master.merge(region_selector, how='left', on='region')

master.to_csv('uk_petitions_master.csv', index=False)


# To run without downloading run these lines, else comment below line
signatures = pd.read_csv('signatures_backup.csv.zip')
mp = pd.read_csv('mp_backup.csv.zip')
