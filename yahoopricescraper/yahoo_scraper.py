from selenium import webdriver
from selenium.webdriver import Chrome
import datetime
import time
import os
import data_logs


def download_tickers(tickers, dbname, start_date, end_date, downloads_dir, wait_time=1):
    driver = Driver()
    data = data_logs.read_log(dbname, data_logs.YAHOO_PRICE_LOG)
    failed = []
    for ticker in tickers:
        ticker = ticker_format(ticker)
        if ticker in data.keys():
            found = False
            for date in data[ticker]:
                if datetime.datetime.today().date() == date.date():
                    found = True
                    break
            if found:
                continue
        try:
            driver.download_ticker(
                ticker, start_date, end_date, downloads_dir, wait_time
            )
            if ticker not in data.keys():
                data[ticker] = []
            data[ticker].append(datetime.datetime.today())
        except:
            failed.append(ticker)
    data_logs.write_log(dbname, data, data_logs.YAHOO_PRICE_LOG)
    return failed


def ticker_format(ticker):
    return ticker.upper().replace(".", "-")


YAHOO_START_DATE = datetime.datetime(1970, 1, 1)
YAHOO_DATE_ITER = 86400


class Driver:
    LINK1 = "https://query1.finance.yahoo.com/v7/finance/download/"
    LINK2 = "?period1="
    LINK3 = "&period2="
    LINK4 = "&interval=1d&events=history&includeAdjustedClose=true"

    def __init__(self):
        self.driver = Chrome()
        self.driver.maximize_window()

    def __del__(self):
        self.driver.quit()

    def verify_download(self, ticker, downloads_dir):
        path = downloads_dir + ticker_format(ticker) + ".csv"
        return os.path.exists(path)

    def download_ticker(self, ticker, start_date, end_date, downloads_dir, wait_time=1):
        number1 = str((start_date - YAHOO_START_DATE).days * YAHOO_DATE_ITER)
        number2 = str((end_date - YAHOO_START_DATE).days * YAHOO_DATE_ITER)
        url = (
            Driver.LINK1
            + ticker_format(ticker)
            + Driver.LINK2
            + number1
            + Driver.LINK3
            + number2
            + Driver.LINK4
        )
        self.driver.get(url)
        time.sleep(wait_time)
        if not self.verify_download(ticker, downloads_dir):
            raise Exception()
