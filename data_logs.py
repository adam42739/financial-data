import json
import datetime

CBOE_OPTION_LOG = "cboe_options_log.json"
YAHOO_PRICE_LOG = "yahoo_prices_log.json"


def clear_log(dbname, log):
    with open(dbname + "/" + log, "w") as file:
        file.write("{}")


def read_log(dbname, log):
    data = None
    with open(dbname + "/" + log, "r") as file:
        data = json.load(file)
    data = dict(data)
    for ticker in data.keys():
        for i in range(0, len(data[ticker])):
            data[ticker][i] = datetime.datetime.strptime(data[ticker][i], "%Y%m%d")
    return data


def write_log(dbname, data, log):
    for ticker in data.keys():
        for i in range(0, len(data[ticker])):
            data[ticker][i] = datetime.datetime.strftime(data[ticker][i], "%Y%m%d")
    with open(dbname + "/" + log, "w") as file:
        json.dump(data, file)
