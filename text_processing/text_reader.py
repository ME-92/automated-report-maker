import re

from json_data.file_manager import load_sources
from logger.logger import log


class Reader():

    def __init__(self):
        self.load_dictionaries()

    def read_twitter_data(self, twitter_data):
        self.link, self.tweet_text, self.city, self.address_type, self.address, self.coordinates, \
        self.tweet_time, self.tweet_date = twitter_data

        self.source, self.relevancy, self.city = self.get_source(self.link), self.get_relevancy(
            self.link), self.get_city(self.link)

        self.address = self.fix_abbr(self.address)

        self.all_indications, self.main_indication, self.facts_injured, self.facts_dead = self.read_tweet(
            self.tweet_text)

        description_data = self.main_indication, self.address_type, self.address, self.facts_injured, self.facts_dead
        self.description = self.finalize_description(description_data)

        processed_twitter_data = self.tweet_text, self.tweet_time, self.tweet_date, self.link, self.city, \
                                 self.description, self.all_indications, self.main_indication, self.facts_injured, \
                                 self.facts_dead, self.address_type, self.address, self.coordinates, self.source, self.relevancy

        return processed_twitter_data

    def order_numbers(self, area_address):
        numeration = {"1": "st", "2": "nd", "3": "rd"}
        x = re.search("\d+\sand\s", area_address)
        if x is not None:
            nr = (re.search("\d+", x.group())).group()
            last_nr = nr[-1]
            for keys, values in numeration.items():
                if last_nr == keys:
                    new_address = re.sub(nr, nr + values, area_address)
                    break
                else:
                    new_address = re.sub(nr, nr + 'th', area_address)
            return new_address
        else:
            return area_address

    def fix_abbr(self, address):
        for keys, values in self.dictionary_abbreviations.items():
            temp = re.search(keys, address)
            if temp is not None:
                address = re.sub(keys, values, address)
        address = self.order_numbers(address)
        return address

    def indication_finder(self, string):
        indications = []
        for keys, values in self.indication_formulas.items():
            read = re.search(keys, string, re.IGNORECASE)
            if read:
                indications.append(values)
        # fixing the 'colliding' indications
        if "Shots fired" in indications and "Sound of gunshots" in indications:
            indications.remove("Shots fired")
        if (("Shot person (injured)" in indications) or (
                "Shot person (dead)" in indications)) and "Shots fired" in indications:
            indications.remove("Shots fired")
        if (("Shot person (injured)" in indications) or (
                "Shot person (dead)" in indications)) and "Sound of gunshots" in indications:
            indications.remove("Sound of gunshots")

        # removes duplicates from the indications list
        indications = list(dict.fromkeys(indications))
        return indications

    def check_facts(self, string, fact):
        try:
            result = re.search(fact, string, re.IGNORECASE)
            facts = result.group().split(" ")[0]
            if result is not None:
                if facts in self.dictionary_numbers.keys():
                    return facts
                else:
                    for keys, values in self.dictionary_numbers.items():
                        if values == facts or values.lower() == facts:
                            facts = keys
                    return facts
        except:
            return '1'

    def additional_facts(self, string, indications):
        injured = self.dictionary_additional_facts['injured']
        dead = self.dictionary_additional_facts['dead']
        both = self.dictionary_additional_facts['both']
        facts_injured = ''
        facts_dead = ''

        for i in indications:
            if 'injured' in i:
                facts_injured = self.check_facts(string, injured)
            if 'dead' in i:
                facts_dead = self.check_facts(string, dead)
        try:
            if re.search(both, string, re.IGNORECASE) is not None:
                facts_injured = str(int(facts_injured) - int(facts_dead))
        except:
            pass
        return facts_injured, facts_dead

    def get_source(self, link):
        twitter_template = "https://twitter.com/"
        if twitter_template in link:
            for keys in self.dictionary_sources.keys():
                if keys in link:
                    return f"Twitter @{keys}"
            else:
                log.info("Twitter account is unknown, please add location and trust score manually.")
                twitter_link = (re.search(r"(?<=om/)(.*?)(?=/stat)", link)).group()
            return f'Twitter @{twitter_link}'
        else:
            log.error("Unknown web address or twitter account, no source was found.")
            return ''

    def get_city(self, link):
        for keys, values in self.dictionary_sources.items():
            if keys in link:
                return values[0]
        log.info("Couldn't find the city in the sources database.")
        return ''

    def get_relevancy(self, link):
        for keys, values in self.dictionary_sources.items():
            if keys in link:
                return values[1]
        log.info("Couldn't find the trust score in the sources database.")
        return 1

    def address_finder(self, string):
        for keys, values in self.address_formulas.items():
            addr = re.search(keys, string)
            if addr is not None:
                address = addr.group()
                address = re.sub('/', ' & ', address)
                address = re.sub('\+', ' & ', address)
                address_type = values
                log.info(f"Found address: '{address}' by using regex formula: '{keys}'.")
                return address_type, address
        return "", ""

    def finalize_description(self, data):
        description = ''
        indication, address_type, address, injured, dead = data
        if ('Shot person' or 'Stabbed person') in indication:
            event = "shot" if 'Shot person' in indication else "stabbed"
            if dead and injured:
                affected = str(int(injured) + int(dead))
                description = f"{self.dictionary_numbers[affected]} persons were {event}," \
                              f" {(self.dictionary_numbers[dead]).lower()} fatally, "
            elif dead or injured == "1":
                for keys, values in self.dictionary_descriptions.items():
                    if keys in indication:
                        description = description.join(values)
            else:
                fatally = 'fatally' if dead else ''
                description = f"{self.dictionary_numbers[(dead if fatally else injured)]} persons were {fatally} {event} "
        else:
            for keys, values in self.dictionary_descriptions.items():
                if keys in indication:
                    description = description.join(values)
        try:
            if address_type == 'address':
                description2 = f"{description}on {address}."
            elif address_type == 'block':
                block_number = re.search('\d+[00]', address).group()
                address = re.sub(block_number, '', address)
                description2 = f"{description}in the {block_number} block of{address}."
            else:
                description2 = f"{description} in the area of {address} ."
            description2 = re.sub("\s\s", " ", description2).replace(' .', '.')
            return description2
        except AttributeError:
            return ''


    def finalize_address(self, addr_info=None):
        if addr_info:
            self.address, self.address_type = addr_info
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
        return self.address_no_number, self.house_nr, self.location_accuracy

    def read_tweet(self, string_data):
        string_data = str(string_data).replace('\n', ' ')
        try:
            all_indications = self.indication_finder(string_data)
            main_indication = all_indications[0]
        except IndexError:
            log.info("No indications were found.")
            main_indication, all_indications = "", ""
        facts_injured, facts_dead = self.additional_facts(string_data, all_indications)
        return all_indications, main_indication, facts_injured, facts_dead

    def load_dictionaries(self):
        self.dictionary_abbreviations, self.indication_formulas, self.address_formulas, \
        self.dictionary_descriptions, self.dictionary_sources, self.dictionary_additional_facts \
            = load_sources()
        self.dictionary_numbers = {"1": "One", "2": "Two", "3": "Three", "4": "Four", "5": "Five", "6": "Six",
                                   "7": "Seven", "8": "Eight", "9": "Nine", "10": "Ten"}

# Instance1=Reader()
