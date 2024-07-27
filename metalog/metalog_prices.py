import metalog
import yahoo
import math
import datetime
import pricetransform


class MetalogPrices:
    def __init__(self, db_name, ticker):
        self.ticker = ticker
        self.changes = pricetransform.changes.read_changes(db_name, ticker)
        self.start_date = self.changes["Date"].min()
        self.end_date = self.changes["Date"].max()

    def compute_metalogs(self, ):
        return

mp = MetalogPrices("data", "aapl")
a = 0
