import pandas
import os
import sys

sys.path.append("/Users/adamlynch/Documents/Hobby Work/Financial Data/")
import yahoopricescraper

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


def get_prices(ticker, db_dir):
    ticker = yahoopricescraper.ticker_format(ticker)
    path = db_dir + ticker + ".csv"
    if os.path.isfile(path):
        df = pandas.read_csv(path)
        df["Date"] = yahoopricescraper.YAHOO_START_DATE + pandas.to_timedelta(
            df["Date"], unit="d"
        )
        return df
    else:
        return DEFAULT_DF


def parse_df(df):
    df["Date"] = pandas.to_datetime(df["Date"], format="%Y-%m-%d")
    df["Date"] = (df["Date"] - yahoopricescraper.YAHOO_START_DATE).dt.days
    return df


def update_db_from_downloads(tickers, downloads_dir, db_dir):
    for ticker in tickers:
        ticker = yahoopricescraper.ticker_format(ticker)
        downloads_path = downloads_dir + ticker + ".csv"
        df = pandas.read_csv(downloads_path)
        os.remove(downloads_path)
        df = parse_df(df)
        db_path = db_dir + ticker + ".csv"
        df.to_csv(db_path, index=False)
