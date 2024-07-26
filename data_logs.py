import json
import datetime

CBOE_OPTION_LOG = "cboe_options_log.json"
YAHOO_PRICE_LOG = "yahoo_prices_log.json"


def clear_log(db_name, log):
    with open(db_name + "/" + log, "w") as file:
        file.write("{}")


def read_log(db_name, log):
    data = None
    with open(db_name + "/" + log, "r") as file:
        data = json.load(file)
    data = dict(data)
    return data


def write_log(db_name, data, log):
    with open(db_name + "/" + log, "w") as file:
        json.dump(data, file)
