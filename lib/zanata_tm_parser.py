import sys
import os
import re
from xml.etree import ElementTree
from .mongo_database import MongoDatabase
import http.client
import yaml
import wget
import logging
import polib
import json
from datetime import datetime, timedelta
from requests import request
from .base_manager import UtilityMixin


class ZANATA_TM_PARSER(UtilityMixin):
    ''' This is a Zanata specefic module which downloads and pre-process the PO data. '''
    def __init__(self):
        self.base_config_dict = self.config_data
        self.log(self.base_config_dict["log_file"])
        self.locale = (self.base_config_dict["locale"]).split("-")[0]
        self.zanata_data = self.base_config_dict["zanata_data"]
        if not re.match(r"en", self.locale):
            getattr(self, "rest_run")()
        else:
            print("Specify your locale other then english in cammand using -l.")

    def log(self,log_file):
        FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(lineno)d:%(message)s"
        datestr = "%m/%d/%Y %I:%M:%S %p"
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(fmt=FORMAT,datefmt=datestr)
        file_handler = logging.FileHandler(filename=log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

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
        """
        Write the dict to yaml file
        :param filepath: file you want to save in
        :param data: json data
        :return: None
        """
        with open(filepath, "w") as obj:
            yaml.dump(data, obj, default_flow_style=False)

    def json_dump(self, filepath, data):
        """
        write the dict to json file
        :param filepath: file you want to save in
        :param data: json data
        :return: None
        """
        with open(filepath, "w") as fp:
            json.dump(data, fp)

    def rest_run(self):
        ''' Rest function to trigger the rest APIs. '''
        
        print("zanata rest call running :")
        function_call = getattr(self, "get_po_zanata_rest")
        function_call(self.locale)

    def get_po_zanata_rest(self, locale):
        ''' Get all po data form zatana '''

        first_project = self.zanata_data["projects"][0]
        project_name = first_project["projectSlug"].split("-")[0]
        output_filename = [self.zanata_data["location"]]
        output_filename.append(project_name)
        output_filename.append(locale)
        output_filename.append("poData.yml")
        path = os.path.join(*output_filename)

        timestamp = datetime.now()
        allData = {}
        allData["timestamp"] = timestamp.strftime("%d/%m/%Y")
        iterator = len(self.zanata_data["projects"])
        dump = 0
        project_counter = 0
        duplicate = []
        for project in self.zanata_data["projects"]:
            project_counter += 1
            print(project_counter)

            today = datetime.now()
            translation_type = "POFile"
            # translation_type="JSON"
            if iterator == 1:
                dump = 1
            if translation_type == "POFile":
                print("Getting PO Data.")
                project["locale"] = locale
                url = "https://translate.zanata.org/rest/file/translation/{projectSlug}/{iterationSlug}/{locale}/po?docId={documentSlug}".format(
                    **project
                )
                poData = self.rest_call_to_zanata(url, translation_type)
                if "network_error" in poData:
                    print("Zanata source not responding.")
                    continue

                self.isDirPresent(output_filename)
                if dump:
                    self.yaml_dump(path, poData)

            elif translation_type == "JSON":

                # To get POT data
                print("Getting POT.")
                url = "https://translate.zanata.org/rest/projects/p/{projectSlug}/iterations/i/{iterationSlug}/r/{documentSlug}".format(
                    **project
                )
                pot_data_dict = self.rest_call_to_zanata(url, translation_type)
                if "network_error" in pot_data_dict:
                    print("Zanata source not responding.")
                    continue
                potData = pot_data_dict["textFlows"]

                for data in potData:
                    if not data["id"] in allData:  # and data["content"]:
                        allData[data["id"]] = {}
                        # print(data["id"])
                        allData[data["id"]]["content"] = data["content"]
                    if not data["content"]:
                        print(data["id"])

                # To get translation data / PO data
                print("Getting PO.")
                project["locale"] = locale
                url = "https://translate.zanata.org/rest/projects/p/{projectSlug}/iterations/i/{iterationSlug}/r/{documentSlug}/translations/{locale}".format(
                    **project
                )
                po_data_dict = self.rest_call_to_zanata(url, translation_type)
                if "network_error" in po_data_dict:
                    print("Zanata source not responding.")
                    continue
                poData = po_data_dict["textFlowTargets"]

                for data in poData:
                    try:
                        if data["content"]:
                            # print(data["content"])
                            allData[data["resId"]]["translation"] = data["content"]
                    except:
                        print(data["resId"], data["content"])

                self.isDirPresent(output_filename)
                if dump:
                    self.yaml_dump(path, allData)
            iterator -= 1

        return True

    def isDirPresent(self, filepath):
        ''' Validating if the folder is present or not. '''

        for i in range(1, len(filepath)):
            if not os.path.exists(os.path.join(*filepath[:i])):
                print("directory not found but creating one")
                os.mkdir(os.path.join(*filepath[:i]))

    def modifiers_filter_for_po(self, data):
        ''' This function will filter the modifier from msgstr and return po data '''

        if isinstance(data, str):
            # Replace #{}, _{}, %{} modifires from po string
            if "%{" in data:
                data = re.sub(r"\%\{[\w]*\}", "", data)

            elif "#{" in data:
                data = re.sub(r"\#\{[\w]*\}", "", data)

            elif "_{" in data:
                data = re.sub(r"\_\{[\w]*\}", "", data)
        else:
            # data = yaml_loader(file_name)
            for po_key, po_id in data.items():
                for lang_key, lang_data in data[po_key].items():

                    # Replace #{}, _{}, %{} modifires from po string
                    if "%{" in data[po_key][lang_key]:
                        data[po_key][lang_key] = re.sub(
                            r"\%\{[\w]*\}", "", data[po_key][lang_key]
                        )

                    elif "#{" in data[po_key][lang_key]:
                        data[po_key][lang_key] = re.sub(
                            r"\#\{[\w]*\}", "", data[po_key][lang_key]
                        )

                    elif "_{" in data[po_key][lang_key]:
                        data[po_key][lang_key] = re.sub(
                            r"\_\{[\w]*\}", "", data[po_key][lang_key]
                        )
        return data

    def rest_call_to_zanata(self, url, translation_type):
        """
        This function will make a rest call to zanata api and get the .po/.pot files as provided
        Please follow template from ZanataDataLinks.txt for link details.
        """
        if translation_type == "POFile":
            try:
                file = wget.download(url)
                po = polib.pofile(file)
                os.remove(file)
                poData = {}
                for data in po:
                    poData[(data.msgid).strip()] = (data.msgstr).strip()
                    # print(data.msgid," :- ",data.msgstr)
                return poData

            except Exception as e:
                # print(e)
                return "network_error"

        elif translation_type == "JSON":
            try:
                response = request(
                    "GET", url, headers={"accept": "application/json"}, stream=True
                )
                if response.status_code == 200:
                    return json.loads(
                        response.text
                    )  # convert string to json and return
            except Exception as e:
                # print(e)
                return "network_error"

    def po_dump_generator(self, po_dict, locale=False):
        ''' This function will create a dict of all the .po found on zanata '''

        po_data_dict = dict()
        if not locale:
            for data in po_dict["textFlows"]:
                po_data_dict[data["id"]] = dict()
                po_data_dict[data["id"]]["en"] = data["content"]
        else:
            po_data_dict = self.yaml_loader("abc.yml")
            for data in po_dict["textFlowTargets"]:
                po_data_dict[data["resId"]][locale] = data["content"]

        self.yaml_dump("abc.yml", po_data_dict)

    def zanata_pull(self, data):
        """
        This module is to do rest api call to get tm xml data from zanata
        :param data: dict with
                    - username: zanata username
                    - authtoken: can get it from zanata
                    - project: list of project_name with project_branch
                    - storage_type: where to dump the file in json/yml
        :return:None
        """
        if isinstance(data, dict):
            dump_list = list()
            for item in data["project"]:
                print("started: " + item["project_name"])
                dump_dict = dict()

                # http call to zanata api
                conn = http.client.HTTPSConnection("translate.zanata.org")
                headers = {
                    "x-auth-user": data["user_name"],
                    "x-auth-token": data["auth_token"],
                }
                conn.request(
                    "GET",
                    "/rest/tm/projects/{}/iterations/{}".format(
                        item["project_name"], item["project_branch"]
                    ),
                    headers=headers,
                )
                res = conn.getresponse()
                response = res.read()
                if "namespace" not in data:
                    data["namespace"] = "{http://www.w3.org/XML/1998/namespace}"

                # parse the xml response
                tm_list = self.custom_xml_parser(
                    namespace=data["namespace"],
                    project_name=item["project_name"],
                    project_branch=item["project_branch"],
                    response=response,
                )
                # extend list of tm if multiple projects passed
                dump_list.extend(tm_list)

            # Depending on storage specified saving the TM content
            if "storage_type" in data:
                if data["storage_type"] == "yml":
                    self.yaml_dump(filepath="tm.yml", data=dump_list)
                elif data["storage_type"] == "mongodb":
                    if not data["collection_name"]:
                        print("collection name parameter missing")
                        sys.exit()
                    elif not data["database_name"]:
                        print("databse name parameter missing")
                        sys.exit()

                    try:
                        print("conneting to mongodb..")
                        # object creation for MongoDatabase class
                        mongo_obj = MongoDatabase(
                            tablename=data["collection_name"],
                            dbname=data["database_name"],
                        )
                        print("Inserting Translation Memory into mongodb..")
                        mongo_obj.insert_document(document=dump_list)
                    except Exception as e:
                        print(e)

                else:
                    print("invalid storage type")
            else:
                self.json_dump(filepath="tm.json", data=dump_list)

        else:
            print("error in input")

    def custom_xml_parser(self, namespace, project_name, project_branch, response=None):
        """
        This module is used to parse xml data a create the yml data dump out of it
        :param namespace: default xml namespace
        :param response: the zanata api xml response
        :return: list of tm for specific project
        """
        if response:
            root = ElementTree.fromstring(response.decode("utf-8"))
            tu_obj_list = root.getchildren()[1].getchildren()
            # iterate through all tu elements
            dump_list = list()
            for tu in tu_obj_list:
                tuid = (tu.get("tuid")).split(":")
                tuv_obj_list = tu.getchildren()
                # iterate through all tuv elements
                dump_data = dict()
                dump_data["project_name"] = project_name
                dump_data["project_branch"] = project_branch
                dump_data["path"] = tuid[2]
                # dump_data["translations"] = dict()
                for tuv in tuv_obj_list:
                    tuv_lang = tuv.get(namespace + "lang")
                    seg = tuv.findtext("seg")
                    dump_data[tuv_lang] = seg

                dump_list.append(dump_data)

            return dump_list
        else:
            print("response error plz check")