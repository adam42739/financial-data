from selenium import webdriver
from selenium.webdriver import Chrome
import datetime
import time
import os
import data_logs
import pandas

DB_DIR = "yahoo_prices"

YAHOO_START_DATE = datetime.datetime(1970, 1, 1)
YAHOO_DATE_ITER = 86400

DEFAULT_DF = pandas.DataFrame(
    {
        "Date": [],
        "Open": [],
        "High": [],
        "Low": [],
        "Close": [],
        "Adj Close": [],
        "Volume": [],
    }
)


def ticker_format(ticker):
    return ticker.upper().replace(".", "-")


def get_prices(ticker, db_name):
    ticker = ticker_format(ticker)
    path = db_name + "/" + DB_DIR + "/" + ticker + ".csv"
    if os.path.isfile(path):
        df = pandas.read_csv(path)
        df["Date"] = YAHOO_START_DATE + pandas.to_timedelta(df["Date"], unit="d")
        return df
    else:
        return DEFAULT_DF


def download_tickers_to_db(
    tickers, start_date, end_date, db_name, downloads_dir, wait_time=1
):
    driver = Driver()
    return driver.download_tickers_to_db(
        tickers, start_date, end_date, db_name, downloads_dir, wait_time
    )


def parse_df(df):
    df["Date"] = pandas.to_datetime(df["Date"], format="%Y-%m-%d")
    df["Date"] = (df["Date"] - YAHOO_START_DATE).dt.days
    return df


def update_db_from_downloads(ticker, downloads_dir, db_name):
    downloads_path = downloads_dir + ticker + ".csv"
    df = pandas.read_csv(downloads_path)
    df = parse_df(df)
    db_path = db_name + "/" + DB_DIR + "/" + ticker + ".csv"
    df.to_csv(db_path, index=False)
    os.remove(downloads_path)


class Driver:
    LINK1 = "https://query1.finance.yahoo.com/v7/finance/download/"
    LINK2 = "?period1="
    LINK3 = "&period2="
    LINK4 = "&interval=1d&events=history&includeAdjustedClose=true"

    def __init__(self):
        self.driver = Chrome()
        self.driver.maximize_window()

    def __del__(self):
        self.driver.quit()

    def verify_download(self, ticker, downloads_dir):
        path = downloads_dir + ticker_format(ticker) + ".csv"
        return os.path.exists(path)

    def download_ticker(self, ticker, start_date, end_date, downloads_dir, wait_time=1):
        number1 = str((start_date - YAHOO_START_DATE).days * YAHOO_DATE_ITER)
        number2 = str((end_date - YAHOO_START_DATE).days * YAHOO_DATE_ITER)
        url = (
            Driver.LINK1
            + ticker_format(ticker)
            + Driver.LINK2
            + number1
            + Driver.LINK3
            + number2
            + Driver.LINK4
        )
        self.driver.get(url)
        time.sleep(wait_time)
        if not self.verify_download(ticker, downloads_dir):
            raise Exception()

    def download_tickers_to_db(
        self, tickers, start_date, end_date, db_name, downloads_dir, wait_time=1
    ):
        failed = []
        data = data_logs.read_log(db_name, data_logs.YAHOO_PRICE_LOG)
        today = datetime.datetime.strftime(datetime.datetime.today(), "%Y%m%d")
        for ticker in tickers:
            ticker = ticker_format(ticker)
            if ticker in data:
                if today in data[ticker]:
                    continue
            try:
                self.download_ticker(
                    ticker, start_date, end_date, downloads_dir, wait_time
                )
                update_db_from_downloads(ticker, downloads_dir, db_name)
                if ticker not in data.keys():
                    data[ticker] = []
                data[ticker].append(today)
            except:
                failed.append(ticker)
        data_logs.write_log(db_name, data, data_logs.YAHOO_PRICE_LOG)
        return failed
