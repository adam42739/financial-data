import metalog
import os
import pandas
import datetime

import metalog.metalog

DB_NAME = "data"


def run_ticker(start_date, ticker, days_back, days_change, dim, db_name):
    results = pandas.DataFrame({"Date": [], ticker: []})
    mprices = metalog.MetalogPrices(db_name, ticker)
    date = max(start_date, mprices.start_date) + datetime.timedelta(
        days_back + days_change
    )
    end_date = min(datetime.datetime.today(), mprices.end_date) - datetime.timedelta(1)
    while date < end_date:
        date_string = datetime.datetime.strftime(date, "%Y%m%d")
        if date_string in mprices.dates_string:
            metalog, next_day = mprices.compute_metalog(
                date - datetime.timedelta(days_back + days_change),
                date,
                days_change,
                dim,
            )
            cdf = metalog.cdf(next_day)
            new_row = pandas.DataFrame({"Date": [date], ticker: [cdf]})
            results = pandas.concat([results, new_row])
            print(date)
        date += datetime.timedelta(1)
    results.to_csv("models/baseline_results/" + ticker + ".csv", index=False)


def run(start_date, days_back, days_change, dim, db_name):
    for path in os.listdir(db_name + "/" + "yahoo_prices/"):
        ticker = path.replace(".csv", "")
        run_ticker(start_date, ticker, days_back, days_change, dim, db_name)
        break


run(datetime.datetime(2020, 1, 1), 100, 1, 5, DB_NAME)
