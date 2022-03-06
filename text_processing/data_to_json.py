import re
import json

from datetime import datetime

from logger.logger import log


class TweetToJson():

    def __init__(self, data):
        self.data = {"reports": []}
        self.tweet_text, self.tweet_time, self.tweet_date, self.link, self.city, self.description, \
            self.all_indications, self.main_indication, self.facts_injured, \
            self.facts_dead, self.address_type, self.address, self.coordinates, self.source, self.relevancy = data
        self.data_to_dict()
        self.dict_to_json()
        self.return_data()

    def data_to_dict(self):
        self._finalize_address()
        self._finalize_time_and_date()
        self._finalize_link()
        self._fill_in_dict()

    def _finalize_address(self):
        self.location_accuracy = ''
        if self.address_type != 'lat/long':
            try:
                self.house_nr = re.search('\d+', self.address).group()
                self.address_no_number = re.sub(self.house_nr, '', self.address).lstrip()
            except:
                log.info("House number was not found in the address.")
                self.house_nr = ""
                self.address_no_number = ""
        elif self.address_type == 'lat/long':
            self.address_no_number = self.address.split(' and ')[0]
            self.house_nr = ''
            self.location_accuracy = '300'
        else:
            self.address_type = ''
            self.house_nr = ''

    def _finalize_time_and_date(self):
        try:
            self.tweet_time = self.tweet_time.rstrip()
            self.starting_time = datetime.strptime(self.tweet_time, "%I:%M %p")
            self.starting_time_hour, self.starting_time_minute = datetime.strftime(self.starting_time,"%H"), datetime.strftime(self.starting_time, "%M")
        except:
            log.error("Tweet time was not found.")
            self.starting_time_hour, self.starting_time_minute = "", ""
        try:
            self.tweet_date = self.date_fixer(self.tweet_date)
        except:
            log.info("Date was not found.")
            self.tweet_date = ''

    def _finalize_link(self):
        pass
        # use webpage link to create a source text like ("news.com")

    def _fill_in_dict(self):
        self.dict_to_JSON = {
            'coordinates': self.coordinates,
            'all_indications': self.all_indications,
            'starting_time': [self.starting_time_hour, self.starting_time_minute],
            'date': self.tweet_date,
            'injured': self.facts_injured,
            'dead': self.facts_dead,
            'source': self.source,
            'link': self.link,
            'address_type': self.address_type,
            'address': self.address_no_number,
            'house_nr': self.house_nr,
            'location_accuracy': self.location_accuracy,
            'tweet_text': self.tweet_text,
            'city_state': self.city,
            'description': self.description,
            'source_type': "",
            'relevancy': self.relevancy,
            'duration': "",
            'time_accuracy': ""}
        self.data['reports'].append(self.dict_to_JSON)

    def date_fixer(self, date_raw: str):
        date = datetime.strptime(date_raw, r' %d %b %Y')
        return date.strftime(f'%e %B %Y').lstrip()

    def dict_to_json(self):
        with open('arm/json_data/report_data.json', "w") as outfile:
            json.dump(self.data, outfile, indent=4)

    def return_data(self):
        return self.data
