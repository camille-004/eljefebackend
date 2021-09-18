import dateutil.parser
import json
import os
import requests
import time

from alpha_vantage.timeseries import TimeSeries
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

CALLS_PER_MINUTE = 5
TIME_SLEEP = 60

DATA_DIR = 'data/'
TICKERS = ['MMM', 'ABT', 'ABBV', 'ABMD', 'ACN', 'AAPL', 'GOOG', 'AMC', 'LUV',
           'AMZN']
TOKEN = os.getenv('API_KEY')

START_DATE = dateutil.parser.parse('2016-01-01')


class AlphaAPIFetch:
    """Class to fetch historical stock data after a certain start date and
    fundamental data for the given tickers"""

    def __init__(self, tickers=TICKERS, start_date=START_DATE, token=TOKEN):
        self.tickers = tickers
        self.start_date = start_date
        self.token = token

        self.max_calls = CALLS_PER_MINUTE
        self.time_sleep = TIME_SLEEP
        self.n_requests = 0

        self.get_stock_data()
        self.get_fundamentals()

    def get_stock_data(self):
        """
        A method to get financial data for a given list of tickers and save
        to a JSON file
        """
        for ticker in tqdm(self.tickers):
            self.n_requests += 1
            if self.n_requests > self.max_calls - 1:
                time.sleep(TIME_SLEEP)
                self.n_requests = 0
            ts = TimeSeries(key=self.token, output_format='pandas')
            stocks = ts.get_daily_adjusted(ticker, outputsize='full')[0]
            stocks.columns = stocks.columns.map(
                lambda x: x.split('.')[1].strip())
            stocks = stocks[stocks.index > self.start_date]
            stocks.reset_index(level=0, inplace=True)
            stocks['date'] = stocks['date'].dt.strftime('%Y-%m-%d')
            stocks.to_json(
                f'{DATA_DIR}{ticker}_financial.json',
                orient='records',
                indent=4,
                date_unit='ns'
            )

    def get_fundamentals(self):
        """
        A method to get fundamental company data for a given list of tickers
        and save to a JSON file
        """
        fundamentals = []
        for ticker in tqdm(self.tickers):
            self.n_requests += 1
            if self.n_requests > self.max_calls - 1:
                time.sleep(self.time_sleep)
                self.n_requests = 0
            url = f'https://www.alphavantage.co/query?function=OVERVIEW' \
                  f'&symbol={ticker}&apikey={self.token}'
            r = requests.get(url)
            fundamentals.append(r.json())
        with open(f'{DATA_DIR}fundamentals.json', 'w') as f:
            json.dump(fundamentals, f, indent=4)


if __name__ == '__main__':
    AlphaAPIFetch()
