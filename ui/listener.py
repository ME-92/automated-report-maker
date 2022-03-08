import time

from text_processing.text_reader import Reader
from text_processing.data_to_json import TweetToJson
from ava_bot import ava_bot
from logger.logger import log
from webcrawler.spider import Spider


def read_tweet(link):
    start = time.perf_counter()
    scraped_data = Spider().scrape_webpages(link)
    if scraped_data:
        log.info("Searching for address and indication patterns in the article..")
        processed_twitter_data = Reader().read_twitter_data(scraped_data)
        log.info("Finalizing report data..")
        report_data = TweetToJson(processed_twitter_data)
        stop = time.perf_counter()
        log.info(f"Report creation took {round(stop - start, 2)} secs.\n")
        return report_data
    else:
        return False


def get_gmaps_data(address, city):
    log.info(f"Looking for location: {address}, {city}")
    new_address, coordinates = Spider().scrape_gmaps_only(address, city)
    if new_address and coordinates:
        new_address = Reader().fix_abbr(new_address)
        address_type, __ = Reader().address_finder(new_address)
        addr_info = [new_address, address_type]
        address_no_number, house_nr, location_accuracy = Reader().finalize_address(addr_info)
        result = address_no_number, house_nr, address_type, location_accuracy, coordinates
        log.info(f"Found address: {house_nr} {address_no_number}, address type: {address_type}")
        return result
    else:
        return ''


def run_bot():
    log.info("Starting AVA bot..")
    ava_bot.AVABot()
    # log.info("Report submitted, closing bot..")


def fix_abbreviations(address):
    return Reader().fix_abbr(address)
