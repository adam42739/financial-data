from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from cboe import elements
import os
import data_logs
import datetime
import pandas

DB_DIR = "cboe_options"

CBOE_FILE_ENDING = "_quotedata.csv"

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


def get_options(ticker, date, db_name):
    ticker = ticker_format(ticker)
    date_str = str(date.year) + str(date.month).zfill(2) + str(date.day).zfill(2)
    path = db_name + "/" + DB_DIR + "/" + ticker + date_str + ".csv"
    if os.path.isfile(path):
        df = pandas.read_csv(path)
        df["Expiration"] = CBOE_START_DATE + pandas.to_timedelta(
            df["Expiration"], unit="d"
        )
        return df
    else:
        return DEFAULT_DF


def download_tickers_to_db(tickers, db_name, downloads_dir, wait_time=1):
    driver = Driver()
    return driver.download_tickers_to_db(tickers, db_name, downloads_dir, wait_time)


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


def update_db_from_downloads(ticker, downloads_dir, db_name, date):
    downloads_path = downloads_dir + ticker + CBOE_FILE_ENDING
    df = pandas.read_csv(downloads_path, header=2)
    df = parse_df(df)
    date_str = str(date.year) + str(date.month).zfill(2) + str(date.day).zfill(2)
    db_path = db_name + "/" + DB_DIR + "/" + ticker + date_str + ".csv"
    df.to_csv(db_path, index=False)
    os.remove(downloads_path)


class Driver:
    def __init__(self):
        self.driver = Chrome()
        self.driver.maximize_window()

    def __del__(self):
        self.driver.quit()

    def get_ticker(self, ticker):
        LINK1 = "https://www.cboe.com/delayed_quotes/"
        LINK2 = "/quote_table"
        url = LINK1 + ticker + LINK2
        self.driver.get(url)

    def find_selectors(self):
        self.selectors = self.driver.find_elements(
            By.CLASS_NAME, elements.SELECTOR_CLASS
        )

    def scroll_element_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        self.driver.execute_script("window.scrollBy(0,-100)")

    def set_selectors(self):
        for selector in self.selectors:
            input = selector.find_element(By.CLASS_NAME, elements.INPUT_CONTAINER)
            self.scroll_element_into_view(input)
            input.send_keys("All")
            input.send_keys(Keys.ENTER)

    def view_chain(self, wait_time=1):
        button = self.driver.find_element(By.CLASS_NAME, elements.VIEW_CHAIN_BUTTON)
        self.scroll_element_into_view(button)
        button.click()
        time.sleep(wait_time)

    def download(self, wait_time=1):
        link = self.driver.find_element(By.CLASS_NAME, elements.DOWNLOAD_LINK)
        self.scroll_element_into_view(link)
        link.click()
        time.sleep(wait_time)

    def verify_download(sefl, ticker, downloads_dir):
        path = downloads_dir + ticker + CBOE_FILE_ENDING
        return os.path.exists(path)

    def download_ticker(self, ticker, downloads_dir, wait_time=1):
        self.get_ticker(ticker)
        self.find_selectors()
        self.set_selectors()
        self.view_chain(wait_time)
        self.download(wait_time)
        if not self.verify_download(ticker, downloads_dir):
            raise Exception()

    def download_tickers_to_db(self, tickers, db_name, downloads_dir, wait_time=1):
        failed = []
        data = data_logs.read_log(db_name, data_logs.CBOE_OPTION_LOG)
        today = datetime.datetime.strftime(datetime.datetime.today(), "%Y%m%d")
        for ticker in tickers:
            ticker = ticker_format(ticker)
            if ticker in data:
                if today in data[ticker]:
                    continue
            try:
                self.download_ticker(ticker, downloads_dir, wait_time)
                update_db_from_downloads(
                    ticker, downloads_dir, db_name, datetime.datetime.today()
                )
                if ticker not in data.keys():
                    data[ticker] = []
                data[ticker].append(today)
            except:
                failed.append(ticker)
        data_logs.write_log(db_name, data, data_logs.CBOE_OPTION_LOG)
        return failed
