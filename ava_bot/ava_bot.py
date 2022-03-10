import time
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException, \
    WebDriverException

from json_data.file_manager import load_settings, load_report_data
from logger.logger import log


class AVABot:

    def __init__(self):
        self.chrome_profile_dir, __, __, self.time_zone, self.ava_username = load_settings()
        self.ava_link = "https://ava.center/login"
        self.data = load_report_data()
        self.run_ava_bot()

    def run_ava_bot(self):
        self._setup_driver()
        with webdriver.Chrome(executable_path=self.chrome_path, options=self.options) as self.driver:
            self.driver.maximize_window()
            self.driver.get(self.ava_link)
            try:
                self.log_into_ava()
                self.close_active_widgets()
                self.go_to_coordinates()
                self.fill_in_indications()
                self.set_time_accuracy()
                self.set_duration()
                self.set_date()
                self.set_time()
                self.set_description_and_facts()
                self.set_channel_and_ref()
                self.set_geo_data()
                self.wait_for_submit()
            except WebDriverException:
                log.info("Chrome Webdriver window manually closed.")
                return

    def _setup_driver(self):
        prefs = {"profile.managed_default_content_settings.images": 1}
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--lang=en-EN")
        self.options.add_argument(f"user-data-dir={self.chrome_profile_dir}")
        self.options.add_experimental_option("detach", True)
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.options.add_experimental_option("prefs", prefs)
        self.chrome_path = os.path.abspath('./webcrawler/chromedriver.exe')

    def waiting_function(self, by_variable, attribute):
        try:
            WebDriverWait(self.driver, 5).until(lambda x: x.find_element(by=by_variable, value=attribute))
        except (NoSuchElementException, TimeoutException):
            print('{} {} not found'.format(by_variable, attribute))
            exit()

    def _middle_screen_click(self):
        map_canvas = self.driver.find_element('canvas[aria-label="Map"]')
        webdriver.ActionChains(self.driver).click(map_canvas).perform()

    def log_into_ava(self):
        self.waiting_function('css selector', 'input[formcontrolname="username"]')
        username = self.driver.find_element('css selector', 'input[formcontrolname="username"]')
        username.send_keys(self.ava_username, Keys.ENTER)
        self.waiting_function('css selector', 'button[class="btn btn-round primary primary-large"]')
        self.driver.find_element('css selector', 'button[class="btn btn-round primary primary-large"]').send_keys(
            Keys.ENTER)
        # click on a logged in email
        self.waiting_function('css selector', 'li[class="JDAKTe ibdqA W7Aapd zpCp3 SmR8"]')
        self.driver.find_element('css selector', 'li[class="JDAKTe ibdqA W7Aapd zpCp3 SmR8"]').click()

    def fill_in_indications(self):
        for indication in self.data['all_indications']:
            self.driver.find_element('css selector', 'input[placeholder="Select indications"]').click()
            self.driver.find_element('css selector', 'input[placeholder="Select indications"]').send_keys(indication)
            self.waiting_function('xpath', f"//*[contains(text(), '{indication}')]")
            self.driver.find_element('xpath', f"//*[contains(text(), '{indication}')]").click()
        # wait and click the next button
        self.waiting_function('css selector', 'button[class="btn btn-round primary"]')
        self.driver.find_element('css selector', 'button[class="btn btn-round primary"]').click()

    def close_active_widgets(self):
        self.waiting_function('xpath', "//button[contains(text(), ' Location briefing ')]")
        location_briefing_button = self.driver.find_element('xpath',
                                                            "//button[contains(text(), ' Location briefing ')]")
        interest_sets_button = self.driver.find_element('xpath', "//button[contains(text(), 'Interest sets')]")
        recent_button = self.driver.find_element('xpath', "//button[contains(text(), ' Recent ')]")
        time.sleep(1)
        if 'active' in location_briefing_button.get_attribute('class').split():
            print('Location briefing button is active, deactivating..')
            location_briefing_button.click()
        if 'active' in interest_sets_button.get_attribute('class').split():
            print('Interest sets button is active, deactivating..')
            interest_sets_button.click()
        if 'active' in recent_button.get_attribute('class').split():
            print('Recent button active, deactivating..')
            recent_button.click()

    def go_to_coordinates(self):
        # press search button
        self.driver.find_element('css selector', "button[class='btn-search']").click()
        # paste coordinate
        self.driver.find_element('css selector', 'input[placeholder="Search for location"]').send_keys(
            self.data['coordinates'])
        time.sleep(1)
        # Go to a coordinate:
        self.waiting_function('css selector', 'input[placeholder="Search for location"]')
        self.driver.find_element('css selector', 'input[placeholder="Search for location"]').send_keys(Keys.ENTER)
        time.sleep(2)
        # select the tool
        self.driver.find_element('css selector', 'button[class="mapbox-gl-draw_circle"]').click()
        # wait until user sets the location
        WebDriverWait(self.driver, 180).until(
            lambda x: x.find_element('css selector', 'input[placeholder="Select indications"]'))

    def set_time_accuracy(self):
        if self.data['time_accuracy'].isnumeric():
            accuracy_line = self.driver.find_elements('css selector', "div[class='label-info-row']")[1]
            accuracy_line.find_element('css selector', "input[type='number']").send_keys(self.data['time_accuracy'])
            if int(self.data['time_accuracy']) > 60:
                level_of_precision = self.driver.find_elements('css selector', "div[class='label-info-row']")[0]
                level_of_precision.find_element('css selector', "input[placeholder='Minute']").send_keys('Hour')
                level_of_precision.find_elements('css selector', "li[class='dropdown-item']")[0].click()

    def set_duration(self):
        if self.data['duration'].isnumeric():
            duration_line = self.driver.find_element('css selector', 'input[id="duration"]')
            duration_line.clear()
            duration_line.send_keys(Keys.BACK_SPACE)
            duration_line.send_keys(self.data['duration'])
        # wait and click on date
        self.waiting_function('css selector', 'input[placeholder="Add a starting date"]')
        self.driver.find_element('css selector', 'input[placeholder="Add a starting date"]').click()

    def set_time(self):
        clock = self.driver.find_elements('css selector', 'input[class="owl-dt-timer-input"]')
        clock[0].clear()
        clock[0].send_keys(self.data['starting_time'][0])
        clock[1].clear()
        clock[1].send_keys(self.data['starting_time'][1])
        time.sleep(0.5)
        self.driver.find_element('xpath', "//button[2]/span[contains(text(),' Set ')]").click()

    def set_date(self):
        try:
            calendar_table = self.driver.find_element('css selector', 'tbody[class="owl-dt-calendar-body"]')
            calendar_table.find_element('css selector', f"td[aria-label='{self.data['date']}']").click()
        except NoSuchElementException:
            self.driver.find_element('css selector', 'button[aria-label="Previous month"]').click()
            self.set_date()

    def set_description_and_facts(self):
        # description
        self.driver.find_element('css selector', 'button[class="btn btn-round primary"]').click()
        self.driver.find_element('css selector', 'textarea[placeholder="Enter description of the incident"]').send_keys(
            self.data['description'])
        # additional facts
        self.counter = 0
        if self.data['injured'] != "":
            self.input_additional_info('Injured', self.data['injured'])
        if self.data['dead'] != "":
            self.input_additional_info('Dead', self.data['dead'])

    def input_additional_info(self, fact, number):
        self.driver.find_element('css selector', 'input[placeholder="Add new fact"]').click()
        self.driver.find_element('css selector', 'input[placeholder="Add new fact"]').send_keys(
            Keys.PAGE_DOWN, f'{fact}')
        self.driver.find_element('css selector', 'li[class="dropdown-item ng-star-inserted"]').click()
        if self.counter == 1:
            fact_box = self.driver.find_elements('xpath', f"//div[contains(@class,'add-fact-box')]")[1]
        else:
            fact_box = self.driver.find_elements('xpath', f"//div[contains(@class,'add-fact-box')]")[0]
        fact_info = fact_box.find_element('xpath', f".//input[@placeholder='Enter fact information']")
        fact_info.click()
        fact_info.send_keys(f'{number}', Keys.PAGE_DOWN)
        add_button = fact_box.find_element('xpath', ".//div[contains(text(),'Add')]")
        add_button.click()
        self.counter = 1

    def set_channel_and_ref(self):
        # channel and reference
        self.driver.find_element('css selector', 'button[class="btn btn-round primary"]').click()
        self.waiting_function('css selector', 'input[placeholder="Select channel"]')
        self.driver.find_element('css selector', 'input[placeholder="Select channel"]').send_keys(
            self.data['source_type'])
        self.driver.find_element('xpath',f"//dropdown-search/div/ul/li[contains(text(), "
                                         f"' {self.data['source_type']} ')]").click()
        self.driver.find_element('css selector', 'input[placeholder="Enter source name"]').send_keys(
            self.data['source'])
        # relevancy
        if self.data['relevancy'] == 2:
            self.driver.find_elements('css selector', 'i[class="icon icon-star"]')[1].click()
        elif self.data['relevancy'] == 3:
            self.driver.find_elements('css selector', 'i[class="icon icon-star"]')[2].click()
        else:
            self.driver.find_elements('css selector', 'i[class="icon icon-star"]')[0].click()
        self.driver.find_element('css selector', 'textarea[placeholder="Enter reference information'
                                                 ' (e.g. url of the source)"]').send_keys(self.data['link'])
        self.driver.find_element('css selector', 'button[class="btn btn-round primary"]').click()
        self.driver.find_element('css selector', 'button[class="btn btn-round primary"]').click()

    def set_geo_data(self):
        # address
        self.driver.find_elements('css selector', 'div[class="list-item"]')[2].click()
        if self.data['address_type'] != 'address':
            self.driver.find_element('css selector', 'input[placeholder="Address"]').click()
            self.driver.find_element('css selector', 'input[placeholder="Address"]').send_keys(
                self.data['address_type'])
            self.driver.find_element('xpath', '//dropdown-search/div/ul/li').click()
        # accuracy
        if self.data['address_type'] == 'lat/long' or self.data['location_accuracy'] is not True:
            self.driver.find_element('xpath', '/html/body/app/div/ng-component/map-component/'
                 'create-report-widget/div/div/div[2]/div/div[11]/div/div[3]/div[4]/div/input').send_keys(
                        self.data['location_accuracy'])
        # street name and house number
        self.driver.find_elements('css selector', "input[type='search']")[8].clear()
        self.driver.find_elements('css selector', "input[type='search']")[8].send_keys(self.data['address'])
        self.driver.find_elements('css selector', "input[type='search']")[9].clear()
        self.driver.find_elements('css selector', "input[type='search']")[9].send_keys(self.data['house_nr'])
        # return to overview
        self.driver.find_element('xpath', "/html/body/app/div/ng-component/map-component/create-"
            "report-widget/div/div/div[2]/div/div[11]/div/div[3]/div[1]/span[contains(text(), 'Address')]").click()

    def wait_for_submit(self):
        try:
            while self.driver.find_element('tag name', 'create-report-widget'):
                time.sleep(1)
        except(NoSuchWindowException, WebDriverException):
            return

# Instance=AVABot()
