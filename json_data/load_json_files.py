
import json
import os


def load_json_files(name=None):
    if name is not None:
        file_path = f"arm/json_data/{name}.json"
        with open (file_path, 'r') as file:
            dictionary = json.load(file)
            for keys, values in dictionary.items():
                return(values)
    else:
        list_of_results = []
        list_of_files = [
            "arm/json_data/abbreviations.json",
            "arm/json_data/indication_formulas.json",
            "arm/json_data/address_formulas.json",
            "arm/json_data/descriptions.json",
            "arm/json_data/sources.json",
            "arm/json_data/additional_facts.json"
        ]
        for path in list_of_files:
            with open (path) as json_file:
                dictionary = json.load (json_file)
                for keys, values in dictionary.items():
                    list_of_results.append(values)
        return list_of_results
    #self.dictionary_abbreviations,self.indication_formulas,self.address_formulas,\
    #self.dictionary_descriptions, self.dictionary_sources, self.dictionary_additional_facts = list_of_results


def load_settings():
    with open('arm/json_data/settings.json', 'r') as settings_dictionary:
        settings_json = json.load(settings_dictionary)
        settings = settings_json['user_profile_path'], settings_json['run_headless'], settings_json['load_images'],settings_json['default_time_zone'], settings_json['ava_username']
        return settings
        #self.chrome_profile_dir, self.run_headless, self.load_images, self.time_zone = settings


def edit_setting(name,value):
    file_path = 'arm/json_data/settings.json'
    with open (file_path, 'r+',encoding='utf-8') as file:
        input_file = json.load(file)
        input_file[f'{name}'] = value
    os.remove(file_path)
    with open(file_path, 'w') as file:
        json.dump (input_file, file, indent=4)


def edit_sources(name, dict):
    file_path = f"arm/json_data/{name}.json"
    with open(file_path,'w') as file:
        new_dict = {f"{name}": dict}
        json.dump(new_dict, file, indent=1)


def load_css(css=""):
    file_path = "arm/ui/ARM_stylesheet.css"
    with open(file_path, 'r',encoding='utf-8') as file:
        css = css.join(file.readlines())
        return css
