import metalog
import yahoo
import math


class MetalogPrices:
    def __init__(self, db_name, ticker):
        self.ticker = ticker
        self.prices = yahoo.get_prices(ticker, db_name)
        self.metalogs = {}

    def copmute_metalog(self, start_date, end_date, change_size, dim, metalog_key):
        bmap = (self.prices["Date"] < end_date) & (self.prices["Date"] >= start_date)
        pframe = (
            self.prices[bmap]
            .sort_values(by=["Date"], ascending=False)
            .reset_index(drop=True)
        )
        x = []
        for i in range(0, len(pframe.index)):
            if i + change_size < len(pframe.index):
                close_f = pframe["Close"][i]
                close_i = pframe["Close"][i + change_size]
                x.append(math.log(close_f / close_i))
            else:
                break
        self.metalogs[metalog_key] = metalog.Metalog(dim)
        self.metalogs[metalog_key].fit(x)
