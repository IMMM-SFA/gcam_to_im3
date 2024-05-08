import gcamreader
import numpy as np
import pandas as pd
from pathlib import Path
from gdp_deflator import *
import os

def get_query_by_name(queries, name):
    return next((x for x in queries if x.title == name), None)

def get_carbon_price(
    path_to_gcam_database:str,
    gcam_file_name:str,
    gcam_scenario:str,
    capacity_crosscheck:pd.DataFrame, 
    save_output=False,
    gcam_query_name = "CO2 prices",
    path_to_query_file: str = './elec_queries.xml',
    ):
    # create connection to gcam db
    conn = gcamreader.LocalDBConn(path_to_gcam_database, gcam_file_name)
    
    # parse the queries file
    queries = gcamreader.parse_batch_query(path_to_query_file)
    
    # collect dataframe
    carbon_price = conn.runQuery(get_query_by_name(queries, gcam_query_name))

    # select correct market
    carbon_price = carbon_price[carbon_price.market == 'globalCO2']

    # convert 1990$ to 2015$ following gdp_deflator
    carbon_price['value'] = carbon_price['value'] * deflate_gdp(2015, 1990)

    # drop variables no longer needed
    carbon_price = carbon_price.drop(['scenario', 'market', 'Units'], axis=1)

    # rename column
    carbon_price.rename(columns={
            'Year': 'x',
            }, inplace=True)

    # map to new capacity rows by year to apply to all technologies, all states, and all years
    carbon_price = pd.merge(capacity_crosscheck, carbon_price, how='left', on=['x'])

    # fill in missing columns
    carbon_price['units'] = 'Carbon Price (2015 USD/tonCarbon)'
    carbon_price['param'] = 'carbon_price_2015USDperTonCarbon'

    if save_output:
        os.makedirs(Path('./extracted_data'), exist_ok=True)
        carbon_price.to_csv(Path(f'./extracted_data/{gcam_scenario}_carbon_price.csv'), index=False)
    else:
       pass

    return carbon_price


def _get_carbon_price(
      path_to_gcam_database,
      gcam_file_name,
      gcam_scenario):
  
  get_carbon_price(
     path_to_gcam_database,
     gcam_file_name,
     gcam_scenario)


if __name__ == "__main__":
  _get_carbon_price()