import metalog
import yahoo
import math


class MetalogPrices:
    def __init__(self, db_name, ticker):
        self.ticker = ticker
        self.prices = yahoo.get_prices(ticker, db_name)
        self.start_date = self.prices["Date"].min()
        self.end_date = self.prices["Date"].max()

    def compute_metalog(self, start_date, end_date, change_size, dim):
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
        if start_date not in self.metalogs:
            self.metalogs[start_date] = {}
        if end_date not in self.metalogs[start_date]:
            self.metalogs[start_date][end_date] = {}
        mlog = metalog.Metalog(dim)
        mlog.fit(x)
        return mlog
