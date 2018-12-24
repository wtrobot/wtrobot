import difflib
import json
import logging
import os
import pathlib
import re
from io import StringIO
import threading
import lxml.etree
import yaml
from requests import request
from datetime import datetime
from .base_manager import UtilityMixin

class I18N_TEST(UtilityMixin):
    def __init__(self, driver=None, thread_name=None):

        self.base_config_dict = self.config_data
        self.log(self.base_config_dict["log_file"])
        self.driver = driver
        self.poData = {}
        self.allPOData = {}
        self.variablePOData = {}
        self.locale = (self.base_config_dict["locale"]).split("-")[0]
        self.zanata_data = self.base_config_dict["zanata_data"]
        if not re.match(r"en", self.locale):
            self.dataReader = threading.Thread(
                target=self.translation_reader, args=(self.poData, self.locale)
            )
            self.dataReader.start()

    def log(self,log_file):
        FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(lineno)d:%(message)s"
        datestr = "%m/%d/%Y %I:%M:%S %p"
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(fmt=FORMAT,datefmt=datestr)
        file_handler = logging.FileHandler(filename=log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def tree_obj(self):
        ''' Create a lxml tree object and return '''
        parser = lxml.etree.HTMLParser()
        html_source = self.driver.page_source
        return lxml.etree.parse(StringIO(html_source), parser)

    def yaml_loader(self, filepath):
        ''' Read the .yml and convert to dict '''
        data = dict()
        if os.path.isfile(filepath):
            with open(filepath, "r") as obj:
                data = yaml.load(obj)
            if not data:
                return dict()
        return data

    def yaml_dump(self, filepath, data):
        ''' Write dict into .yml file '''
        with open(filepath, "w") as obj:
            yaml.dump(data, obj, default_flow_style=False)

    def getText(self, tree, field):
        ''' 
        It is a function to get the text out of XPATH element.
        return: List regresion with a regex validator to avoud number.
        '''
        return [
            i.replace("\n", "").strip()
            for i in tree.xpath(tree.getpath(field) + "/text()")
            if i.strip() and not re.match(r"^[0-9.]*$", i.strip())
        ]

    def getTextWithXpath(self, xpath):
        ''' This function will return the valid texts with its XPATHs. '''
        tree = self.tree_obj()
        fields = tree.xpath(xpath)
        # Dictionary comprehension for fields.
        fields = {
            tree.getpath(field): self.getText(tree, field)[0]
            for field in fields
            if tree.xpath(tree.getpath(field) + "/text()")
            and not re.search(r"\/script$", tree.getpath(field))
            and self.getText(tree, field)
        }
        return fields

    def i18n(self):
        ''' This function should all the function internally to do i18n testing '''
        self.i18n_get_all_text()

    def i18n_get_all_text(self):
        """
        This module will scrape the entire text from single page and make ".yml" file to record the text
        :return:
        """
        print("web-scrape on url : {}".format(self.driver.current_url))
        self.logger.info("web-scrape on url : {}".format(self.driver.current_url))

        # xpath to scrape entire text from webpage
        xpath = "//body//*[not(self::script) and not(self::noscript)]//*[contains(.,text())]"

        # yml file which will have all the text scrapped from web   { url: {xpath of text:text} }
        filepath = []
        fname = self.base_config_dict["lang_scrape_filepath"]
        if not fname:
            fname = "lang_scrape.yml"
        textDir = self.base_config_dict["text_dir"]
        locale = self.base_config_dict["locale"]
        if textDir in os.listdir():
            if locale in os.listdir(textDir):
                filepath.extend([textDir, locale, fname])
            else:
                filepath.extend([textDir, locale])
                os.mkdir(os.path.join(*filepath))
                filepath.append(fname)
        else:
            filepath.extend([textDir, locale])
            # print(filepath)
            pathlib.Path(os.path.join(*filepath)).mkdir(parents=True, exist_ok=True)
            filepath.append(fname)

        filepath = os.path.join(*filepath)
        locale_lang_scrape = self.yaml_loader(filepath)

        # main function to get all the text with xpaths.
        data = self.getTextWithXpath(xpath)

        if not str(self.driver.current_url) in locale_lang_scrape:
            locale_lang_scrape[str(self.driver.current_url)] = dict()
        locale_lang_scrape[str(self.driver.current_url)] = data
        print(locale_lang_scrape.keys())
        self.yaml_dump(filepath, locale_lang_scrape)

        filepath = [textDir, "en-US", fname]
        filepath = os.path.join(*filepath)
        en_US_scrape = self.yaml_loader(filepath)

        if not re.match(r"en", self.locale):
            self.dataReader.join()
            if self.poData["data"]:
                poData = self.poData["data"]
                # print(poData)
                report = self.generate_report(poData, locale_lang_scrape, en_US_scrape)
                # print(report)
                filepath = self.base_config_dict["report"]
                self.isDirPresent(filepath)
                filepath = os.path.join(*filepath)
                print("dumping into yml")
                self.yaml_dump(filepath, report)
        print("I18N")
        return True

    def isDirPresent(self, filepath):
        ''' Validating if the folder is present or not. '''
        print("searching directory")
        for i in range(1, len(filepath)):
            if not os.path.exists(os.path.join(*filepath[:i])):
                print("directory not found but creating one")
                os.mkdir(os.path.join(*filepath[:i]))

    def getFlag(self, englishUI, localeUI):
        ''' Returns the comments for the report regarding the words found by I18N module. '''

        # print(self.allPOData)
        if (
            localeUI
            and re.match(englishUI, localeUI)
            and not englishUI in self.allPOData
            and not self.isInVariableData(englishUI)
        ):
            return "{} :- Text not found in PO.".format(englishUI)

        elif (
            localeUI
            and re.match(englishUI, localeUI)
            and englishUI in self.allPOData
            and not self.allPOData[englishUI]
        ):
            return "{} :- Text found in PO but no translated was found.".format(
                englishUI
            )

        elif (
            localeUI
            and re.match(englishUI, localeUI)
            and englishUI in self.allPOData
            and self.allPOData[englishUI]
        ):
            return "{}:{} :- Text is not yet updated in UI as the translation is present in PO or text is present in original state as translation.".format(
                englishUI, self.allPOData[englishUI]
            )

        elif not localeUI:
            return "{} :- Translation not found on UI".format(englishUI)

    def translation_reader(self, poData, locale):
        ''' 
        Function to read the pre-processed po data. 
        This function is called as a tread at the begining of WTRobot as it takes 9+ seconds to read this data.
        '''
        first_project = self.zanata_data["projects"][0]
        project_name = first_project["projectSlug"].split("-")[0]
        output_filename = [self.zanata_data["location"]]
        output_filename.append(project_name)
        output_filename.append(locale)
        output_filename.append("poData.yml")
        path = os.path.join(*output_filename)
        try:
            poData["data"] = self.yaml_loader(path)
        except Exception as e:
            print(
                "PO data not found. \nPlease run 'python engine.py config -t' to download translation data."
            )
            poData["data"] = None

    def clean_poData(self, poData):
        ''' 
        This function does the final cleanup of poData.
        Cleanup like removing the variable texts.
        '''
        translation_status = {}
        contentCounter = 0
        translationCounter = 0
        translation_type = "POFile"
        if translation_type == "POFile":
            try:
                if isinstance(poData, dict):

                    for key in poData:
                        self.allPOData[key] = poData[key]
                        if self.modifiers_filter_for_po(key):
                            self.variablePOData[key] = self.modifiers_filter_for_po(
                                key, value=True
                            )
                        if poData[key]:
                            translationCounter += 1
                    contentCounter = len(poData)

            except Exception as e:
                print(e)
        elif translation_type == "JSON":
            for data in poData:
                try:
                    if isinstance(poData[data], dict):
                        keys = poData[data].keys()
                        if "content" in keys and "translation" in keys:
                            #                 print(poData[data])
                            self.allPOData[poData[data]["content"]] = poData[data][
                                "translation"
                            ]
                            if self.modifiers_filter_for_po(poData[data]["content"]):
                                self.variablePOData[
                                    poData[data]["content"]
                                ] = self.modifiers_filter_for_po(
                                    poData[data]["content"], value=True
                                )

                            translationCounter += 1
                        elif not "translation" in keys:
                            self.allPOData[poData[data]["content"]] = None
                        #                 print("translation missing.")
                        elif not "content" in keys:
                            print("content missing.")
                        #     break
                        if "content" in keys:
                            #         print("no Trabslation.")
                            contentCounter += 1
                except Exception as e:
                    print(e)
        translation_status["No Of Translation available"] = translationCounter
        translation_status["Total content found"] = contentCounter
        return translation_status

    def isInVariableData(self, englishUI):
        ''' Validator function to find the English data which contains variables. '''
        for data in self.variablePOData:
            listData = self.variablePOData[data]
            textData = data
            if all(
                [
                    True if d.strip() and d.strip() in englishUI else False
                    for d in listData
                ]
            ):
                print("Found the variable data ", textData)

    def generate_report(self, poData, localeUI, enUS):
        ''' Function to compare UI data and PO data and generate a report. '''
        translation_status = self.clean_poData(poData)
        report = {}
        for key in localeUI:
            print(len(localeUI[key].keys()))
            print(len(enUS[key].keys()))
            print(key)
            data = {}
            for xpath in enUS[key]:
                flag = False
                status = {}
                status["English UI"] = enUS[key][xpath]
                if xpath in localeUI[key]:
                    #             print(xpath+":"+enUS[key][xpath]+":"+localeUI[key][xpath])
                    status["Locale UI"] = localeUI[key][xpath]

                    if not re.match(status["English UI"], status["Locale UI"]):
                        continue

                    status["Flag"] = self.getFlag(
                        status["English UI"], status["Locale UI"]
                    )

                else:
                    #             print(xpath+":"+enUS[key][xpath])
                    status["Flag"] = self.getFlag(status["English UI"], None)

                data[xpath] = status
            report[key] = data
        report["translation_status"] = translation_status
        # print(report)
        return report

    # Below functions are not been used for now.

    def diffffff(self, str1, str2):
        count = 0
        str1 = str1.split(" ")

        for str in str1:  # scrapped text
            if str2.find(str) >= 0:  # find substring(scrapped) inside po
                count += 1
        if ((count / len(str1)) * 100) >= 60:
            return True
        else:
            return False

    def i18n_translation_stats(self):

        print("here")
        cutoff = 0.8

        self.not_i18n_dict = dict()
        po_list = list()
        po_dump = self.yaml_loader(self.manageiq_classic_ui_po_dump)
        text_dump = self.yaml_loader(self.lang_scrape_filepath)
        # po dump has dict data of all the locale so creating a list of required lang
        for key, data in po_dump.items():
            po_list.append(po_dump[key]["en"])

        # comparing the text strings to po list and check for correctness
        for key, data in text_dump.items():
            if key not in self.not_i18n_dict:
                self.not_i18n_dict[key] = list()
            for text in text_dump[key]:
                text = difflib.get_close_matches(data, po_list, cutoff=cutoff)
                if not text:
                    self.not_i18n_dict[key]["en"] = data

        self.yaml_dump("not_i18n_dict.yml", self.not_i18n_dict)

    def modifiers_filter_for_po(self, data, value=False):
        """ 
        This function will filter the modifier from msgstr and return po data
        value = True when you want to get the formated text.
        value = False if you just want if the text contains the variable.
        """

        if isinstance(data, str):
            # Replace #{}, _{}, %{} modifires from po string
            if "%{" in data:
                if value == True:
                    # work on data to return.
                    value = re.compile(r"\%\{[\w]*\}").split(data)
                    return value
                return True
            elif "#{" in data:
                if value == True:
                    value = re.compile(r"\#\{[\w]*\}").split(data)
                    return value
                return True

            elif "_{" in data:
                if value == True:
                    value = re.compile(r"\_\{[\w]*\}").split(data)
                    return value
                return True
        return False

    def detect_language(self, lang):
        """
        This module is used to check if the scraped text contains the given language
        :param lang: lang to pe checked
        :param scraped_text: list of text scraped from webpage
        :return:{"lang_detected_count": number of strings found for that locale,
                "total_string_count":scraped text count,
                "lang":lang}
        """

        # detect_count = 0
        # for text in scraped_text:
        #     if lang == langdetect.detect(text):
        #         detect_count += 1
        # return {"lang_detected_count":detect_count,
        #         "total_string_count":len(scraped_text),
        #         "lang":lang
        #         }
        try:
            # xpath to scrape entire text from webpage
            xpath = "//body//*[not(self::script) and not(self::noscript)]/text()"
            tree = self.tree_obj()
            text_list = tree.xpath(xpath)
            text_list = [x.strip() for x in text_list if x.strip()]
            # query to search the text_list in database for that locale
            db_result_list = list(
                self.db[self.base_config_dict["zanata_data"]["collection_name"]].find(
                    {lang: {"$in": text_list}}
                )
            )

            if len(db_result_list) > 2:
                print(
                    "yes page is transalted {} string found".format(len(db_result_list))
                )
                return True
            else:
                print(
                    "no corresponding transaltion found in TM please check it manually or update TM."
                )
                return False
        except Exception as e:
            print(e)