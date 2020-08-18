"""
Contains a set of utility function to process data
"""

import csv
import datetime
import numpy as np
import pandas as pd
import h5py

start_date = '2020-03-20 02-PM'
end_date = '2020-06-20 01-PM'
date_format = '%Y-%m-%d %I-%p'
start_datetime = datetime.datetime.strptime(start_date, date_format)
end_datetime = datetime.datetime.strptime(end_date, date_format)
number_datetime = ((end_datetime - start_datetime).days) * 24 + (end_datetime - start_datetime).seconds/3600 + 1

def normalize(x):
    """ Create a universal normalization function across close/open ratio
    Args:
        x: input of any shape
    Returns: normalized data
    """
    return (x - 1) * 100

def create_spread(beta, alpha, first_currency, second_currency, start_datetime):
    BTC_df = pd.read_csv('Bitstamp_'+first_currency+'USD_1h.csv', skiprows = 1)
    XRP_df = pd.read_csv('Bitstamp_'+second_currency+'USD_1h.csv', skiprows = 1)
    BTC_df['Date'] = BTC_df['Date'].apply(lambda x: datetime.datetime.strptime(x, date_format))
    XRP_df['Date'] = XRP_df['Date'].apply(lambda x: datetime.datetime.strptime(x, date_format))
    BTC_df = BTC_df[BTC_df['Date'] >= start_datetime]
    XRP_df = XRP_df[XRP_df['Date'] >= start_datetime]
    BTC_df.sort_values(by = 'Date', inplace = True)
    XRP_df.sort_values(by = 'Date', inplace = True)
    BTC_df.set_index(['Date'], inplace = True)
    XRP_df.set_index(['Date'], inplace = True)

    spread_df = pd.DataFrame(index = BTC_df.index, columns = ['Open', 'High', 'Low', 'Close'])
    spread_df['Open'] = BTC_df['Open'] + beta * XRP_df['Open']+alpha
    spread_df['High'] = BTC_df['High'] + beta * XRP_df['High']+alpha
    spread_df['Low'] = BTC_df['Low'] + beta * XRP_df['Low']+alpha
    spread_df['Close'] = BTC_df['Close'] + beta * XRP_df['Close']+alpha
    return spread_df

def create_dataset(spread_df, filepath = 'datasets/stocks_history_target.h5'):
    history = np.empty(shape=(1, len(spread_df), 4), dtype=np.float)
    for row in range(len(spread_df)):
        history[0][row] = spread_df.iloc[row, :4].values
    abbreviation = ['BTCXRP']
    write_to_h5py(history, abbreviation, filepath)
    return history, abbreviation

def write_to_h5py(history, abbreviation, filepath='datasets/stocks_history_target.h5'):
    """ Write a numpy array history and a list of string to h5py
    Args:
        history: (N, timestamp, 5)
        abbreviation: a list of stock abbreviations
    Returns:
    """
    with h5py.File(filepath, 'w') as f:
        f.create_dataset('history', data=history)
        abbr_array = np.array(abbreviation, dtype=object)
        string_dt = h5py.special_dtype(vlen=str)
        f.create_dataset("abbreviation", data=abbr_array, dtype=string_dt)

def create_target_dataset(target_list, filepath='datasets/stocks_history_target.h5'):
    """ Create history datasets
    Args:
        target_list:
        filepath:
    Returns:

    """
    history_all, abbreviation_all = read_stock_history()
    history = None
    for target in target_list:
        data = np.expand_dims(history_all[abbreviation_all.index(target)], axis=0)
        if history is None:
            history = data
        else:
            history = np.concatenate((history, data), axis=0)
    write_to_h5py(history, target_list, filepath=filepath)


def read_stock_history(filepath='datasets/stocks_history_target.h5'):
    """ Read data from extracted h5
    Args:
        filepath: path of file
    Returns:
        history:
        abbreviation:
    """
    with h5py.File(filepath, 'r') as f:
        history = f['history'][:]
        abbreviation = f['abbreviation']
#        print(abbreviation)
        abbreviation = [abbr.decode('utf-8') for abbr in abbreviation]
    return history, abbreviation

def index_to_date(index):
    """
    Args:
        index: the date from start-date (2020-03-20 14:00:00)
    Returns: string of date
    """
    return str(start_datetime + datetime.timedelta(hours = index))
#    return pd.to_datetime(str(start_datetime + datetime.timedelta(hours = index)))

def date_to_index(dt):
    """
    Args:
        datetime: in format of 2020-04-20 14:00:00

    Returns: the days from start_date: 2020-03-20 14:00:00
    """
    return int(((dt - start_datetime).days) * 24 + (dt - start_datetime).seconds/3600)

if __name__ == '__main__':
    beta = - 54832.949188
    alpha = 4830.852766
    first_currency = 'BTC'
    second_currency = 'XRP'
    spread_df = create_spread(beta, alpha, first_currency, second_currency, start_datetime)
    history, abbre = create_dataset(spread_df)
