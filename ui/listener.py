
import json
import time

from text_processing.text_reader import Reader
from text_processing.data_to_json import TweetToJson
from ava_bot import ava_bot
from json_data import load_json_files
from logger.logger import log
from webcrawler.spider import Spider


def read_tweet(link):
        start = time.perf_counter()
        scraped_data = Spider().scrape_webpages(link)
        if scraped_data:
            log.info("Searching for address and indication patterns in the article..")
            processed_twitter_data = Reader().read_twitter_data (scraped_data)
            log.info("Finalizing report data..")
            report_data = TweetToJson(processed_twitter_data)
            stop = time.perf_counter()
            log.info(f"Report creation took {round(stop-start,2)} secs.\n")
            return report_data
        else:
            return False

# def read_tweet_text(tweet_text):
#     data = Tweetreader().read_tweet(tweet_text)
#     return data

def load_report_data():
    with open('./json_data/report_data.json', 'r') as file:
        report_data=json.load(file)
        return report_data['reports'][0]

def load_source_files():
    return load_json_files.load_json_files()

def load_settings_files():
    return load_json_files.load_settings()

def to_report_data(data_from_ui):
    with open('./json_data/report_data.json', 'w') as file:
        input_data={"reports":[data_from_ui]}
        json.dump(input_data,file, indent=4)

def load_indications_json():
    with open('./json_data/indications.json', 'r') as indications:
        data=json.load(indications)
        return data

def write_to_json(dictionary,dict_name):
    with open (f'./json_data/{dict_name}.json', 'w') as file:
        input_data = {f"{dict_name}": dictionary}
        json.dump (input_data, file, indent=4)

def edit_setting(name,value):
    load_json_files.edit_setting(name,value)

# def to_json(data_from_ui):
#     with open('json_data/bot_input.json','w') as file:
#         input_data={"reports":[data_from_ui]}
#         json.dump(input_data,file, indent=4)



# def get_address_from_gmaps(address,city):
#     try:
#         address, coordinates = Spider().get_address(address,city)
#         raw_address, address_type = Reader ().address_finder (address)
#         raw_address = Reader().fix_abbr (raw_address)
#         address_type, address_no_number, house_nr, location_accuracy = Reader ().finalize_address (address_type, raw_address)
#         return address_type, address_no_number, house_nr, location_accuracy, coordinates
#     except ValueError:
#         log.error("No coordinates can be found using the address info.")
#         return '',''


def get_gmaps_data(address, city):
    log.info(f"Looking for location: {address}, {city}")
    new_address, coordinates = Spider().scrape_gmaps_only(address, city)
    if new_address and coordinates:
        new_address = Reader().fix_abbr(new_address)
        address_type,__ = Reader().address_finder(new_address)
        addr_info = [new_address, address_type]
        address_no_number, house_nr, location_accuracy= Reader().finalize_address(addr_info)
        result = address_no_number, house_nr, address_type, location_accuracy, coordinates
        log.info(f"Found address: {house_nr} {address_no_number}, address type: {address_type}")
        return result
    else:
        log.error("No address can be found using the address info.")
        return ""


def fix_abbreviations(address):
    return Reader().fix_abbr(address)


def run_bot():
    log.info("Starting AVA bot..")
    ava_bot.AVABot()
    #log.info("Report submitted, closing bot..")
