from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from cboeoptionscraper import elements
import os
import data_logs
import datetime


def download_tickers(tickers, downloads_dir, dbname, wait_time=1):
    driver = Driver()
    data = data_logs.read_log(dbname, data_logs.CBOE_OPTION_LOG)
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
            driver.download_ticker(ticker, downloads_dir, wait_time)
            if ticker not in data.keys():
                data[ticker] = []
            data[ticker].append(datetime.datetime.today())
        except:
            failed.append(ticker)
    data_logs.write_log(dbname, data, data_logs.CBOE_OPTION_LOG)
    return failed


def ticker_format(ticker):
    return ticker.lower().replace("-", ".")


CBOE_FILE_ENDING = "_quotedata.csv"


class Driver:
    def __init__(self):
        self.driver = Chrome()
        self.driver.maximize_window()

    def __del__(self):
        self.driver.quit()

    def get_ticker(self, ticker):
        LINK1 = "https://www.cboe.com/delayed_quotes/"
        LINK2 = "/quote_table"
        url = LINK1 + ticker_format(ticker) + LINK2
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
        path = downloads_dir + ticker_format(ticker) + CBOE_FILE_ENDING
        return os.path.exists(path)

    def download_ticker(self, ticker, downloads_dir, wait_time=1):
        self.get_ticker(ticker)
        self.find_selectors()
        self.set_selectors()
        self.view_chain(wait_time)
        self.download(wait_time)
        if not self.verify_download(ticker, downloads_dir):
            raise Exception()
