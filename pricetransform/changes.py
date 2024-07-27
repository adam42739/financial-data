import yahoo
import pandas
import math
import data_logs

DB_FOLDER = "price_transforms/changes/"


def read_changes(db_name, ticker):
    path = db_name + "/" + DB_FOLDER + ticker + ".csv"
    return pandas.read_csv(path)


def compute_changes(db_name, ticker):
    changes = PriceChanges(db_name, ticker)
    changes.compute_changes()
    changes.write_changes()


def compute_all_changes(db_name):
    log = data_logs.read_log(db_name, data_logs.YAHOO_PRICE_LOG)
    tickers = log.keys()
    for ticker in tickers:
        compute_changes(db_name, ticker)


class PriceChanges:
    def __init__(self, db_name, ticker):
        self.ticker = yahoo.ticker_format(ticker)
        self.db_name = db_name
        self.prices = yahoo.get_prices(ticker, db_name)

    def compute_changes(self):
        self.prices = self.prices.sort_values(by=["Date"], ascending=False).reset_index(
            drop=True
        )
        self.changes_dict = {"Date": [], "Change": []}
        for i in range(0, len(self.prices.index) - 1):
            self.changes_dict["Date"].append(self.prices["Date"][i])
            close_f = self.prices["Close"][i]
            close_i = self.prices["Close"][i + 1]
            self.changes_dict["Change"].append(math.log(close_f / close_i))
        self.changes = pandas.DataFrame(self.changes_dict)

    def write_changes(self):
        path = self.db_name + "/" + DB_FOLDER + self.ticker + ".csv"
        self.changes.to_csv(path, index=False)
