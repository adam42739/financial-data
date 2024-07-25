import pandas
import datetime
import os

CBOE_START_DATE = datetime.datetime(1970, 1, 1)

DEFAULT_DF = pandas.DataFrame(
    {
        "Expiration": [],
        "CBid": [],
        "CAsk": [],
        "CVolumne": [],
        "COI": [],
        "Strike": [],
        "PBid": [],
        "PAsk": [],
        "PVolume": [],
        "POI": [],
    }
)


def ticker_format(ticker):
    return ticker.lower().replace("-", ".")


CBOE_FILE_ENDING = "_quotedata.csv"


def get_options(ticker, date, db_dir):
    ticker = ticker_format(ticker)
    date_str = str(date.year) + str(date.month).zfill(2) + str(date.day).zfill(2)
    path = db_dir + ticker + date_str + ".csv"
    if os.path.isfile(path):
        df = pandas.read_csv(path)
        df["Expiration"] = CBOE_START_DATE + pandas.to_timedelta(
            df["Expiration"], unit="d"
        )
        return df
    else:
        return DEFAULT_DF


def parse_df(df):
    df = df.drop(
        [
            "Calls",
            "Last Sale",
            "Net",
            "IV",
            "Delta",
            "Gamma",
            "Puts",
            "Last Sale.1",
            "Net.1",
            "IV.1",
            "Delta.1",
            "Gamma.1",
        ],
        axis=1,
    )
    df = df.rename(
        columns={
            "Expiration Date": "Expiration",
            "Bid": "CBid",
            "Ask": "CAsk",
            "Volume": "CVolume",
            "Open Interest": "COI",
            "Bid.1": "PBid",
            "Ask.1": "PAsk",
            "Volume.1": "PVolume",
            "Open Interest.1": "POI",
        }
    )
    df["Expiration"] = pandas.to_datetime(df["Expiration"], format="%a %b %d %Y")
    df["Expiration"] = (df["Expiration"] - CBOE_START_DATE).dt.days
    return df


def update_db_from_downloads(tickers, downloads_dir, db_dir, date):
    for ticker in tickers:
        ticker = ticker_format(ticker)
        downloads_path = downloads_dir + ticker + CBOE_FILE_ENDING
        df = pandas.read_csv(downloads_path, header=2)
        os.remove(downloads_path)
        df = parse_df(df)
        date_str = str(date.year) + str(date.month).zfill(2) + str(date.day).zfill(2)
        db_path = db_dir + ticker + date_str + ".csv"
        df.to_csv(db_path, index=False)
