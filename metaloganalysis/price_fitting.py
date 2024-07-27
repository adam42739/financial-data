import metaloganalysis
import yahoo
import math
import datetime


class MetalogPrices:
    def __init__(self, db_name, ticker):
        self.ticker = ticker
        self.prices = yahoo.get_prices(ticker, db_name)
        self.start_date = self.prices["Date"].min()
        self.end_date = self.prices["Date"].max()
        self.dates_string = self.prices["Date"].dt.strftime("%Y%m%d").to_list()

    def compute_metalog(self, start_date, end_date, change_size, dim):
        bmap = (self.prices["Date"] <= end_date + datetime.timedelta(1)) & (
            self.prices["Date"] >= start_date
        )
        pframe = (
            self.prices[bmap]
            .sort_values(by=["Date"], ascending=False)
            .reset_index(drop=True)
        )
        x = []
        next_day = math.log(pframe["Close"][0] / pframe["Close"][1])
        for i in range(1, len(pframe.index)):
            if i + change_size < len(pframe.index):
                close_f = pframe["Close"][i]
                close_i = pframe["Close"][i + change_size]
                x.append(math.log(close_f / close_i))
            else:
                break
        mlog = metaloganalysis.Metalog(dim)
        mlog.fit(x)
        return mlog, next_day
