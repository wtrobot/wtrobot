from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from io import StringIO
import lxml.etree
import time
import os
import yaml
import copy
import pojson
import polib
import hashlib
from datetime import datetime
import requests
import re

class WTRobot():

    def __init__(self, driver):
        self.driver = driver
        self.tree = self.tree_obj()
        self.nav_dims = {"home": [10, 20, 30, 20], "navbar": [10, 20, 30, 1]}
        self.WTScript = dict()
        self.lang_scrape_filepath = "lang_scrape.yml"
        self.wtscript_filepath = "wtscript.yml"
        self.script_filepath = "script.yml"  # intermediate script generated
        self.script = None  # script from script.yml
        self.script_file_obj = None

    def random_hash_generator(self):
        '''
        This function will generate a random md5 hash on current date timestamp
        :return: md5 hash
        '''
        return hashlib.md5(str(datetime.now()).encode()).hexdigest()

    # Get all elements in the given dimension
    def get_all_nav(self, dimension):
        xpath = "//body//*[not(self::script)]/text()"
        tree = self.tree_obj()

        # Will get list of text found
        fields = tree.xpath(xpath)
        fields = [x.strip() for x in fields if x.strip()]
        path_list = list()

        if not fields:
            return False

        for field in fields:
            # find that string in dom
            obj_path = tree.xpath("//body//*[contains(text(),'"+field+"')]")
            # get entire dom path
            elem_abs_path = tree.getpath(obj_path[0])
            if self.check_element_location(dimension, elem_abs_path):
                path_list.append(elem_abs_path)
        return path_list

    # Function will check if the given element exist in the given dimension
    def check_element_location(self, dimensions, element):
        element_obj = None
        if isinstance(element, str):
            element_obj = self.driver.find_element_by_xpath(element)
            if element_obj.is_displayed():
                txt_location = element_obj.location
                if (txt_location['x'] >= dimensions[0] and txt_location['y'] >= dimensions[1] and txt_location['x'] <= dimensions[2] and txt_location['y'] <= dimensions[3]):
                    return True
                else:
                    return False
        elif isinstance(element, dict):
            if (element['x'] >= dimensions[0] and element['y'] >= dimensions[1] and element['x'] <= dimensions[2] and element['y'] <= dimensions[3]):
                return True
            else:
                return False
        else:
            return False

    # Create a lxml tree object and return
    def tree_obj(self):
        parser = lxml.etree.HTMLParser()
        html_source = self.driver.page_source
        return lxml.etree.parse(StringIO(html_source), parser)

    # Read yaml file and return the dict
    def yaml_loader(self, filepath):
        data = dict()
        if os.path.isfile(filepath):
            with open(filepath, "r") as obj:
                data = yaml.load(obj)
            if not data:
                return dict()
        return data

    # Write the dict to yaml file
    def yaml_dump(self, filepath, data):
        with open(filepath, "w") as obj:
            yaml.dump(data, obj, default_flow_style=False)

    # Get absolute path of an given element
    # def get_element_abs_path(self, text):
    #     tree = self.tree_obj()
    #     # xpath = "//body//*[not(self::script)]//*[contains(text(),'"+text+"')]"
    #     xpath = "//body//*[not(self::script)]//*[text()='"+text+"']"
    #     elem_path = tree.xpath(xpath)
    #     for i in range(len(elem_path)):
    #         if(i == 0):
    #             return tree.getpath(elem_path[i])

    def get_element_abs_path(self, xpath=False, text=False, elements=False):
        '''
        Get absolute path for the provided text as an input
        :param text:
        :return: path if found else False
        '''

        tree = self.tree_obj()
        if not xpath and text:
            xpath = "//body//*[not(self::script) and not(self::noscript)]//*[contains(.,text())]"

            elem_path = tree.xpath(xpath)
            for i in range(len(elem_path)):
                # will return the abs path but parent paths aswell
                path = tree.getpath(elem_path[i])
                # Now to check the valid with the text get this xpath value
                abs_path = tree.xpath(path + "/text()")
                abs_path = [x.strip() for x in abs_path if x.strip()]
                # If the absolute path if found and the text is equal to the provided text
                if (len(abs_path) > 0) and (text == abs_path[0]):
                    return path

        elif xpath and not text:
            elem_path = tree.xpath(xpath)
            elem_path_list = list()
            if xpath.endswith('text()') and elements:
                return elem_path
            elif xpath.endswith('text()') and not elements:
                return elem_path[0]
            elif elements:
                for elem in elem_path:
                    elem_path_list.append(tree.getpath(elem))
                return elem_path_list
            else:
                return tree.getpath(elem_path[0])
        else:
            return False
        return False


    def CHOOSE(self, test_case_no, cmd_list):
        print("no defination yet")

    # This function which will create a WTScript with absoulte
    def create_script(self, test_case_no, cmd_list):
        try:
            if cmd_list not in self.WTScript[test_case_no]:
                self.WTScript[test_case_no].append("  ".join(cmd_list))
        except Exception as e:
            print(e)

    # This function will visit the URL specified
    def GOTO(self, test_case_no, cmd_list):
        try:
            self.driver.get(cmd_list[1])
            if self.language == "en":
                self.create_script(test_case_no, cmd_list)
        except Exception as e:
            print(e)

    # This function will click the element specified
    def CLICK(self, test_case_no, cmd_list):

        if "//" in cmd_list[1]:
            self.get_element(cmd_list[1]).click()
            self.create_script(test_case_no, cmd_list)
        else:
            try:
                if "/html/body" not in cmd_list[1]:
                    element_obj = self.get_element_abs_path(text=cmd_list[1])
                    if self.driver.find_element_by_xpath(element_obj).text == cmd_list[1]:
                        cmd_list[1] = element_obj
                        self.create_script(test_case_no, cmd_list)
                        element = self.get_element(element_obj)
                        element.click()
                        return True
                elif "/html/body" in cmd_list[1]:
                    self.get_element(cmd_list[1]).click()

                else:
                    print("error")
                    return False

            except Exception as e:
                print(e)


    # This function will emulate the radio button selection
    def RADIO_CHECKBOX(self, test_case_no, cmd_list):
        try:
            type = None
            xpath = None
            if cmd_list[0].upper() == "SELECT":
                type = "radio"
            elif cmd_list[0].upper() == "CHECK":
                type = "checkbox"

            if not ("/html/body/" in cmd_list[2]) or ("/html/body/" in cmd_list[1]):
                element_obj = self.get_element_abs_path(text=cmd_list[2])

                # // *[contains(text(), "Female")] / preceding::input[ @ type = "radio"][1]
                if "BEFORE" in cmd_list:
                    xpath = element_obj + "/preceding::input[@type='"+type+"'][1]"
                else:
                    xpath = element_obj + "/following::input[@type='"+type+"'][1]"

                cmd_list[2] = xpath
                self.create_script(test_case_no, cmd_list)

                input_obj = self.get_element(xpath)

                if "IN" in cmd_list:
                    if self.check_element_location(self.nav_dims[cmd_list[cmd_list.index("IN") + 1]], input_obj.location):
                        input_obj.click()
                else:
                    input_obj.click()

            elif ("/html/body/" in cmd_list[2]) or ("/html/body/" in cmd_list[1]):
                self.get_element(cmd_list[2]).click()

            else:
                return False
        except Exception as e:
            print(e)

    # This function will wait until the element is ready
    def element_ready(self, locator):
        # logging.info("Waiting for element ready")
        try:
            return WebDriverWait(self.driver, 300).until(EC.presence_of_element_located((By.XPATH, locator)))
        except Exception as e:
            print(e)

    # This function will wait until the element is visible
    def WAIT_UNTIL(self, test_case_no, cmd_list):
        try:
            elem = None
            element_obj = None
            if "/html/body" not in cmd_list[1]:
                elem = self.get_element("//body//*[contains(text(),'" + cmd_list[1] + "')]")
                element_obj = self.get_element_abs_path(text=cmd_list[1])
            elif "/html/body" in cmd_list[1]:
                elem = self.get_element(cmd_list[1])
                element_obj = cmd_list[1]
            else:
                return False

            if elem:
                cmd_list[1] = element_obj
                if self.language == "en":
                    self.create_script(test_case_no, cmd_list)
            else:
                print("element not found..")
        except Exception as e:
            print(e)

    # This function will emulate the mouse hover action
    def HOVER(self, test_case_no, cmd_list):
        try:
            # input_obj = None
            if "/html/body" not in cmd_list[2]:
                element = self.get_element_abs_path(text=cmd_list[2])
                cmd_list[2] = element
                self.create_script(test_case_no, cmd_list)

            element_obj = self.get_element(cmd_list[2])
            ActionChains(self.driver).move_to_element(element_obj).perform()
            time.sleep(2)
        except Exception as e:
            print(e)

    # This function will be used to input data inside <input> tag
    def INPUT(self, test_case_no, cmd_list):
        try:
            input_obj = None
            if "/html/body" not in cmd_list[1]:
                element_obj = self.get_element_abs_path(text=cmd_list[1])
                xpath = element_obj + "/following::input[1]"
                input_obj = self.get_element(xpath)
                cmd_list[cmd_list.index("INPUT")+1] = xpath
                self.create_script(test_case_no, cmd_list)

            elif "/html/body" in cmd_list[1]:
                input_obj = self.get_element(cmd_list[cmd_list.index("INPUT")+1])
            else:
                return

            if "IN" in cmd_list:
                if self.check_element_location(self.nav_dims[cmd_list[cmd_list.index("IN")+1]], input_obj.location):
                    input_obj.send_keys(cmd_list[cmd_list.index("AS")+1])
            else:
                input_obj.send_keys(cmd_list[cmd_list.index("AS") + 1])
        except Exception as e:
            print(e)

    # def TEST_EXIT(self):
    #     try:
    #         self.yaml_dump(self.wtscript_filepath, self.WTScript)
    #     except Exception as e:
    #         print(e)

    # This function will return the element object on screen
    def get_element(self, locator):
        try:
            return WebDriverWait(self.driver,1000).until(EC.presence_of_element_located((By.XPATH, locator)))
        except Exception as e:
            print(e)

    # # This module will scrape the entire text from single page and make a .yml to record the text and return the list of text scrapped
    # def i18n_get_all_text(self, lang="en-US"):
    #     try:
    #         # xpath to scrape entire text from webpage
    #         xpath = "//body//*[not(self::script)]/text()"
    #
    #         # yml file which will have all the text scrapped from web
    #         fname = "lang_scrape.yml"
    #         lang_scrape = self.yaml_loader(fname)
    #         tree = self.tree_obj()
    #         fields = tree.xpath(xpath)
    #         fields = [x.strip() for x in fields if x.strip()]
    #         new_data = {lang: fields}
    #         if not str(driver.current_url) in lang_scrape:
    #             lang_scrape[str(driver.current_url)] = list()
    #         if new_data not in lang_scrape[str(driver.current_url)]:
    #             lang_scrape[str(driver.current_url)].append(new_data)
    #         self.yaml_dump(fname, lang_scrape)
    #         return fields
    #     except Exception as e:
    #         print(e)

    # This module will convert po to json/list according to type specified
    def po_to_json(self, po_filename, type):
        try:
            po_file_path = polib.pofile(po_filename)
            po_dict = pojson.po2dict(po_file_path)
            if type.lower() == "list":
                po_list = list()
                for key, val in po_dict.items():
                    # [None,"unicode"] return the first non None string
                    po_list.append(next(item for item in val if item is not None))
                return po_list
            else:
                return po_dict
        except Exception as e:
            print(e)

    # # This method will compare the webpage text with .po file and return the list of text which are untranslated or not found in .po file
    # def translation_check(self, text_list, po_data):
    #     try:
    #         not_i18n_list = list()
    #         # if you have po_list
    #         if isinstance(po_data, list):
    #             for text in text_list:
    #                 if text not in po_data:
    #                     not_i18n_list.append(text)
    #         # if you have po_dict then the logic goes here
    #         elif isinstance(po_data, dict):
    #             pass
    #         return not_i18n_list
    #     except Exception as e:
    #         print(e)

    # This module will be used to parse the cmd provided via script
    def wtscript(self, msg_string):
        try:
            if msg_string.upper() == "START":
                self.script = dict()
            elif msg_string.upper() == "STOP":
                # print(self.script)
                self.yaml_dump(self.script_filepath, self.script)
                self.command_parser(self.script_filepath)
            else:
                test_case = msg_string.split("  ")
                if "TESTCASE" in msg_string.upper():
                    if len(test_case) == 2:
                        if not test_case[1] in self.script:
                            self.script[test_case[1]] = list()
                            self.current_test_case = test_case[1]
                    else:
                        # self.script[self.current_test_case].extend(self.script[msg_string])
                        self.script[self.current_test_case].append(msg_string)
                else:
                    self.script[self.current_test_case].append(msg_string)
        except Exception as e:
            print(e)

    # This module will parse the entire script and execute it one by one
    def command_parser(self, filename, language="en"):
        try:
            self.language = language
            self.script_dict = self.yaml_loader(filename)
            full_script = dict()
            temp_script = copy.deepcopy(self.script_dict)

            if language == "en":
                for key, script in temp_script.items():
                    full_script[key] = self.cmd_substitution_stack(script)
            else:
                full_script = self.script_dict

            # print(full_script)

            script_keys = [i for i in full_script.keys()]

            # This logic will check for sequence list and if fails then get keys to iterate through the script
            if "SEQUENCE" in script_keys:
                script_keys = full_script["SEQUENCE"]
                # checking if that testcase exist in testcase
                for script in script_keys:
                    if script not in full_script:
                        print("invalid testcase/module : "+script)
                        script_keys.remove(script)

                self.WTScript["SEQUENCE"] = list(full_script["SEQUENCE"])
            else:
                if "SEQUENCE" in script_keys:
                    script_keys.remove("SEQUENCE")

            for key in script_keys:  # Access all the testcase as per the key sequence
                test_case_no = key
                for cmd_str in full_script[key]:  # Access the list for single testcase
                    cmd_list = cmd_str.split("  ")

                    if (test_case_no not in self.WTScript) and (language == "en"):
                        self.WTScript[test_case_no] = list()

                    if cmd_list[0].upper() == "GOTO":
                        self.GOTO(test_case_no, cmd_list)

                    elif cmd_list[0].upper() == "CHECK":
                        if cmd_list[1].upper() == "LINK":
                            self.check_broken_links(test_case_no, cmd_list)
                        elif cmd_list[1].upper() == "TITLE":
                            self.check_title(cmd_list[2])

                        else:
                            self.CHECK(test_case_no,cmd_list)

                    elif cmd_list[0].upper() == "CLICK":
                        self.CLICK(test_case_no, cmd_list)

                    elif cmd_list[0].upper() == "INPUT":
                        self.INPUT(test_case_no, cmd_list)

                    elif cmd_list[0].upper() == "CHOOSE":
                        self.CHOOSE(test_case_no, cmd_list)

                    elif (cmd_list[0].upper() == "SELECT" or cmd_list[0].upper() == "CHECK"):
                        self.RADIO_CHECKBOX(test_case_no, cmd_list)

                    elif cmd_list[0].upper() == "WAIT":
                        self.WAIT_UNTIL(test_case_no, cmd_list)

                    elif cmd_list[0].upper() == "HOVER":
                        self.HOVER(test_case_no, cmd_list)

                    elif cmd_list[0].upper() == "FUNCTION":  # This block will call custom function
                        fun_call = getattr(self, cmd_list[1])(*cmd_list[2:])
                        print(fun_call)
                        if not fun_call:
                            print("Function "+cmd_list[1]+" failed to execute.")
                    else:
                        print("Invalid command passed...")

                print("excuted : "+test_case_no)

            if self.language == "en":
                self.yaml_dump(self.wtscript_filepath, self.WTScript)
        except Exception as e:
            print(e)


    # Assert function
    def CHECK(self, test_case_no, cmd_list):
        s = "Houston we've got a problem"
        self.assertTrue(self.get_element(cmd_list[1]))

    # This function will reslove the recursive testcase call and return single script
    def cmd_substitution_stack(self, script):
        try:
            new_script = list()
            visited = list()
            script.reverse()
            while len(script) != 0:
                cmd_str = script.pop()
                if "IMPORT" in cmd_str.upper():
                    cmd_list = cmd_str.split("  ")
                    if not cmd_list[1] in visited:
                        visited.append(cmd_list[1])
                        sub_script = copy.deepcopy(self.script_dict[cmd_list[1]])
                        sub_script.reverse()
                        script.extend(sub_script)
                else:
                    new_script.append(cmd_str)
            return new_script
        except Exception as e:
            print(e)

    def clickCoordinates(self,co_ordinates,canvas=None):

        '''
        This function will click on the cordinates given
        :param coordinates: {'x':1,'y':2} or (1,2) or [1,2] or [(0,1)]  co-ordinates
        :return: false if not valid input else true
        '''
        #coordinates = (795,437)
        #self.driver.execute_script('document.elementFromPoint(884,495).click();')

        # tue  928 82

        # self.fullpageSnapshot()
        # action = ActionChains(self.driver)
        # action.move_by_offset(938,106)
        # action.click()
        # action.perform()

        #self.driver.execute_script('document.elementFromPoint(795,437).click();')

        if canvas:
            # canvas = self.driver.find_element_by_id("noVNC_canvas")
            # print("-------------------")
            # print(canvas.location)
            # print(canvas.size)
            # print("-------------------")
            action = ActionChains(self.driver)
            action.move_by_offset(co_ordinates[0],co_ordinates[1])
            action.click(canvas)
            action.release()
            action.perform()
            time.sleep(2)
        else:
            action = ActionChains(self.driver)
            action.move_by_offset(co_ordinates[0],co_ordinates[1])
            action.click()
            action.perform()

        return True

    def fullpageSnapshot(self, filename=time.time()):
        from PIL import Image, ImageEnhance, ImageChops
        '''
        This function will take entire screenshot.
        :param filename: file to save screenshot image (optional)
        :return: fullpage screenshot image object and image name
        '''

        try:
            self.filepath = "/home/vishal/PycharmProjects/WTRobot-01/"
            self.filetype = ".png"
            FQ_filename = self.filepath + str(filename) + self.filetype
            self.driver.get_screenshot_as_file(FQ_filename)
            image = Image.open(FQ_filename)  # open that image
            return {"image_object": image, "image_name": FQ_filename}

        except Exception as e:
            print(e)

    def check_broken_links(self, test_case_no, cmd_list):
        '''
        This function is used to check if the given link is broken or not.It simply makes a http call and checks response
        :param url: link which you want to check
        :return: True if response is 200 else False
        '''

        try:
            url = cmd_list[2]
            if not re.match(r'^www|http',url):
                link_abs_path = self.get_element_abs_path(text=url)
                url = self.driver.find_element_by_xpath(link_abs_path).get_attribute("href")

                cmd_list[2] = url
                self.create_script(test_case_no, cmd_list)

            print("visiting : "+url)
            request = requests.get(url,verify=False)
            if request.status_code == 200:
                print('Web site exists')
                return True
            else:
                print('Web site does not exist')
                return False
        except Exception as e:
            print(e)
            return False

    def check_title(self, test_case_no, title_text):

        # url = self.driver.find_element_by_xpath(link_abs_path).get_attribute("href")
        # link_abs_path = self.get_element_abs_path(url)
        page_title = self.get_element_abs_path(xpath="//head/title/text()")
        if page_title == title_text:
            print("title match")
            return True
        else:
            print("title not match")
            return False


if __name__ == "__main__":

    options = webdriver.ChromeOptions()
    options.add_argument("–lang=ja")
    driver = webdriver.Chrome(chrome_options=options)
    
    driver.get("https://www.youtube.com")
    driver.maximize_window()

    obj = WTRobot(driver)
    obj.command_parser("script.yml")

    time.sleep(10)
    driver.close()
