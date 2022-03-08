import os
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, InvalidSessionIdException, \
    SessionNotCreatedException, InvalidArgumentException

from json_data import load_json_files
from text_processing.text_reader import Reader
from logger.logger import log
 
import time


class Spider():

    def __init__(self) -> None:
        self.chrome_profile_dir, self.run_headless, self.load_images, self.time_zone, __ = load_json_files.load_settings()

    def scrape_webpages(self, link):
        self.link = link
        self._setup_driver()
        with webdriver.Chrome(executable_path=self.chrome_path, options=self.options) as self.driver:
            # Get data from Twitter
            log.info(f"Reading tweet: {link}")
            try:
                self.tweet_text, self.time_date = self._scrape_tweet_body(self.link)
                self.tweet_time, self.tweet_date = self._extract_twitter_datetime(self.time_date)
            except (InvalidArgumentException, TypeError):
                log.error("Invalid Twitter link provided. Returning the previous report..")
                return False
            # Get data from Gmaps
            self.find_loc_data(self.link, self.tweet_text)
            self.address, self.coordinates = self.get_address(self.address, self.city)
        # return data
        return self.link, self.tweet_text, self.city, self.address_type, self.address, self.coordinates, \
               self.tweet_time, self.tweet_date

    def find_loc_data(self, link: str, text: str):
        self.city = Reader().get_city(link)
        self.address_type, self.address = Reader().address_finder(text)
        return self.city, self.address, self.address_type

    def _scrape_tweet_body(self, link: str):
        self.driver.get(self.link)
        ARTICLE_CSS = 'article[data-testid="tweet"]'
        datetime_link = re.sub("https://twitter.com", "", link)
        self.waiting_function('css selector', ARTICLE_CSS)
        tweet_articles = self.driver.find_elements('css selector', ARTICLE_CSS)
        for article in tweet_articles:
            try:
                time_date = article.find_element('css selector', f"a[href='{datetime_link}']").text
                tweet_text = article.find_element('css selector', "div[lang='en']").text
                log.info(f"Article content collected.")
                return tweet_text, time_date
            except:
                continue

    def _extract_twitter_datetime(self, time_date: str):
        tweet_time, tweet_date = time_date.split('·')[0], time_date.split('·')[1]
        return tweet_time, tweet_date

    def get_address(self, address, city):
        if address and city:
            log.info(f"Searching GMaps for: {address}, {city}")
            try:
                new_address, coordinates = self.scrape_gmaps_for_address(address, city)
                return new_address, coordinates
            except (TypeError, ValueError):
                log.info(f"Location was not found. Please enter the coordinates manually.")
        else:
            log.info(f"Missing location data, please enter the city and address and run Gmaps manually.")
        # returns the old address without coordinates
        new_address, coordinates = address, ""
        return new_address, coordinates

    def scrape_gmaps_for_address(self, address, city):
        self.driver.get("https://www.google.com/maps/")
        self.waiting_function('css selector', 'input[id="searchboxinput"]')
        enter_address = self.driver.find_element_by_css_selector('input[id="searchboxinput"]')
        enter_address.send_keys(f"{address}, {city}")
        self.driver.find_element('css selector', 'button[id="searchbox-searchbutton"]').click()
        try:
            WebDriverWait(self.driver, 8).until(EC.url_contains("maps/place/"))
        except TimeoutException:
            log.error("No valid address could be found on GMaps.")
            return ''
        gmaps_url = self.driver.current_url
        coordinates = self._extract_coord_from_gmaps_link(gmaps_url)
        address = self._extract_address_from_gmaps_link(gmaps_url)
        return address, coordinates

    def scrape_gmaps_only(self, address, city):
        self._setup_driver()
        with webdriver.Chrome(executable_path=self.chrome_path, options=self.options) as self.driver:
            try:
                new_address, coordinates = self.scrape_gmaps_for_address(address, city)
                return new_address, coordinates
            except:
                return "",""

    def _extract_address_from_gmaps_link(self, gmaps_url):
        address = re.search('(?<=place\/)(.*?)(?=,)', gmaps_url).group()
        address = address.replace('+%26+', ' & ')
        address = address.replace('+', ' ')
        return address

    def _extract_coord_from_gmaps_link(self, gmaps_url):
        coord = re.search('!3d[\d.\-\+]+!4d[\d.\-\+]+', gmaps_url)
        coord = coord.group()
        coord = re.sub('!3d', '', coord)
        coord = re.sub('!4d', ',', coord)
        return coord

    def _scrape_tweet_time_and_date(self):
        self.waiting_function('css selector', 'a[role="link"].innerText()')
        date_time = self.driver.find_element('css selector', "a[role='link']").innerText
        print(date_time)
        tweet_time, tweet_date = date_time.split('·')[0], date_time.split('·')[1]
        return tweet_time, tweet_date

    def _setup_driver(self):
        self.options = webdriver.ChromeOptions()
        if self.load_images:
            prefs = {"profile.managed_default_content_settings.images": 0}
        else:
            prefs = {"profile.managed_default_content_settings.images": 2}
        if self.run_headless:
            self.options.add_argument('headless')
        self.options.add_argument("--lang=en-EN")
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.options.add_experimental_option("prefs", prefs)
        self.chrome_path = os.path.abspath('./webcrawler/chromedriver.exe')

    def waiting_function(self, by_variable, attribute):
        try:
            WebDriverWait(self.driver, 10).until(lambda x: x.find_element(by=by_variable, value=attribute))
        except (NoSuchElementException, TimeoutException):
            log.error('{} {} not found'.format(by_variable, attribute))
            exit()

# Instance1=Spider()
