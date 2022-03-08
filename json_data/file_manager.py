import json
import os


def load_sources(name=None):
    if name is not None:
        file_path = f"./json_data/{name}.json"
        with open(file_path, 'r') as file:
            dictionary = json.load(file)
            for keys, values in dictionary.items():
                return values
    else:
        list_of_results = []
        list_of_files = [
            "./json_data/abbreviations.json",
            "./json_data/indication_formulas.json",
            "./json_data/address_formulas.json",
            "./json_data/descriptions.json",
            "./json_data/sources.json",
            "./json_data/additional_facts.json"
        ]
        for path in list_of_files:
            with open(path) as json_file:
                dictionary = json.load(json_file)
                for keys, values in dictionary.items():
                    list_of_results.append(values)
        return list_of_results
    # self.dictionary_abbreviations,self.indication_formulas,self.address_formulas,\
    # self.dictionary_descriptions, self.dictionary_sources, self.dictionary_additional_facts = list_of_results


def load_settings():
    with open('./json_data/settings.json', 'r') as settings_dictionary:
        settings_json = json.load(settings_dictionary)
        settings = settings_json['user_profile_path'], settings_json['run_headless'], settings_json['load_images'], \
                 settings_json['default_time_zone'], settings_json['ava_username']
        return settings
        # self.chrome_profile_dir, self.run_headless, self.load_images, self.time_zone = settings


def edit_setting(name, value):
    file_path = './json_data/settings.json'
    with open(file_path, 'r+', encoding='utf-8') as file:
        input_file = json.load(file)
        input_file[f'{name}'] = value
    os.remove(file_path)
    with open(file_path, 'w') as file:
        json.dump(input_file, file, indent=4)


def edit_sources(name, dictionary):
    file_path = f"./json_data/{name}.json"
    with open(file_path, 'w') as file:
        new_dict = {f"{name}": dictionary}
        json.dump(new_dict, file, indent=1)


def load_css(css=""):
    file_path = "./ui/ARM_stylesheet.css"
    with open(file_path, 'r', encoding='utf-8') as file:
        css = css.join(file.readlines())
        return css


def load_report_data():
    with open('./json_data/report_data.json', 'r') as file:
        report_data = json.load(file)
        return report_data['reports'][0]


def load_indications_json():
    with open('./json_data/indications.json', 'r') as indications:
        data = json.load(indications)
        return data


def write_report_json(data):
    with open('./json_data/report_data.json', 'w') as file:
        input_data = {"reports": [data]}
        json.dump(input_data, file, indent=4)
