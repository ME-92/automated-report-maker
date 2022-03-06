
import time
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QModelIndex, QItemSelectionModel, pyqtSignal, QThread, QRunnable, \
    QThreadPool, QObject
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTableWidgetItem, QInputDialog, QMessageBox, QFileDialog, QDialog, QDialogButtonBox, \
    QLineEdit, QFormLayout, QHeaderView

from ui import ARM_resource_rc, listener
from ui.tree_proxy_model import LeafFilterProxyModel
from json_data import load_json_files
from logger.logger import UiHandler,log


class ARM_Main(QtWidgets.QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self._init_UI()
        self._finalize_UI()
        self._set_tooltips()
        self._set_text()
        self._set_placeholders()
        self._set_curr_time_date()
        self._set_logging()

    def _finalize_UI(self):
        self._get_settings()
        self._get_css()
        self._get_dictionaries()
        self._build_indication_tree()
        self._set_indication_buttons()
        self._fill_source_tables()
        self._set_reports_tab()
        self._set_sources_tab()
        self._set_settings_tab()


    def read_tweet_thread(self):
        worker1 = Worker(self.read_tweet_from_link)
        prog_bar = ProgBar()
        self.threadpool = QThreadPool()
        self.threadpool.start(worker1)
        self.threadpool.start(prog_bar)
        prog_bar.signals.start_sig.connect(self.start_prog_bar)
        prog_bar.signals.change_value.connect(self.change_prog_value)
        worker1.signals.result.connect(self.load_data_from_dict)
        worker1.signals.result.connect(self.end_prog_bar)

    def run_bot_thread(self):
        bot_worker = Worker(listener.run_bot)
        self.threadpool = QThreadPool()
        self.threadpool.start(bot_worker)

    def get_address_thread(self):
        get_loc_data = Worker(self.get_address)
        self.threadpool.start(get_loc_data)
        get_loc_data.signals.result.connect(self.fill_address_form)

    def _set_tooltips(self):
        dictionary_tooltips = {self.clear_indications:"Clears selected indications",self.sound_of_gunshots:"Sound of gunshots",self.police_ats:"Police at the scene",self.dead:"Insert the number of dead persons here",self.firefighters_ats:"Firefighters at the scene",self.shots_fired:"Shots fired",self.stabbing:"Stabbed person",self.police_investigation:"Police investigation", self.ambulance_ats:"Ambulance at the scene",self.injured:"Insert the number of injured persons here",self.shooting:"Shot person",self.indications_list:"List of report indications",self.add_indication:"Add an indication",self.emergency_services:"Emergency responders at the scene",self.run_bot:"Runs the Bot and takes you to AVA Center, if all needed information is present",self.console:"",self.account:"Twitter account taken from the link",self.time:"Event time",self.gmaps_button:"Searches for coordinates on Google Maps",self.source:"Source of information",self.time_accuracy:"Accuracy of the time of the incident in minutes",self.house_number:"House number",self.date:"Event date",self.address_type:"Type of address recognized by the reader",self.coordinates:"Geographical coordinates obtained from Google Maps",self.city_state:"City/State",self.location_accuracy:"Location accuracy in meters",self.trust_score:"",self.address:"Street name",self.duration:"Duration of the incident, remains on AVA\'s default duration if left empty",self.enter_tweet_link:"Run webcrawler for the current tweet link",self.tweet_text:"Original tweet text",self.tweet_link_clear:"Reset all of the text fields",self.tweet_link:"Tweet link",self.description:"Generated report description",self.indication_selection:"Search for indications in the tree",self.add_twitter_accounts:"Add a source to the table",self.remove_twitter_accounts:"Removes the selected source from the table",self.add_template:"Add a custom text template to the table",self.remove_template:"Removes the selected template from the table"}
        for keys, values in dictionary_tooltips.items():
            keys.setToolTip(values)

    def _set_text(self):
        dictionary_set_text = {self.clear_indications:"Clear", self.dead_label:"Dead", self.injured_label:"Injured", self.add_indication:"Add", self.run_bot:"Run Bot", self.label_trust_score:"Trust score:", self.label_location_accuracy:"Accuracy:", self.label_address:"Address:", self.label_time_accuracy:"Accuracy (+/-)", self.label_time_duration:"Duration (min):", self.label_address_type:"Address type:", self.label_account:"Account info:", self.label_time_and_date:"Time and date:", self.label_tweet_link:"Source link:", self.enter_tweet_link:"[Enter]", self.paste_link:"Paste", self.tweet_link_clear:"Reset", self.label_datum:"Indications:", self.remove_regex_indication_formula:"-", self.add_regex_indication_formula:"+", self.edit_regex_indication_formula:"Edit", self.regex_formulas_label:"Regex formulas:", self.twitter_accounts_label:"Twitter Accounts:", self.templates_label:"Templates:", self.remove_regex_address_formula:"-", self.add_regex_address_formula:"+", self.edit_regex_address_formula:"Edit", self.chrome_headless: "Run Chrome in headless mode", self.load_images: "Load images in pages", self.chrome_user_profile_label: "Chrome User Profile:", self.default_time_zone_label: "Default time zone (GMT):", self.ava_username_label: "AVA Username:", self.ava_username_button: "...", self.chrome_user_profile_button: "...", self.add_twitter_accounts: "+", self.add_template: "+", self.remove_twitter_accounts: "-", self.remove_template: "-", self.edit_template: "Edit"}
        for keys, values in dictionary_set_text.items():
            keys.setText(values)

    def _set_placeholders(self):
        dictionary_set_placeholder = {self.tweet_link: "Tweet link", self.tweet_text: "Tweet text", self.description: "Report description",self.account: "Twitter acount name", self.coordinates: "Coordinates",self.house_number: "House nr.", self.address: "Street name", self.city_state: "City/State", self.console: "Console window"}

        for keys, values in dictionary_set_placeholder.items():
            keys.setPlaceholderText(values)

    def _set_reports_tab(self):
        self.enter_tweet_link.clicked.connect(self.read_tweet_thread)
        self.gmaps_button.clicked.connect (self.get_address_thread)
        self.tweet_link_clear.clicked.connect (self.clear_fields)
        self.indication_selection.textChanged.connect (self.filter_proxy_model.setFilterRegExp)
        self.indication_selection.textChanged.connect (self.indication_tree.expandAll)
        self.indication_tree.doubleClicked.connect (self.add_indication_to_list)
        self.indication_tree.doubleClicked.connect (self.indication_selection.clear)
        self.add_indication.clicked.connect (
            lambda: self.add_indication_to_list (self.indication_tree.selectedIndexes ()[0]))
        self.add_indication.clicked.connect (self.indication_selection.clear)
        self.clear_indications.clicked.connect (self.clear_indications_list)
        self.paste_link.clicked.connect (lambda: self.tweet_link.paste ())
        #self.paste_tweet_text.clicked.connect (lambda: self.tweet_text.paste ())
        #self.paste_description.clicked.connect (lambda: self.description.paste ())
        self.run_bot.clicked.connect (self.get_data)
        self.run_bot.clicked.connect(self.run_bot_thread)

    def _set_sources_tab(self):
        self.remove_regex_indication_formula.clicked.connect(lambda:self._remove_table_item_dialog(self.regex_indication_formulas_table))
        self.remove_regex_address_formula.clicked.connect(lambda:self._remove_table_item_dialog(self.regex_address_formulas_table))
        self.remove_twitter_accounts.clicked.connect(lambda:self._remove_table_item_dialog(self.twitter_accounts_table))
        self.remove_template.clicked.connect(lambda:self._remove_table_item_dialog(self.templates_table))
        self.add_regex_indication_formula.clicked.connect(lambda:self._add_table_item_dialog('indication_formulas'))
        self.add_regex_address_formula.clicked.connect(lambda:self._add_table_item_dialog('address_formulas'))
        self.add_twitter_accounts.clicked.connect(lambda:self._add_table_item_dialog('sources'))
        self.add_template.clicked.connect(lambda:self._add_table_item_dialog('descriptions'))
        self.edit_regex_indication_formula.clicked.connect(
            lambda: self._edit_table_item(self.regex_indication_formulas_table))
        self.edit_regex_address_formula.clicked.connect(
            lambda:self._edit_table_item (self.regex_address_formulas_table))

    def _set_settings_tab(self):
        self.ava_username.setPlainText(self.ava_username_value)
        self.ava_username.setReadOnly(True)
        self.ava_username_button.clicked.connect(self._set_ava_profile)
        self.chrome_user_profile.setPlainText(self.chrome_profile_dir_setting)
        self.chrome_user_profile.setReadOnly (True)
        self.chrome_user_profile_button.clicked.connect(self._set_directory)
        if self.load_images_setting:
            self.load_images.setChecked(True)
        self.load_images.toggled.connect(lambda:self._set_checkbox(self.load_images,'load_images'))
        if self.run_minimized_setting:
            self.chrome_headless.setChecked(True)
        self.chrome_headless.toggled.connect(lambda: self._set_checkbox (self.chrome_headless, 'run_headless'))
        self.default_time_zone.setValue(self.time_zone_setting)

    def _set_ava_profile(self):
        response, ok = QInputDialog.getText(self, 'Edit Username', 'Enter your AVA email address:')
        if ok:
            listener.edit_setting('ava_username', response)
        self._get_settings()
        self.ava_username.setPlainText(self.ava_username_value)

    def _set_directory(self):
        response = QFileDialog.getExistingDirectory(self,caption="Choose the Google Chrome profile folder: ")
        if response:
            listener.edit_setting('user_profile_path', response)
        self._get_settings()
        self.chrome_user_profile.setPlainText (self.chrome_profile_dir_setting)

    def _set_checkbox(self,checkbox, setting):
        if checkbox.checkState () == 2:
            listener.edit_setting (setting, True)
        else:
            listener.edit_setting(setting, False)

    def _set_indication_buttons(self):
        self.shots_fired.clicked.connect(lambda:self.toggle_buttons("Shots fired"))
        self.sound_of_gunshots.clicked.connect(lambda:self.toggle_buttons("Sound of gunshots"))
        self.police_investigation.clicked.connect(lambda:self.toggle_buttons("Police investigation"))
        self.shooting.clicked.connect(lambda:self.toggle_buttons("Shot person (injured)"))
        self.shooting.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.shooting.customContextMenuRequested.connect(lambda:self.toggle_buttons("Shot person (dead)"))
        self.stabbing.clicked.connect(lambda:self.toggle_buttons("Stabbed person (injured)"))
        self.stabbing.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.stabbing.customContextMenuRequested.connect(lambda:self.toggle_buttons("Stabbed person (dead)"))
        self.police_ats.clicked.connect(lambda:self.toggle_buttons("Police at the scene"))
        self.ambulance_ats.clicked.connect(lambda:self.toggle_buttons("Ambulance at the scene"))
        self.firefighters_ats.clicked.connect(lambda:self.toggle_buttons("Firefighters at the scene"))
        self.emergency_services.clicked.connect(lambda:self.toggle_buttons("Emergency responders at the scene"))

    def _set_curr_time_date(self):
        self.time.setTime(QtCore.QTime.currentTime())
        self.date.setDate(QtCore.QDate.currentDate())

    def _set_logging(self):
        ui_handler = UiHandler(self.console)
        log.addHandler(ui_handler)

    def _remove_table_item_dialog(self,table):
        if table.currentItem():
            self.msgbox.setText (f'Are you sure you wish to delete the selected entry? \n"{table.currentItem().text()}"')
            ret_value = self.msgbox.exec_()
            if ret_value == QMessageBox.Ok:
                self._remove_table_item(table)

    def _add_table_item_dialog(self,dict_name):
        self._create_dialog_window(dict_name)
        if self.add_table.exec():
            if self.add_table.third.text().isdigit() and self.add_table.second.text() and self.add_table.third.text():
                new_item = (self.add_table.first.text(), self.add_table.second.text(), self.add_table.third.text())
                #twitter account table has more columns
                if dict_name == 'sources':
                    self._add_item_to_sources(dict_name, new_item)
                else:
                    self._add_item_to_table(dict_name, new_item)
            else:
                error = QMessageBox(self.add_table)
                error.setWindowTitle("A.R.M.")
                error.setText("Invalid input information, try again.")
                error.exec_()

    def _add_item_to_table(self,dict_name,item):
        old_dict = load_json_files(dict_name)
        indication, regex, row = item
        row_in_list = int(row)-1
        item_list = list(old_dict.items())
        item_list.insert(row_in_list,(regex,indication))
        new_dict = dict(item_list)
        load_json_files.edit_sources(dict_name,new_dict)
        self._get_dictionaries()
        self._fill_source_tables()

    def _add_item_to_sources(self,dict_name,item):
        old_dict = load_json_files(dict_name)
        account, city_state, relevancy = item
        item_list = list(old_dict.items())
        item_list.append((account, [city_state, int(relevancy)]))
        new_dict = dict(item_list)
        load_json_files.edit_sources(dict_name,new_dict)
        self._get_dictionaries()
        self._fill_source_tables()

    def _remove_table_item(self,table):
        row_in_list = int(table.currentRow())
        dict_name = self.table_source_dict[table]
        old_dict = load_json_files (dict_name)
        item_list = list (old_dict.items ())
        item_list.pop(row_in_list)
        new_dict = dict (item_list)
        load_json_files.edit_sources(dict_name, new_dict)
        self._get_dictionaries()
        self._fill_source_tables()

    def _edit_table_item(self, table):
        #load the source of the table and turn it into a list
        dict_name = self.table_source_dict[table]
        old_dict = load_json_files (dict_name)
        item_list = list (old_dict.items ())
        #create dialog window with edit title
        self._create_dialog_window(dict_name)
        self.add_table.setWindowTitle("Edit table entry:")
        #fill in the dialog forms
        row_in_list = int (table.currentRow ())
        self.add_table.first.setText(f"{item_list[row_in_list][1]}")
        self.add_table.second.setText(f"{item_list[row_in_list][0]}")
        self.add_table.third.setText(f"{row_in_list+1}")

        if self.add_table.exec():
            if self.add_table.third.text().isdigit() and self.add_table.second.text() and self.add_table.third.text():
                new_item = (self.add_table.first.text(), self.add_table.second.text(), self.add_table.third.text())
                #remove existing entry:
                self._remove_table_item(table)
                #adds the edited item (twitter account table has more columns)
                if dict_name == 'sources':
                    self._add_item_to_sources(dict_name, new_item)
                else:
                    self._add_item_to_table(dict_name, new_item)
            else:
                error = QMessageBox(self.add_table)
                error.setWindowTitle("A.R.M.")
                error.setText("Invalid input information, try again.")
                error.exec_()

    def _create_dialog_window(self,dict_name):
        self.add_table = QDialog(self)
        self.add_table.setFixedSize(400,140)
        self.add_table.setWindowTitle("New table entry:")
        self.add_table.first = QLineEdit (self.add_table)
        self.add_table.second = QLineEdit (self.add_table)
        self.add_table.third = QLineEdit (self.add_table)
        self.buttonBox = QDialogButtonBox (QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self.add_table)
        self.layout = QFormLayout (self.add_table)
        if dict_name == 'descriptions':
            column_names = ("Indication:","Text:","Row:")
        elif dict_name == 'sources':
            column_names = ("Account:","City/State:","Relevancy:")
        else:
            column_names = ("Indication name:", "Regex formula:","Row:")
        self.layout.addRow (column_names[0],  self.add_table.first)
        self.layout.addRow (column_names[1], self.add_table.second)
        self.layout.addRow (column_names[2], self.add_table.third)
        self.layout.addWidget (self.buttonBox)
        self.buttonBox.accepted.connect (self.add_table.accept)
        self.buttonBox.rejected.connect (self.add_table.reject)

    def _build_indication_tree(self):
        self.treeModel = QStandardItemModel()
        rootNode = self.treeModel.invisibleRootItem()
        self.tree_data = listener.load_indications_json()
        self._fill_tree (rootNode, self.tree_data)

        self.filter_proxy_model = LeafFilterProxyModel()
        self.filter_proxy_model.setSourceModel(self.treeModel)
        self.filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)

        self.indication_tree.setSortingEnabled(True)
        self.indication_tree.setHeaderHidden(True)
        self.indication_tree.setModel(self.filter_proxy_model)

    def toggle_indications(self):
        self.buttons_dict = {"Shots fired":self.shots_fired,"Sound of gunshots":self.sound_of_gunshots,"Police investigation":self.police_investigation,"Shot person (injured)":self.shooting,"Shot person (dead)":self.shooting,"Stabbed person (injured)":self.stabbing,"Stabbed person (dead)":self.stabbing,"Police at the scene":self.police_ats,"Ambulance at the scene":self.ambulance_ats,"Firefighters at the scene":self.firefighters_ats,"Emergency responders at the scene":self.emergency_services}
        for keys,values in self.buttons_dict.items():
                if values.isChecked():
                        values.setChecked(False)
        for keys,values in self.buttons_dict.items():
                if self.indications_list.findItems(keys,Qt.MatchFlag(0)):
                        values.setChecked(True)

    def toggle_buttons(self,indication):
        if  not self.indications_list.findItems(indication,Qt.MatchFlag(0)):
                self.indications_list.addItem(indication)
        elif self.indications_list.findItems(indication,Qt.MatchFlag(0)):
                try:
                        for x in range(self.indications_list.count()):
                                if indication == self.indications_list.item(x).text():
                                        self.indications_list.takeItem(x)
                except AttributeError:
                        pass
        self.toggle_indications()

    def clear_indications_list(self):
        self.indications_list.takeItem(self.indications_list.currentRow())
        self.toggle_indications()

    def add_indication_to_list(self,indication):
        #print(indication)
        if type(indication) is not str:
                self.indications_list.addItem(indication.data())
        else:
                self.indications_list.addItem(indication)
        self.toggle_indications()

    def _fill_tree(self,item, value):
        if type(value) is dict:
                for key, val in sorted(value.items()):
                        child = QStandardItem(key)
                        item.appendRow(child)
                        self._fill_tree(child, val)
        elif type(value) is list:
                for val in value:
                        if type(val) is dict:
                                self._fill_tree(item, val)
                        else:
                                child = QStandardItem(val)
                                item.appendRow(child)
        else:
                child = QStandardItem(value)   
                item.appendRow(child)

    def _fill_source_tables(self):
        source_tables = self.regex_indication_formulas_table, self.regex_address_formulas_table, self.twitter_accounts_table, self.templates_table
        for table in source_tables:
            table.clearContents()
            table.verticalHeader().setVisible(False)
            table.resizeColumnsToContents()
            table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self._fill_regex_formula_tables(self.regex_indication_formulas_table, self.indication_formulas)
        self._fill_regex_formula_tables(self.regex_address_formulas_table, self.address_formulas)
        self._fill_twitter_accounts_table(self.twitter_accounts_table, self.dictionary_sources)
        self._fill_templates_table(self.templates_table, self.dictionary_descriptions)
        self.twitter_accounts_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        for table in source_tables:
            table.resizeColumnsToContents()

    def _fill_templates_table(self,table, dictionary):
        table.clearContents()
        table.setRowCount(len(dictionary.items()))
        row = 0
        for keys,values in dictionary.items():
            table.setItem(row, 0, QTableWidgetItem(keys))
            table.setItem(row, 1, QTableWidgetItem(values))
            row += 1

    def _fill_regex_formula_tables (self,table, dictionary):
        table.clearContents()
        table.setRowCount(len(dictionary.items()))
        row = 0
        for keys,values in dictionary.items():
            table.setItem(row, 0, QTableWidgetItem(values))
            table.setItem(row, 1, QTableWidgetItem(keys))
            row += 1

    def _fill_twitter_accounts_table(self,table,dictionary):
        table.clearContents()
        table.setRowCount(len(dictionary.items()))
        row = 0
        for keys,values in dictionary.items():
            table.setItem(row, 0, QTableWidgetItem(keys))
            table.setItem(row, 1, QTableWidgetItem(values[0]))
            table.setItem(row, 2, QTableWidgetItem(str(values[1])))
            row += 1

    def get_address(self):
        address_info = f"{self.house_number.toPlainText()} {self.address.toPlainText()}"
        city = self.city_state.toPlainText()
        location_data = listener.get_gmaps_data(address_info, city)
        return location_data

    def fill_address_form(self, data: list):
        if data:
            address_no_number, house_nr, address_type, location_accuracy, coordinates \
                = data
            addr_list = self.address, self.house_number, self.location_accuracy,self.coordinates
            for item in addr_list:
                item.clear()
            self.address_type.setCurrentText(address_type)
            self.address.insertPlainText(address_no_number)
            self.house_number.insertPlainText(house_nr)
            if location_accuracy:
                self.location_accuracy.setValue(int(location_accuracy))
            self.coordinates.insertPlainText(coordinates)


    # def get_address(self):
    #     address_info = f"{self.house_number.toPlainText()} {self.address.toPlainText()}"
    #     address_type, address_no_number, house_nr, location_accuracy, coordinates\
    #         = listener.get_address_from_gmaps(address_info,self.city_state.toPlainText())
    #     addr_list = self.address, self.house_number, self.location_accuracy,self.coordinates
    #     for item in addr_list:
    #         item.clear()
    #     self.address_type.setCurrentText(address_type)
    #     self.address.insertPlainText(address_no_number)
    #     self.house_number.insertPlainText(house_nr)
    #     if location_accuracy:
    #         self.location_accuracy.setValue(int(location_accuracy))
    #     self.coordinates.insertPlainText(coordinates)

    def read_tweet_from_link(self):
        listener.read_tweet (self.tweet_link.toPlainText())

    def load_data_from_dict(self):
        self.tweet_data = listener.load_report_data()
        self.clear_fields()
        self.tweet_link.insertPlainText(self.tweet_data['link'])
        self.time_accuracy.insertPlainText (self.tweet_data['time_accuracy'])
        self.address.insertPlainText (self.tweet_data['address'])
        self.address_type.setCurrentText (self.tweet_data['address_type'])
        if self.tweet_data['all_indications'] != '':
            self.indications_list.addItems (self.tweet_data['all_indications'])
        self.coordinates.insertPlainText (self.tweet_data['coordinates'])
        self.city_state.insertPlainText (self.tweet_data['city_state'])
        self.date.setDate (QtCore.QDate.fromString (self.tweet_data['date'], "d MMMM yyyy"))
        self.hours_minutes = f"{self.tweet_data['starting_time'][0]} {self.tweet_data['starting_time'][1]}"
        self.time.setTime (QtCore.QTime.fromString (self.hours_minutes, "HH mm"))
        if str (self.tweet_data['location_accuracy']).isnumeric ():
            self.location_accuracy.setValue (int (self.tweet_data['location_accuracy']))
        if self.tweet_data['dead'] != "":
            self.dead.setValue (int (self.tweet_data['dead']))
        if self.tweet_data['injured'] != "":
            self.injured.setValue (int (self.tweet_data['injured']))
        self.description.insertPlainText (self.tweet_data['description'])
        self.duration.insertPlainText (self.tweet_data['duration'])
        self.house_number.insertPlainText (self.tweet_data['house_nr'])
        self.trust_score.setValue (int(self.tweet_data['relevancy']))
        self.account.insertPlainText (self.tweet_data['source'])
        self.tweet_text.insertPlainText (self.tweet_data['tweet_text'])
        self.toggle_indications()

    def _get_dictionaries(self):
        self.dictionary_abbreviations,self.indication_formulas,self.address_formulas,\
         self.dictionary_descriptions, self.dictionary_sources, self.dictionary_additional_facts = listener.load_source_files()
        self.table_source_dict = {self.regex_indication_formulas_table:"indication_formulas",
            self.regex_address_formulas_table:"address_formulas", self.twitter_accounts_table:"sources", self.templates_table:"descriptions"}

    def _get_settings(self):
        self.chrome_profile_dir_setting, self.run_minimized_setting,\
        self.load_images_setting, self.time_zone_setting,self.ava_username_value = listener.load_settings_files()

    def _get_css(self):
        self.setStyleSheet (load_json_files.load_css ())

    def clear_fields(self):
        fields_list=[self.tweet_link,self.tweet_text,self.description,self.indications_list,self.account,self.coordinates,self.house_number,self.address,self.city_state,self.time_accuracy,self.duration]
        set_to_0=[self.injured,self.dead,self.location_accuracy]
        self.trust_score.setValue(1)
        self.source.setCurrentText('Social Media')
        self.address_type.setCurrentText("address")
        for field in fields_list:
                field.clear()
        for field in set_to_0:
                field.setValue(0)
        self.time.setTime(QtCore.QTime.currentTime())
        self.date.setDate(QtCore.QDate.currentDate())
        self.toggle_indications()

    def get_data(self):
        self.tweet_data = {
        'coordinates':'','all_indications':'','starting_time':[0,0],'time_accuracy':'','date':'','duration':'','description':'','injured':'','dead':'','source':'','source_type':'','relevancy':'','link':'','address_type':'','address':'','house_nr':'','location_accuracy':'','tweet_text':'','city_state':''}
        self.tweet_data['time_accuracy']=self.time_accuracy.toPlainText()
        self.tweet_data['address']=self.address.toPlainText()
        self.tweet_data['address_type']=self.address_type.currentText()
        self.tweet_data['all_indications']= [self.indications_list.item(x).text() for x in range(self.indications_list.count())]
        self.tweet_data['coordinates']=self.coordinates.toPlainText()
        self.tweet_data['city_state'] = self.city_state.toPlainText()
        self.tweet_data['date'] = self.date.date().toString('d MMMM yyyy')
        self.tweet_data['starting_time'][0],self.tweet_data['starting_time'][1] = self.time.time().toString("HH,mm").split(',')
        if self.location_accuracy.value()!= 0:
                self.tweet_data['location_accuracy'] = self.location_accuracy.value() 
        if self.dead.value()!= 0:
                self.tweet_data['dead'] = self.dead.value()
        if self.injured.value() != 0:
                self.tweet_data['injured'] = self.injured.value()
        self.tweet_data['description'] = self.description.toPlainText()
        self.tweet_data['duration'] = self.duration.toPlainText()
        self.tweet_data['house_nr'] = self.house_number.toPlainText()
        self.tweet_data['relevancy'] = self.trust_score.value()
        self.tweet_data['source'] = self.account.toPlainText()
        self.tweet_data['tweet_text'] = self.tweet_text.toPlainText()
        self.tweet_data['source_type'] = self.source.currentText()
        self.tweet_data['link'] = self.tweet_link.toPlainText()
        listener.to_report_data(self.tweet_data)

    def _init_UI (self):
        self.resize (862, 581)
        self.setWindowTitle ("Automated Report Maker 1.01")
        icon = QtGui.QIcon ()
        icon.addPixmap (QtGui.QPixmap (":/icons/A.R.M. icons/robot-arm.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon (icon)
        self.setIconSize (QtCore.QSize (32, 32))
        self.centralwidget = QtWidgets.QWidget (self)
        self.menu_tab = QtWidgets.QTabWidget (self.centralwidget)
        self.menu_tab.setGeometry (QtCore.QRect (0, 0, 861, 591))
        self.menu_tab.setTabPosition (QtWidgets.QTabWidget.North)
        self.menu_tab.setTabShape (QtWidgets.QTabWidget.Rounded)
        self.menu_tab.setIconSize (QtCore.QSize (32, 32))
        self.menu_tab.setElideMode (QtCore.Qt.ElideLeft)
        self.menu_tab.setUsesScrollButtons (False)
        self.menu_tab.setTabsClosable (False)
        self.menu_tab.setMovable (False)
        self.menu_tab.setTabBarAutoHide (False)
        self.menu_tab.setCurrentIndex (0)
        font = QtGui.QFont ()
        font.setPointSize (12)
        self.menu_tab.setFont (font)
        # Report tab
        self.Report = QtWidgets.QWidget ()
        self.clear_indications = QtWidgets.QPushButton (self.Report)
        self.clear_indications.setGeometry (QtCore.QRect (390, 340, 41, 31))
        self.sound_of_gunshots = QtWidgets.QPushButton (self.Report)
        self.sound_of_gunshots.setGeometry (QtCore.QRect (440, 380, 41, 31))
        icon1 = QtGui.QIcon ()
        icon1.addPixmap (QtGui.QPixmap (":/icons/A.R.M. icons/auditory.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.sound_of_gunshots.setIcon (icon1)
        self.sound_of_gunshots.setIconSize (QtCore.QSize (25, 25))
        self.sound_of_gunshots.setCheckable (True)
        self.sound_of_gunshots.setObjectName ("sound_of_gunshots")
        self.dead_label = QtWidgets.QLabel (self.Report)
        self.dead_label.setGeometry (QtCore.QRect (300, 300, 41, 31))
        self.dead_label.setObjectName ("dead_label")
        self.police_ats = QtWidgets.QPushButton (self.Report)
        self.police_ats.setGeometry (QtCore.QRect (390, 460, 41, 31))
        icon2 = QtGui.QIcon ()
        icon2.addPixmap (QtGui.QPixmap (":/icons/A.R.M. icons/police-hat (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.police_ats.setIcon (icon2)
        self.police_ats.setIconSize (QtCore.QSize (25, 25))
        self.police_ats.setCheckable (True)
        self.police_ats.setObjectName ("police_ats")
        self.dead = QtWidgets.QSpinBox (self.Report)
        self.dead.setGeometry (QtCore.QRect (340, 300, 41, 31))
        self.dead.setMinimum (0)
        self.dead.setObjectName ("dead")
        self.firefighters_ats = QtWidgets.QPushButton (self.Report)
        self.firefighters_ats.setGeometry (QtCore.QRect (490, 460, 41, 31))
        icon3 = QtGui.QIcon ()
        icon3.addPixmap (QtGui.QPixmap (":/icons/A.R.M. icons/fireman (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.firefighters_ats.setIcon (icon3)
        self.firefighters_ats.setIconSize (QtCore.QSize (25, 25))
        self.firefighters_ats.setCheckable (True)
        self.firefighters_ats.setObjectName ("firefighters_ats")
        self.shots_fired = QtWidgets.QPushButton (self.Report)
        self.shots_fired.setGeometry (QtCore.QRect (390, 380, 41, 31))
        self.shots_fired.setAutoFillBackground (False)
        icon4 = QtGui.QIcon ()
        icon4.addPixmap (QtGui.QPixmap (":/icons/A.R.M. icons/bullets.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.shots_fired.setIcon (icon4)
        self.shots_fired.setCheckable (True)
        self.shots_fired.setObjectName ("shots_fired")
        self.stabbing = QtWidgets.QPushButton (self.Report)
        self.stabbing.setGeometry (QtCore.QRect (490, 420, 41, 31))
        icon5 = QtGui.QIcon ()
        icon5.addPixmap (QtGui.QPixmap (":/icons/A.R.M. icons/kill.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.stabbing.setIcon (icon5)
        self.stabbing.setCheckable (True)
        self.stabbing.setObjectName ("stabbing")
        self.police_investigation = QtWidgets.QPushButton (self.Report)
        icon6 = QtGui.QIcon ()
        icon6.addPixmap (QtGui.QPixmap (":/icons/A.R.M. icons/loupe.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.police_investigation.setIcon (icon6)
        self.police_investigation.setIconSize (QtCore.QSize (25, 25))
        self.police_investigation.setGeometry (QtCore.QRect (390, 420, 41, 31))
        self.police_investigation.setCheckable (True)
        self.police_investigation.setObjectName ("police_investigation")
        self.ambulance_ats = QtWidgets.QPushButton (self.Report)
        self.ambulance_ats.setGeometry (QtCore.QRect (440, 460, 41, 31))
        self.ambulance_ats.setAutoFillBackground (False)
        icon7 = QtGui.QIcon ()
        icon7.addPixmap (QtGui.QPixmap (":/icons/A.R.M. icons/ambulance.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ambulance_ats.setIcon (icon7)
        self.ambulance_ats.setCheckable (True)
        self.ambulance_ats.setObjectName ("ambulance_ats")
        self.injured = QtWidgets.QSpinBox (self.Report)
        self.injured.setGeometry (QtCore.QRect (250, 300, 41, 31))
        self.injured.setMinimum (0)
        self.injured.setObjectName ("injured")
        self.shooting = QtWidgets.QPushButton (self.Report)
        self.shooting.setGeometry (QtCore.QRect (440, 420, 41, 31))
        icon8 = QtGui.QIcon ()
        icon8.addPixmap (QtGui.QPixmap (":/icons/A.R.M. icons/pistol.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.shooting.setIcon (icon8)
        self.shooting.setIconSize (QtCore.QSize (32, 32))
        self.shooting.setCheckable (True)
        self.shooting.setObjectName ("shooting")
        self.indications_list = QtWidgets.QListWidget (self.Report)
        self.indications_list.setGeometry (QtCore.QRect (220, 340, 161, 181))
        self.indications_list.setObjectName ("indications_list")

        self.injured_label = QtWidgets.QLabel (self.Report)
        self.injured_label.setGeometry (QtCore.QRect (200, 300, 51, 31))
        self.injured_label.setObjectName ("injured_label")
        self.add_indication = QtWidgets.QPushButton (self.Report)
        self.add_indication.setGeometry (QtCore.QRect (180, 340, 41, 31))
        self.add_indication.setStyleSheet ("border-color: rgb(213, 220, 197);")
        self.add_indication.setObjectName ("add_indication")
        self.emergency_services = QtWidgets.QPushButton (self.Report)
        self.emergency_services.setGeometry (QtCore.QRect (540, 460, 41, 31))
        icon9 = QtGui.QIcon ()
        icon9.addPixmap (QtGui.QPixmap (":/icons/A.R.M. icons/helicopter.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.emergency_services.setIcon (icon9)
        self.emergency_services.setCheckable (True)
        self.emergency_services.setObjectName ("emergency_services")
        self.run_bot = QtWidgets.QPushButton (self.Report)
        self.run_bot.setGeometry (QtCore.QRect (780, 300, 71, 31))
        self.run_bot.setObjectName("run_bot")
        self.account = QtWidgets.QPlainTextEdit (self.Report)
        self.account.setEnabled (True)
        self.account.setGeometry (QtCore.QRect (400, 40, 171, 31))
        self.account.setObjectName ("account")
        self.time = QtWidgets.QTimeEdit (self.Report)
        self.time.setGeometry (QtCore.QRect (400, 210, 111, 31))
        self.time.setObjectName ("time")
        self.gmaps_button = QtWidgets.QPushButton (self.Report)
        self.gmaps_button.setGeometry (QtCore.QRect (810, 10, 41, 31))
        icon10 = QtGui.QIcon ()
        icon10.addPixmap (QtGui.QPixmap (":/icons/A.R.M. icons/earth.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.gmaps_button.setIcon (icon10)
        self.gmaps_button.setIconSize (QtCore.QSize (24, 24))
        self.gmaps_button.setObjectName ("gmaps_button")
        self.label_trust_score = QtWidgets.QLabel (self.Report)
        self.label_trust_score.setGeometry (QtCore.QRect (400, 80, 71, 21))
        self.label_trust_score.setObjectName ("label_trust_score")
        self.label_location_accuracy = QtWidgets.QLabel (self.Report)
        self.label_location_accuracy.setGeometry (QtCore.QRect (720, 110, 71, 21))
        self.label_location_accuracy.setObjectName ("label_location_accuracy")
        self.source = QtWidgets.QComboBox (self.Report)
        self.source.setGeometry (QtCore.QRect (580, 40, 101, 31))
        self.source.setObjectName ("source")
        self.source.addItem ("Social Media")
        self.source.addItem ("News Media")
        font.setPointSize (10)
        self.source.setFont (font)
        self.time_accuracy = QtWidgets.QPlainTextEdit (self.Report)
        self.time_accuracy.setEnabled (True)
        self.time_accuracy.setGeometry (QtCore.QRect (400, 280, 51, 31))
        self.time_accuracy.setObjectName ("time_accuracy")
        self.label_address = QtWidgets.QLabel (self.Report)
        self.label_address.setGeometry (QtCore.QRect (400, 110, 71, 31))
        self.label_address.setObjectName ("label_address")
        self.house_number = QtWidgets.QPlainTextEdit (self.Report)
        self.house_number.setEnabled (True)
        self.house_number.setGeometry (QtCore.QRect (400, 140, 71, 31))
        self.house_number.setObjectName ("house_number")
        self.label_time_accuracy = QtWidgets.QLabel (self.Report)
        self.label_time_accuracy.setGeometry (QtCore.QRect (400, 250, 111, 21))
        self.label_time_accuracy.setFont (font)
        self.label_time_accuracy.setObjectName ("label_time_accuracy")
        self.label_time_duration = QtWidgets.QLabel (self.Report)
        self.label_time_duration.setGeometry (QtCore.QRect (530, 250, 111, 21))
        self.label_time_duration.setFont (font)
        self.label_time_duration.setObjectName ("label_time_duration")
        self.label_address_type = QtWidgets.QLabel (self.Report)
        self.label_address_type.setGeometry (QtCore.QRect (500, 110, 91, 21))
        self.label_address_type.setObjectName ("label_address_type")
        self.date = QtWidgets.QDateEdit (self.Report)
        self.date.setGeometry (QtCore.QRect (530, 210, 111, 31))
        self.date.setCalendarPopup (True)
        font.setPointSize (12)
        self.date.setFont (font)
        self.date.setObjectName ("date")
        self.address_type = QtWidgets.QComboBox (self.Report)
        self.address_type.setGeometry (QtCore.QRect (590, 110, 91, 21))
        self.address_type.setObjectName ("address_type")
        self.address_type.addItem ("address")
        self.address_type.addItem ("block")
        self.address_type.addItem ("lat/long")
        self.coordinates = QtWidgets.QPlainTextEdit (self.Report)
        self.coordinates.setEnabled (True)
        self.coordinates.setGeometry (QtCore.QRect (690, 40, 161, 31))
        font = QtGui.QFont ()
        font.setPointSize (10)
        self.coordinates.setFont (font)
        self.coordinates.setStyleSheet ("background-color: rgb(213, 220, 197);")
        self.coordinates.setObjectName ("coordinates")
        self.city_state = QtWidgets.QPlainTextEdit (self.Report)
        self.city_state.setEnabled (True)
        self.city_state.setGeometry (QtCore.QRect (690, 140, 161, 31))
        self.city_state.setObjectName ("city_state")
        self.location_accuracy = QtWidgets.QSpinBox (self.Report)
        self.location_accuracy.setGeometry (QtCore.QRect (790, 110, 61, 21))
        self.location_accuracy.setMinimum (0)
        self.location_accuracy.setMaximum (500)
        self.location_accuracy.setSingleStep (50)
        self.location_accuracy.setObjectName ("location_accuracy")
        self.label_account = QtWidgets.QLabel (self.Report)
        self.label_account.setGeometry (QtCore.QRect (400, 10, 121, 21))
        self.label_account.setFrameShape (QtWidgets.QFrame.NoFrame)
        self.label_account.setFrameShadow (QtWidgets.QFrame.Plain)
        self.label_account.setObjectName ("label_account")
        self.trust_score = QtWidgets.QSpinBox (self.Report)
        self.trust_score.setGeometry (QtCore.QRect (480, 80, 41, 21))
        self.trust_score.setSuffix ("")
        self.trust_score.setMinimum (1)
        self.trust_score.setMaximum (3)
        self.trust_score.setObjectName ("trust_score")
        self.label_time_and_date = QtWidgets.QLabel (self.Report)
        self.label_time_and_date.setGeometry (QtCore.QRect (400, 180, 111, 21))
        sizePolicy = QtWidgets.QSizePolicy (QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch (0)
        sizePolicy.setVerticalStretch (0)
        sizePolicy.setHeightForWidth (self.label_time_and_date.sizePolicy ().hasHeightForWidth ())
        self.label_time_and_date.setSizePolicy (sizePolicy)
        self.label_time_and_date.setFont (font)
        self.label_time_and_date.setObjectName ("label_time_and_date")
        self.address = QtWidgets.QPlainTextEdit (self.Report)
        self.address.setEnabled (True)
        self.address.setGeometry (QtCore.QRect (480, 140, 201, 31))
        self.address.setObjectName ("address")
        self.duration = QtWidgets.QPlainTextEdit (self.Report)
        self.duration.setEnabled (True)
        self.duration.setGeometry (QtCore.QRect (530, 280, 51, 31))
        self.duration.setObjectName ("duration")
        self.label_tweet_link = QtWidgets.QLabel (self.Report)
        self.label_tweet_link.setGeometry (QtCore.QRect (10, 10, 131, 21))
        self.label_tweet_link.setObjectName ("label_tweet_link")
        self.enter_tweet_link = QtWidgets.QPushButton (self.Report)
        self.enter_tweet_link.setGeometry (QtCore.QRect (340, 40, 51, 31))
        self.enter_tweet_link.setObjectName ("enter_tweet_link")
        self.paste_link = QtWidgets.QPushButton (self.Report)
        self.paste_link.setGeometry (QtCore.QRect (300, 20, 31, 21))
        self.paste_link.setObjectName ("paste_link")
        # self.read_text = QtWidgets.QPushButton (self.Report)
        # self.read_text.setGeometry (QtCore.QRect (340, 110, 51, 31))
        # self.read_text.setObjectName ("read_text")
        # self.paste_tweet_text = QtWidgets.QPushButton (self.Report)
        # self.paste_tweet_text.setGeometry (QtCore.QRect (300, 90, 31, 21))
        # self.paste_tweet_text.setObjectName ("paste_tweet_text")
        # self.paste_description = QtWidgets.QPushButton (self.Report)
        # self.paste_description.setGeometry (QtCore.QRect (300, 210, 31, 21))
        # self.paste_description.setObjectName ("paste_description")
        self.tweet_text = QtWidgets.QPlainTextEdit (self.Report)
        self.tweet_text.setGeometry (QtCore.QRect (10, 100, 321, 111))
        self.tweet_text.setObjectName ("tweet_text")
        self.tweet_link_clear = QtWidgets.QPushButton (self.Report)
        self.tweet_link_clear.setGeometry (QtCore.QRect (340, 10, 51, 31))
        self.tweet_link_clear.setObjectName ("tweet_link_clear")
        self.tweet_link = QtWidgets.QPlainTextEdit (self.Report)
        self.tweet_link.setGeometry (QtCore.QRect (10, 40, 321, 41))
        self.tweet_link.setObjectName ("tweet_link")
        self.label_datum = QtWidgets.QLabel (self.Report)
        self.label_datum.setGeometry (QtCore.QRect (10, 310, 91, 21))
        self.label_datum.setObjectName ("label_datum")
        self.description = QtWidgets.QPlainTextEdit (self.Report)
        self.description.setGeometry (QtCore.QRect (10, 230, 321, 51))
        self.description.setObjectName ("description")
        self.indication_selection = QtWidgets.QLineEdit (self.Report)
        self.indication_selection.setGeometry (QtCore.QRect (10, 340, 161, 31))
        self.indication_selection.setObjectName ("indication_selection")
        self.indication_tree = QtWidgets.QTreeView (self.Report)
        self.indication_tree.setGeometry (QtCore.QRect (10, 370, 211, 151))
        sizePolicy = QtWidgets.QSizePolicy (QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch (0)
        sizePolicy.setVerticalStretch (0)
        sizePolicy.setHeightForWidth (self.indication_tree.sizePolicy ().hasHeightForWidth ())
        self.indication_tree.setSizePolicy (sizePolicy)
        font.setPointSize (9)
        self.indication_tree.setFont (font)
        self.indication_tree.setAutoFillBackground (False)
        self.indication_tree.setFrameShape (QtWidgets.QFrame.StyledPanel)
        self.indication_tree.setFrameShadow (QtWidgets.QFrame.Sunken)
        self.indication_tree.setSizeAdjustPolicy (QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.indication_tree.setEditTriggers (QtWidgets.QAbstractItemView.NoEditTriggers)
        self.indication_tree.setAlternatingRowColors (False)
        self.indication_tree.setRootIsDecorated (True)
        self.indication_tree.setUniformRowHeights (False)
        self.indication_tree.setAnimated (False)
        self.indication_tree.setAllColumnsShowFocus (True)
        self.indication_tree.setWordWrap (True)
        self.indication_tree.setHeaderHidden (True)
        self.indication_tree.setObjectName ("indication_tree")
        self.indication_tree.header ().setVisible (False)
        self.indication_tree.setExpandsOnDoubleClick(False)
        self.indication_tree.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        icon11 = QtGui.QIcon ()
        icon11.addPixmap (QtGui.QPixmap (":/icons/A.R.M. icons/bionic-arm.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.menu_tab.addTab (self.Report, icon11, "Report")
        self.Sources = QtWidgets.QWidget ()
        self.Sources.setObjectName ("Sources")
        # self.Sources.setText("Sources")
        icon12 = QtGui.QIcon ()
        icon12.addPixmap (QtGui.QPixmap (":/icons/A.R.M. icons/book.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.menu_tab.addTab (self.Sources, icon12, "Sources")
        self.Settings = QtWidgets.QWidget ()
        self.Settings.setObjectName ("Settings")
        icon13 = QtGui.QIcon ()
        icon13.addPixmap (QtGui.QPixmap (":/icons/A.R.M. icons/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.menu_tab.addTab (self.Settings, icon13, "Settings")
        self.setCentralWidget (self.centralwidget)
        # Sources Tab
        self.twitter_accounts_table = QtWidgets.QTableWidget (self.Sources)
        self.twitter_accounts_table.setGeometry (QtCore.QRect (520, 40, 331, 231))
        self.twitter_accounts_table.setStyleSheet ("background-color: rgb(213, 220, 197);")
        self.twitter_accounts_table.setSizeAdjustPolicy (QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.twitter_accounts_table.setObjectName ("twitter_accounts_table")
        self.twitter_accounts_table.setColumnCount (3)
        item = QtWidgets.QTableWidgetItem ()
        item.setText ("Account")
        self.twitter_accounts_table.setHorizontalHeaderItem (0, item)
        item = QtWidgets.QTableWidgetItem ()
        item.setText ("City/State")
        self.twitter_accounts_table.setHorizontalHeaderItem (1, item)
        item = QtWidgets.QTableWidgetItem ()
        item.setText ("Relevancy")
        self.twitter_accounts_table.setHorizontalHeaderItem (2, item)
        self.twitter_accounts_table.horizontalHeader ().setStretchLastSection (True)
        self.twitter_accounts_table.setAutoScroll (False)
        self.add_twitter_accounts = QtWidgets.QPushButton (self.Sources)
        self.add_twitter_accounts.setGeometry (QtCore.QRect (480, 40, 31, 21))
        self.add_twitter_accounts.setObjectName ("add_twitter_accounts")
        self.remove_twitter_accounts = QtWidgets.QPushButton (self.Sources)
        self.remove_twitter_accounts.setGeometry (QtCore.QRect (480, 60, 31, 21))
        self.remove_twitter_accounts.setObjectName ("remove_twitter_accounts")
        self.regex_indication_formulas_table = QtWidgets.QTableWidget (self.Sources)
        self.regex_indication_formulas_table.setGeometry (QtCore.QRect (10, 40, 381, 311))
        self.regex_indication_formulas_table.setObjectName ("regex_indication_formulas_table")
        self.regex_indication_formulas_table.setColumnCount (2)
        self.regex_indication_formulas_table.setAutoScroll(False)
        #self.regex_indication_formulas_table.row
        item = QtWidgets.QTableWidgetItem ()
        item.setText ("Indication")
        self.regex_indication_formulas_table.setHorizontalHeaderItem (0, item)
        item = QtWidgets.QTableWidgetItem ()
        item.setText ("Regex Formula")
        self.regex_indication_formulas_table.setHorizontalHeaderItem (1, item)
        self.regex_indication_formulas_table.horizontalHeader ().setStretchLastSection (True)
        self.add_regex_indication_formula = QtWidgets.QPushButton (self.Sources)
        self.add_regex_indication_formula.setGeometry (QtCore.QRect (400, 40, 31, 21))
        self.add_regex_indication_formula.setObjectName ("add_regex_indication_formula")
        self.remove_regex_indication_formula = QtWidgets.QPushButton (self.Sources)
        self.remove_regex_indication_formula.setGeometry (QtCore.QRect (400, 60, 31, 21))
        self.remove_regex_indication_formula.setObjectName ("remove_regex_indication_formula")
        self.edit_regex_indication_formula = QtWidgets.QPushButton (self.Sources)
        self.edit_regex_indication_formula.setGeometry (QtCore.QRect (400, 80, 31, 21))
        self.edit_regex_indication_formula.setObjectName ('edit_regex_indication_formula')
        self.regex_formulas_label = QtWidgets.QLabel (self.Sources)
        self.regex_formulas_label.setGeometry (QtCore.QRect (10, 10, 131, 21))
        self.regex_formulas_label.setObjectName ("regex_formulas_label")
        self.twitter_accounts_label = QtWidgets.QLabel (self.Sources)
        self.twitter_accounts_label.setGeometry (QtCore.QRect (520, 10, 131, 21))
        self.twitter_accounts_label.setObjectName ("twitter_accounts_label")
        self.templates_label = QtWidgets.QLabel (self.Sources)
        self.templates_label.setGeometry (QtCore.QRect (520, 280, 131, 21))
        self.templates_label.setObjectName ("templates_label")
        self.templates_table = QtWidgets.QTableWidget (self.Sources)
        self.templates_table.setGeometry (QtCore.QRect (520, 310, 331, 211))
        self.templates_table.setSizeAdjustPolicy (QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.templates_table.setObjectName ("templates_table")
        self.templates_table.setColumnCount (2)
        item = QtWidgets.QTableWidgetItem ()
        item.setText ("Indication")
        self.templates_table.setHorizontalHeaderItem (0, item)
        item = QtWidgets.QTableWidgetItem ()
        item.setText ("Text")
        self.templates_table.setHorizontalHeaderItem (1, item)
        self.templates_table.horizontalHeader ().setStretchLastSection (True)
        self.templates_table.setAutoScroll(False)
        self.add_template = QtWidgets.QPushButton (self.Sources)
        self.add_template.setGeometry (QtCore.QRect (480, 310, 31, 21))
        self.add_template.setObjectName ("add_template")
        self.remove_template = QtWidgets.QPushButton (self.Sources)
        self.remove_template.setGeometry (QtCore.QRect (480, 330, 31, 21))
        self.remove_template.setObjectName ("remove_template")
        self.edit_template = QtWidgets.QPushButton (self.Sources)
        self.edit_template.setGeometry (QtCore.QRect (480, 350, 31, 21))
        self.edit_template.setObjectName ("edit_template")
        self.regex_address_formulas_table = QtWidgets.QTableWidget (self.Sources)
        self.regex_address_formulas_table.setGeometry (QtCore.QRect (10, 360, 381, 161))
        self.regex_address_formulas_table.setObjectName ("regex_address_formulas_table")
        self.regex_address_formulas_table.setColumnCount (2)
        self.regex_address_formulas_table.setAutoScroll(False)
        item = QtWidgets.QTableWidgetItem ()
        item.setText ("Indication")
        self.regex_address_formulas_table.setHorizontalHeaderItem (0, item)
        item = QtWidgets.QTableWidgetItem ()
        item.setText ("Regex Formula")
        self.regex_address_formulas_table.setHorizontalHeaderItem (1, item)
        self.regex_address_formulas_table.horizontalHeader ().setStretchLastSection (True)
        self.add_regex_address_formula = QtWidgets.QPushButton (self.Sources)
        self.add_regex_address_formula.setGeometry (QtCore.QRect (400, 360, 31, 21))
        self.add_regex_address_formula.setObjectName ("add_regex_address_formula")
        self.remove_regex_address_formula = QtWidgets.QPushButton (self.Sources)
        self.remove_regex_address_formula.setGeometry (QtCore.QRect (400, 380, 31, 21))
        self.remove_regex_address_formula.setObjectName ("remove_regex_address_formula")
        self.edit_regex_address_formula = QtWidgets.QPushButton (self.Sources)
        self.edit_regex_address_formula.setGeometry (QtCore.QRect (400, 400, 31, 21))
        self.edit_regex_address_formula.setObjectName ("edit_regex_address_formula")

        # Settings Tab
        self.chrome_headless = QtWidgets.QCheckBox (self.Settings)
        self.chrome_headless.setGeometry (QtCore.QRect (470, 40, 261, 21))
        font.setPointSize (10)
        self.chrome_headless.setFont (font)
        self.chrome_headless.setObjectName ("chrome_headless")
        self.load_images = QtWidgets.QCheckBox (self.Settings)
        self.load_images.setGeometry (QtCore.QRect (470, 70, 261, 21))
        font.setPointSize (10)
        self.load_images.setFont (font)
        self.load_images.setObjectName ("load_images")
        self.chrome_user_profile = QtWidgets.QPlainTextEdit (self.Settings)
        self.chrome_user_profile.setGeometry (QtCore.QRect (10, 110, 351, 44))
        self.chrome_user_profile.setObjectName ("chrome_user_profile")
        self.chrome_user_profile_label = QtWidgets.QLabel (self.Settings)
        self.chrome_user_profile_label.setGeometry (QtCore.QRect (10, 80, 161, 21))
        self.chrome_user_profile_label.setObjectName ("chrome_user_profile_label")
        self.default_time_zone = QtWidgets.QSpinBox (self.Settings)
        self.default_time_zone.setGeometry (QtCore.QRect (10, 200, 41, 31))
        self.default_time_zone.setFont (font)
        self.default_time_zone.setMinimum (-12)
        self.default_time_zone.setMaximum (12)
        self.default_time_zone.setProperty ("value", 0)
        self.default_time_zone.setObjectName ("default_time_zone")
        self.default_time_zone_label = QtWidgets.QLabel (self.Settings)
        self.default_time_zone_label.setGeometry (QtCore.QRect (10, 170, 191, 21))
        self.default_time_zone_label.setObjectName ("default_time_zone_label")
        self.ava_username = QtWidgets.QPlainTextEdit (self.Settings)
        self.ava_username.setGeometry (QtCore.QRect (10, 40, 261, 31))
        self.ava_username.setObjectName ("ava_username")
        self.ava_username_label = QtWidgets.QLabel (self.Settings)
        self.ava_username_label.setGeometry (QtCore.QRect (10, 10, 161, 21))
        self.ava_username_label.setObjectName ("ava_username_label")
        self.ava_username_button = QtWidgets.QPushButton (self.Settings)
        self.ava_username_button.setGeometry (QtCore.QRect (280, 50, 31, 21))
        self.ava_username_button.setObjectName ("ava_username_button")
        self.chrome_user_profile_button = QtWidgets.QPushButton (self.Settings)
        self.chrome_user_profile_button.setGeometry (QtCore.QRect (370, 134, 31, 21))
        self.chrome_user_profile_button.setObjectName ("ava_username_button")

        self.msgbox = QMessageBox (self)
        self.msgbox.setIcon(QMessageBox.Information)
        self.msgbox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.msgbox.setWindowTitle('A.R.M.')

        self.tweet_progress_bar = QtWidgets.QProgressBar(self.Report)
        self.tweet_progress_bar.setGeometry(QtCore.QRect(117, 10, 171, 21))
        self.tweet_progress_bar.setObjectName("tweet_progress_bar")
        self.tweet_progress_bar.setMaximum(120)
        self.tweet_progress_bar.setVisible(False)

        self.console = QtWidgets.QPlainTextEdit(self.Report)
        self.console.setGeometry(QtCore.QRect(590, 340, 261, 181))
        self.console.setObjectName("console")
        self.console.setReadOnly(True)


    def start_prog_bar(self):
        self.tweet_progress_bar.setVisible(True)
        self.tweet_progress_bar.setValue(0)
        self.enter_tweet_link.setEnabled(False)

    def change_prog_value(self, val):
        self.tweet_progress_bar.setValue(val)

    def end_prog_bar(self):
        self.tweet_progress_bar.setValue(100)
        self.tweet_progress_bar.setVisible(False)
        self.enter_tweet_link.setEnabled(True)


class ProgBar(QRunnable):
    def __init__(self):
        super(ProgBar, self).__init__()
        self.signals = WorkerSignals()
        self.start_sig = WorkerSignals()
        self.change_value = pyqtSignal(int)

    def run(self):
        self.signals.start_sig.emit()
        cnt = 0
        while cnt < 113:
            cnt += 1
            time.sleep(0.1)
            self.signals.change_value.emit(cnt)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        result = self.fn(*self.args,**self.kwargs)
        self.signals.result.emit(result)


class WorkerSignals(QObject):
    start_sig = pyqtSignal()
    change_value = pyqtSignal(int)
    result = pyqtSignal(object)


app = QtWidgets.QApplication(sys.argv)
Main = ARM_Main()
Main.show()
sys.exit(app.exec_())
