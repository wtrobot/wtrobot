import ast
import copy
import logging
import os
import re
import time
from datetime import datetime
from io import StringIO
import lxml.etree
import requests
import yaml
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .I18N_TEST import I18N_TEST
from .base_manager import UtilityMixin
from .image_processing import Image_Processing

class WTRobot(Image_Processing, I18N_TEST, UtilityMixin):
    '''
        Core module of the project.
        It is used to parse the yaml script and map it to its specefic functions.
    '''

    def __init__(self, driver):
        ''' 
            Basic functions and variables are initialized. I18N object is very important. 
        '''
        self.base_config_dict = self.config_data
        self.log(self.base_config_dict["log_file"])
        self.driver = driver
        self.tree = self.tree_obj()
        self.WTScript = dict()
        self.script = None  # script from script.yml

        self.script_file_obj = None
        self.take_screenshot = True

        self.i18n_obj = I18N_TEST(driver=driver)

    def log(self,log_file):
        FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(lineno)d:%(message)s"
        datestr = "%m/%d/%Y %I:%M:%S %p"
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(fmt=FORMAT,datefmt=datestr)
        file_handler = logging.FileHandler(filename=log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def date_generator(self):
        """
        This function will return current date timestamp
        :return: datetime string.
        """
        return str(datetime.now())

    def get_all_nav(self, dimension):
        '''
            Get all elements in the given dimension.
            Status: This function is not in use right now.
        '''
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
            obj_path = tree.xpath("//body//*[contains(text(),'" + field + "')]")
            # get entire dom path
            elem_abs_path = tree.getpath(obj_path[0])
            if self.check_element_location(dimension, elem_abs_path):
                path_list.append(elem_abs_path)
        return path_list

    def check_element_location(self, dimensions, element):
        '''
            Function will check if the given element exist in the given dimension
            Status: Its dependent functions are not been used right now.
                    Also duplicate to isValidElement function.
        '''
        element_obj = None
        if isinstance(element, str):
            element_obj = self.driver.find_element_by_xpath(element)
            if element_obj.is_displayed():
                txt_location = element_obj.location
                if (
                    txt_location["x"] >= dimensions[0]
                    and txt_location["y"] >= dimensions[1]
                    and txt_location["x"] <= dimensions[2]
                    and txt_location["y"] <= dimensions[3]
                ):
                    return True
                else:
                    return False
        elif isinstance(element, dict):
            if (
                element["x"] >= dimensions[0]
                and element["y"] >= dimensions[1]
                and element["x"] <= dimensions[2]
                and element["y"] <= dimensions[3]
            ):
                return True
            else:
                return False
        else:
            return False

    def getRegion(self, regionName, points=False, xpath=False):
        '''
        Get region from XPaths provided in config.json file.
        It provides 4 values about the region.
            1) X co-ordinate
            2) Y co-ordinate
            3) width
            4) Height
        '''

        regions = {}
        try:
            menu_region = self.base_config_dict["menu_region"]
            workspace_region = self.base_config_dict["workspace_region"]
            settings_region = self.base_config_dict["settings_region"]
        except Exception as e:
            self.logger.exception("Make sure the region xpaths are updated in config.json.")
            exit()

        menu = self.driver.find_element_by_xpath(menu_region)
        regions["menu_region"] = menu.rect
        workspace = self.driver.find_element_by_xpath(workspace_region)
        regions["workspace_region"] = workspace.rect
        settings = self.driver.find_element_by_xpath(settings_region)
        regions["settings_region"] = settings.rect

        if regionName not in regions:
            raise Exception("region not found")
        region = regions[regionName]
        if points:
            coordinates = {}
            coordinates["start"] = {"x": region["x"], "y": region["y"]}
            coordinates["end"] = {
                "x": region["x"] + region["width"],
                "y": region["y"] + region["height"],
            }
            coordinates["width"] = region["width"]
            coordinates["height"] = region["height"]
            return coordinates
        elif xpath:
            # print('pass')
            return self.base_config_dict[regionName]

    # Validation of the element if it is present in specefied region and also is it clickable.
    def isValidElement(self, elementPath, regionPoints, regionName, searchText=False):

        # For region approach.
        elementLocation = self.driver.find_element_by_xpath(elementPath)
        elementPoint = elementLocation.rect
        elementPoint = {"x": elementPoint["x"], "y": elementPoint["y"]}

        # For parent child approach.
        regionXpath = self.getRegion(regionName, xpath=True)

        if (
            elementPoint["x"] >= regionPoints["start"]["x"]
            and elementPoint["y"] >= regionPoints["start"]["y"]
            and elementPoint["x"] <= regionPoints["end"]["x"]
            and elementPoint["y"] <= regionPoints["end"]["y"]
        ):
            self.logger.info(elementPoint)
            try:
                if WebDriverWait(self.driver, 0.5).until(
                    EC.element_to_be_clickable((By.XPATH, elementPath))
                ):
                    self.logger.info("point approach")
                    return True
            except WebDriverException:
                self.logger.exception("WebDriverException")
            except Exception as e:
                self.logger.exception(e)
                return False

        elif regionXpath in elementPath:
            try:
                if WebDriverWait(self.driver, 0.5).until(
                    EC.element_to_be_clickable((By.XPATH, elementPath))
                ):
                    self.logger.info("xpath approach")
                    return True
            except WebDriverException:
                self.logger.exception("WebDriverException")
            except Exception as e:
                self.logger.exception(e)
                return False
        else:
            return False

    def tree_obj(self):
        ''' Create a lxml tree object and return '''
        parser = lxml.etree.HTMLParser()
        html_source = self.driver.page_source
        return lxml.etree.parse(StringIO(html_source), parser)

    def yaml_loader(self, filepath):
        ''' Read yaml file and return the dict '''
        data = dict()
        if os.path.isfile(filepath):
            with open(filepath, "r") as obj:
                data = yaml.load(obj)
            if not data:
                return dict()
        return data

    def yaml_dump(self, filepath, data):
        ''' Write the dict to yaml file '''
        with open(filepath, "w") as obj:
            yaml.dump(data, obj, default_flow_style=False)

    def get_element_abs_path(self, xpath=False, text=False, elements=False, flag=False):
        """
        Get absolute path for the provided text as an input
        :param text:
        :return: path if found else False
        """

        tree = self.tree_obj()
        if not xpath and text:
            xpath = "//body//*[not(self::script) and not(self::noscript)]//*[contains(.,text())]"
            allFoundXpaths = []
            elem_path = tree.xpath(xpath)
            for i in range(len(elem_path)):
                path = tree.getpath(
                    elem_path[i]
                )  # will return the abs path but parent paths aswell
                abs_path = tree.xpath(
                    path + "/text()"
                )  # Now to check the valid with the text get this xpath value
                abs_path = [x.strip() for x in abs_path if x.strip()]
                # If the absolute path is found and the text is equal to the provided text
                if (len(abs_path) > 0) and (text == abs_path[0]):
                    self.logger.info(path)
                    allFoundXpaths.append(path)
            if len(allFoundXpaths)>1:
                message = "{} text found {} times on page. ".format(text,len(allFoundXpaths))
                self.logger.warning(message)
            if flag:
                return allFoundXpaths
            else:
                return allFoundXpaths[0]

        elif xpath and not text:
            elem_path = tree.xpath(xpath)
            elem_path_list = list()
            if xpath.endswith("text()") and elements:
                return elem_path
            elif xpath.endswith("text()") and not elements:
                return elem_path[0]
            elif elements:
                for elem in elem_path:
                    elem_path_list.append(tree.getpath(elem))
                return elem_path_list
            else:
                return tree.getpath(elem_path[0])
        return False

    def CHOOSE(self, test_case_no, cmd_list):
        self.logger.error("CHOOSE have no defination yet")

    def create_script(self, test_case_no, cmd_list):
        """
        This function which will create a WTScript with absoulte path.
        :param test_case_no:
        :param cmd_list:
        :return: None
        """
        try:
            if cmd_list not in self.WTScript[test_case_no]:
                self.WTScript[test_case_no].append("  ".join(cmd_list))
        except Exception as e:
            self.logger.exception(e)

    def GOTO(self, test_case_no, cmd_list):
        """
        This function will visit the URL specified
        :param test_case_no:
        :param cmd_list:
        :return: None
        """
        try:
            self.driver.get(cmd_list[1])
            if self.base_config_dict["locale"] == "en-US":
                self.create_script(test_case_no, cmd_list)
        except Exception as e:
            print("Error in GOTO, please refer log file for details.")
            self.logger.exception(e)

    def web_coordinates_click(self, xaxis, yaxis):
        """
        Click x,y co-ordinates on browser
        :param xaxis:
        :param yaxis:
        :return: None
        """
        try:
            action = webdriver.ActionChains(self.driver)
            action.move_by_offset(float(xaxis), float(yaxis))
            action.click()
            action.perform()
        except Exception as e:
            print("internal error, cannot click")
            self.logger.exception(e)

    def ALERT(self, test_case_no, cmd_list):
        """
        Alert based login system and accept or decline.
        :param test_case_no:
        :param cmd_list:
        :return: True/False
        """
        alert = self.driver.switch_to.alert
        self.logger.info("Alert selected.")

        if cmd_list[-1] == "accept":
            if len(cmd_list)>2:
                alert.send_keys(keysToSend="\ue004".join(cmd_list[1:-1]))
            alert.accept()
            print("alert accepted.")
            self.logger.info("alert accepted.")
        elif cmd_list[-1] == "deny":
            if len(cmd_list)>2:
                alert.send_keys(keysToSend="\ue004".join(cmd_list[1:-1]))
            alert.dismiss()
            print("alert denied.")
            self.logger.info("alert denied.")
        else:
            print("Alert syntex not supported.")
            self.logger.error("Alert syntex not supported.")
            return False
        if self.base_config_dict["locale"] == "en-US":
            self.create_script(test_case_no, cmd_list)
            self.logger.debug(self.WTScript)
        return True

    def CLICK(self, test_case_no, cmd_list, regionPoints={}, regionName=False):
        """
        This function will click the element specified
        :param test_case_no:
        :param cmd_list:
        :return: True/False
        """

        # If region is specefied.
        if "region" in cmd_list[-1].split("=")[0] or regionPoints:
            try:
                if regionPoints:
                    pass
                elif cmd_list[-1].split("=")[1]:
                    regionName = cmd_list[-1].split("=")[1]
                    regionPoints = self.getRegion(regionName, points=True)
                    self.logger.info("your region is in :- {}".format(regionPoints))

                else:
                    raise Exception("Region name not specefied.")

                if "/html/body" not in cmd_list[1]:
                    element_objs = self.get_element_abs_path(
                        text=cmd_list[1], flag=True
                    )
                
                    self.logger.info(element_objs)

                    # Business logic for validating region
                    validElements = [
                        element
                        for element in element_objs
                        if self.isValidElement(
                            element, regionPoints, regionName, searchText=cmd_list[1]
                        )
                    ]

                    if len(validElements)>1:
                        message = "{} text found {} valid times in specefied region. ".format(cmd_list[1],len(validElements))
                        print(message)
                        self.logger.warning(message)

                    if (
                        len(validElements) == 1
                        and self.driver.find_element_by_xpath(validElements[0]).text
                        == cmd_list[1]
                    ):
                        cmd_list[1] = validElements[0]
                        self.create_script(test_case_no, cmd_list[:2])
                        element = self.get_element(validElements[0])
                        element.click()
                        time.sleep(1)
                        return True
                    else:
                        print("Please use XPATH for {} keyword.".format(cmd_list[1]))
                        self.logger.error("Please use XPATH for {} keyword.".format(cmd_list[1]))
                        return False
                else:
                    print("You have specefied xpath with region.")
                    self.logger.error("You have specefied xpath with region.")
                    return False

            except Exception as e:
                self.logger.exception(e)

        # if input param is image
        elif len(cmd_list) == 3 and cmd_list[1].upper() == "IMAGE":
            try:
                # check if param has file path
                if re.match(r".*(\.jpg|\.png)", cmd_list[2]):
                    if not os.path.isfile(cmd_list[2]):  # check if file exist
                        return False
                    else:
                        image_coordinates = self.image_coordinates(
                            image_path=self.fullpageSnapshot(),
                            subimage_path=cmd_list[2],
                        )
                        self.web_coordinates_click(
                            xaxis=image_coordinates["x"], yaxis=image_coordinates["y"]
                        )
                        cmd_list[2] = "{},{}".format(
                            image_coordinates["x"], image_coordinates["y"]
                        )
                        self.create_script(test_case_no, cmd_list)
                        return True
                # click cordinates from wtscripts
                else:
                    image_coordinates = cmd_list[2].split(",")
                    self.web_coordinates_click(
                        image_coordinates[0], image_coordinates[1]
                    )
                    return True
            except Exception as e:
                self.logger.exception("Error in image click module")
                print("Error in image click module")
                self.test_case_fail = True

        # if xpath is given as param
        elif "//" in cmd_list[1]:
            try:
                self.get_element(cmd_list[1]).click()
                self.create_script(test_case_no, cmd_list)
                return True
            except Exception as e:
                self.logger.exception("element: {}  not found".format(cmd_list[1]))
                self.test_case_fail = True

        # if absolute path is given as input param or even the keyword
        else:
            try:
                # This condition handles the text input from user without any region.
                if "/html/body" not in cmd_list[1]:
                    element_obj = self.get_element_abs_path(text=cmd_list[1])
                    self.logger.info("{}:{}".format(cmd_list[1],element_obj))
                    if (
                        self.driver.find_element_by_xpath(element_obj).text
                        == cmd_list[1]
                    ):
                        cmd_list[1] = element_obj
                        self.create_script(test_case_no, cmd_list)
                        element = self.get_element(element_obj)
                        element.click()
                        return True
                elif "/html/body" in cmd_list[1]:
                    self.get_element(cmd_list[1]).click()
                    return True
                else:
                    print("Unsupported text passed.")
                    self.logger.error("Unsupported text passed.")
                    return False

            except Exception as e:
                self.logger.exception(e)

    def RADIO_CHECKBOX(self, test_case_no, cmd_list):
        ''' This function will emulate the radio button selection '''
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
                    xpath = element_obj + "/preceding::input[@type='" + type + "'][1]"
                else:
                    xpath = element_obj + "/following::input[@type='" + type + "'][1]"

                cmd_list[2] = xpath
                self.create_script(test_case_no, cmd_list)

                input_obj = self.get_element(xpath)

                # if "IN" in cmd_list:
                #     if self.check_element_location(self.nav_dims[cmd_list[cmd_list.index("IN") + 1]], input_obj.location):
                #         input_obj.click()

                input_obj.click()
                return True
            elif ("/html/body/" in cmd_list[2]) or ("/html/body/" in cmd_list[1]):
                self.get_element(cmd_list[2]).click()
                return True
            else:
                return False
        except Exception as e:
            self.logger.exception("element: {}  not found".format(cmd_list[1]))
            self.test_case_fail = True
            return False

    def element_ready(self, locator):
        ''' This function will wait until the element is ready '''
        self.logger.info("Waiting for element ready")
        try:
            return WebDriverWait(self.driver, 900).until(
                EC.presence_of_element_located((By.XPATH, locator))
            )
        except Exception as e:
            self.logger.exception(e)

    def WAIT_UNTIL(self, test_case_no, cmd_list):
        ''' This function will wait until the element is visible '''
        try:
            elem = None
            element_obj = None
            if "/html/body" not in cmd_list[1]:
                elem = self.get_element(
                    "//body//*[contains(text(),'" + cmd_list[1] + "')]"
                )
                element_obj = self.get_element_abs_path(text=cmd_list[1])

            elif "/html/body" in cmd_list[1]:
                elem = self.get_element(cmd_list[1])
                element_obj = cmd_list[1]

            else:
                return False

            if elem:
                cmd_list[1] = element_obj
                if self.base_config_dict["locale"] == "en-US":
                    self.create_script(test_case_no, cmd_list)
                return True
            else:
                return False

        except Exception as e:
            self.logger.exception("element: {}  not found".format(cmd_list[1]))
            self.test_case_fail = True

    def HOVER(self, test_case_no, cmd_list, regionPoints={}, regionName=False):
        ''' This function will emulate the mouse hover action '''
        try:
            if "region" in cmd_list[-1].split("=")[0] == 2 or regionPoints:

                if regionPoints:
                    pass
                elif cmd_list[-1].split("=")[1]:
                    regionName = cmd_list[-1].split("=")[1]
                    regionPoints = self.getRegion(regionName, points=True)
                    self.logger.info("your region is in :- {}".format(regionPoints))

                else:
                    raise Exception("Region name not specefied.")

                if "/html/body" not in cmd_list[1]:
                    element_objs = self.get_element_abs_path(
                        text=cmd_list[1], flag=True
                    )
                    validElements = [
                        element
                        for element in element_objs
                        if self.isValidElement(
                            element, regionPoints, regionName, searchText=cmd_list[1]
                        )
                    ]

                    if len(validElements)>1:
                        message = "{} text found {} valid times in specefied region. ".format(cmd_list[1],len(validElements))
                        print(message)
                        self.logger.warning(message)

                    if len(validElements) == 1:
                        cmd_list[1] = validElements[0]
                        self.create_script(test_case_no, cmd_list)

            # input_obj = None
            # print(cmd_list[-1])
            elif "/html/body" not in cmd_list[1]:
                element = self.get_element_abs_path(text=cmd_list[1])
                # print(element)
                cmd_list[1] = element
                self.create_script(test_case_no, cmd_list)

            element_obj = self.get_element(cmd_list[1])
            # print(element_obj)
            ActionChains(self.driver).move_to_element(element_obj).perform()
            time.sleep(1)
            return True
        except Exception as e:
            self.logger.error("element: {}  not found".format(cmd_list[1]))
            self.logger.exception(e)
            self.test_case_fail = True

    def NAVIGATE(self, test_case_no, cmd_list):
        ''' This function will navigate to the menu pages. It uses the internal functions like hover and click. '''
        print("test_case = {}, cmd is {} ".format(test_case_no, cmd_list))
        self.logger.info("test_case = {}, cmd is {} ".format(test_case_no, cmd_list))
        time.sleep(2)
        try:
            addFlag = 1
            regionName = "menu_region"
            regionPoints = self.getRegion(regionName, points=True)
            iterator = 0
            path = cmd_list[-1]
            dirs = path.split(">>")
            locale = self.base_config_dict["locale"]
            for page in dirs:
                # print(page)
                if page == dirs[-1]:
                    print("click = " + page)
                    self.logger.info("click = " + page)
                    self.CLICK(test_case_no, ["CLICK", page], regionPoints, regionName)
                    directory = copy.deepcopy(
                        self.base_config_dict["required_screenshot_dir"]
                    )

                    for i in range(1, len(directory) + 1):
                        if not os.path.exists(os.path.join(*directory[:i])):
                            print("directory not found for saving screenshot but creating one")
                            self.logger.info("directory not found for saving screenshot but creating one")
                            os.mkdir(os.path.join(*directory[:i]))

                    if locale in os.listdir(os.path.join(*directory)):
                        directory.append(locale)
                    else:
                        directory.append(locale)
                        os.mkdir(os.path.join(*directory))

                    fullPath = os.path.join(*directory, "_".join(dirs) + ".png")
                    # print(directory)
                    time.sleep(2)
                    self.fullpageSnapshot(fullPath)
                    self.create_script(test_case_no, ["SCREENSHOT", "_".join(dirs)])
                    addFlag = 0
                else:
                    print("hover = " + page)
                    self.logger.info("hover = " + page)
                    self.HOVER(test_case_no, ["HOVER", page], regionPoints, regionName)
                if addFlag:
                    regionPoints["start"]["x"] += regionPoints["width"]
                    regionPoints["end"]["x"] += regionPoints["width"]

        except Exception as e:
            self.logger.error("element: {}  not found".format(cmd_list[1]))
            self.logger.exception(e)
            self.test_case_fail = True

    def INPUT(self, test_case_no, cmd_list):
        ''' This function will be used to input data inside <input> tag '''
        try:
            input_obj = None
            if "/html/body" not in cmd_list[1]:
                element_obj = self.get_element_abs_path(text=cmd_list[1])
                xpath = element_obj + "/following::input[1]"
                input_obj = self.get_element(xpath)
                cmd_list[cmd_list.index("INPUT") + 1] = xpath
                self.create_script(test_case_no, cmd_list)

            # incase of xpaths
            # elif "//" in cmd_list[1]:
            #     pdb.set_trace()
            #     try:
            #         input_obj = self.get_element(cmd_list[cmd_list.index("INPUT") + 1])
            #         self.create_script(test_case_no, cmd_list)
            #     except Exception as e:
            #         self.logger.exception("element not found")
            #         self.test_case_fail = True
            #         return False

            elif "/html/body" in cmd_list[1]:
                input_obj = self.get_element(cmd_list[cmd_list.index("INPUT") + 1])

            input_obj.send_keys(cmd_list[cmd_list.index("AS") + 1])
            return True
        except Exception as e:
            self.logger.exception("Element not found")
            self.test_case_fail = True

    def get_element(self, locator, flag=False, region={}):
        ''' This function will return the element object on screen '''
        try:
            if flag:
                pass
            else:
                return WebDriverWait(self.driver, 2000).until(
                    EC.presence_of_element_located((By.XPATH, locator))
                )
        except Exception as e:
            self.logger.exception(e)

    def wtscript(self, msg_string):
        ''' This module will be used to parse the cmd provided via script '''
        try:
            if msg_string.upper() == "START":
                self.script = dict()
            elif msg_string.upper() == "STOP":
                # print(self.script)
                self.yaml_dump(self.base_config_dict["script_filepath"], self.script)
                self.command_parser(self.base_config_dict["script_filepath"])
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
            self.logger.exception(e)

    def command_substitution(self, test_case_no, cmd_list):
        ''' This module will substitute all the varible and types as required '''
        
        for i in range(len(cmd_list[1:])):  # check for parameter list

            # self.create_script(test_case_no, cmd_list)

            if re.match(
                r"^\$", cmd_list[i + 1]
            ):  # check if variable and substitute value
                cmd_list[i + 1] = getattr(self, cmd_list[i + 1].replace("$", ""))

            elif re.match(
                r"^\{|\[", cmd_list[i + 1]
            ):  # check type and convert string to that type accordingly
                cmd_list[i + 1] = ast.literal_eval(cmd_list[i + 1])
        return cmd_list

    def testcases_loader(self, filename=None, all_testcases=None):
        ''' Function to load the testcase from yml file/files according to the SEQUENCE provided by user. '''

        test_sequence = []
        if filename:
            new_testcases = self.yaml_loader(filename)
        elif all_testcases:
            new_testcases = all_testcases
        else:
            print("Proper data not passes for SEQUENCE in code.")
            self.logger.error("Proper data not passes for SEQUENCE in code.")
            exit()
        if "SEQUENCE" in new_testcases:
            testcase_keys = new_testcases["SEQUENCE"]
            testcase_keys.reverse()
            while testcase_keys:
                key = testcase_keys.pop()
                # print(key)
                # Validation to test if testcase is defined.
                if not re.search(r"\.yml$", key) and key not in new_testcases:
                    print("invalid testcase/module : {}".format(key))
                    self.logger.exception("invalid testcase/module : {}".format(key))
                    testcase_keys.remove(key)

                # If yml is found in the sequence.
                if re.search(r"\.yml$", key):
                    # print(key)
                    file = key
                    name = file.split(".yml")[0]
                    file_testcases, file_test_sequence = self.testcases_loader(
                        filename=file
                    )

                    # Updating testcase name if duplicate is found.
                    for case in file_test_sequence:
                        if case in new_testcases:
                            new_testcases[case + name] = {}
                            new_testcases[case + name] = file_testcases[case]
                            testcase_keys.append(case + name)
                        else:
                            new_testcases[case] = file_testcases[case]
                            testcase_keys.append(case)
                else:
                    test_sequence.append(key)

            # print(new_testcases,test_sequence)
            return (new_testcases, test_sequence)
        else:
            print("SEQUENCE not specefied.")
            self.logger.exception("SEQUENCE not specefied.")
            exit()

    def command_parser(self, filename=None):
        ''' This module will parse the entire script and execute it one by one. '''
        
        # check if custom file name is passed and which locale is set and accordingly select the script file
        if not filename:
            if self.base_config_dict["locale"] == "en-US":
                filename = self.base_config_dict["script_filepath"]
            else:
                filename = self.base_config_dict["wtscript_filepath"]

        try:
            self.test_case_fail = False
            locale = self.base_config_dict["locale"]

            self.script_dict = self.yaml_loader(filename)
            full_script = dict()
            temp_script = copy.deepcopy(self.script_dict)

            if locale == "en-US":
                for key, script in temp_script.items():
                    full_script[key] = self.cmd_substitution_stack(script)
            else:
                full_script = self.script_dict

            full_script, testcase_keys = self.testcases_loader(
                all_testcases=full_script
            )
            full_script["SEQUENCE"] = testcase_keys
            self.WTScript["SEQUENCE"] = testcase_keys
            # print(testcase_keys)
            # print(full_script)

            # testcase_keys is the keys present in SEQUENCE block.
            for key in testcase_keys:  # Access all the testcase as per the key sequence
                test_case_no = key
                self.logger.info("Executing testcase : {}".format(key))
                # print( full_script)

                for cmd_str in full_script[key]:  # Access the list for single testcase

                    cmd_list = cmd_str.split("  ")
                    cmd_list = self.command_substitution(
                        test_case_no=test_case_no, cmd_list=cmd_list
                    )  # parser for $ and {}

                    if (test_case_no not in self.WTScript) and (locale == "en-US"):
                        self.WTScript[test_case_no] = list()

                    if cmd_list[0].upper() == "GOTO":
                        self.GOTO(test_case_no, cmd_list)

                    elif cmd_list[0].upper() == "CHECK":
                        if cmd_list[1].upper() == "LINK":
                            self.check_broken_links(test_case_no, cmd_list)
                        elif cmd_list[1].upper() == "TITLE":
                            self.check_title(cmd_list[2])

                    # Alert handling
                    elif cmd_list[0].upper() == "ALERT":
                        if self.ALERT(test_case_no, cmd_list):
                            self.logger.info(
                                "{} :: handled alert".format("  ".join(cmd_list))
                            )
                        else:
                            self.logger.exception(
                                "{} :: handled alert".format("  ".join(cmd_list))
                            )
                            self.test_case_fail = True

                    # click element on html page
                    elif cmd_list[0].upper() == "CLICK":
                        if self.CLICK(test_case_no, cmd_list):
                            self.logger.info(
                                "{} :: element clicked".format("  ".join(cmd_list))
                            )
                        else:
                            self.logger.exception(
                                "{} :: element not found".format("  ".join(cmd_list))
                            )
                            self.test_case_fail = True

                    # Input text in input element on html page
                    elif cmd_list[0].upper() == "INPUT":
                        if self.INPUT(test_case_no, cmd_list):
                            self.logger.info(
                                "{} :: element input".format("  ".join(cmd_list))
                            )
                        else:
                            self.logger.exception(
                                "{} :: element not found".format("  ".join(cmd_list))
                            )
                            self.test_case_fail = True

                    # radio or checkbox selection
                    elif (
                        cmd_list[0].upper() == "SELECT"
                        or cmd_list[0].upper() == "CHECK"
                    ):
                        if self.RADIO_CHECKBOX(test_case_no, cmd_list):
                            self.logger.info(
                                "{} :: element selected".format("  ".join(cmd_list))
                            )
                        else:
                            self.logger.exception(
                                "{} :: element not found".format("  ".join(cmd_list))
                            )
                            self.test_case_fail = True

                    # Wait for something in html
                    elif cmd_list[0].upper() == "WAIT":
                        if self.WAIT_UNTIL(test_case_no, cmd_list):
                            self.logger.info(
                                "{} :: Wait executed".format("  ".join(cmd_list))
                            )
                        else:
                            self.logger.exception(
                                "{} :: element not found".format("  ".join(cmd_list))
                            )
                            self.test_case_fail = True
                            self.take_screenshot = False

                    # Hover html element
                    elif cmd_list[0].upper() == "HOVER":
                        # print(cmd_list)
                        if self.HOVER(test_case_no, cmd_list):
                            self.logger.info(
                                "{} :: Hover executed".format("  ".join(cmd_list))
                            )
                        else:
                            self.logger.exception(
                                "{} :: element not found".format("  ".join(cmd_list))
                            )
                            self.test_case_fail = True

                    # Navigate to respective pages
                    elif cmd_list[0].upper() == "NAVIGATE":
                        if self.NAVIGATE(test_case_no, cmd_list):
                            self.logger.info(
                                "{} :: Hover executed".format("  ".join(cmd_list))
                            )
                        else:
                            self.logger.exception(
                                "{} :: element not found".format("  ".join(cmd_list))
                            )
                            self.test_case_fail = True
                    # if want to declare variable with value or with return value from function
                    elif re.match(r"^\$", cmd_list[0]):

                        # if function returns value
                        if cmd_list[1].upper() == "FUNCTION":

                            # declare variable with the value returned from function
                            try:
                                setattr(
                                    self,
                                    cmd_list[0].replace("$", ""),
                                    getattr(self, cmd_list[2])(*cmd_list[3:]),
                                )
                            except Exception as e:
                                print(
                                    "function {} not found or improper call".format(
                                        cmd_list[2]
                                    )
                                )
                                self.logger.exception(
                                    "function {} not found or improper call ".format(
                                        cmd_list[2]
                                    )
                                )

                        # variable declaration
                        else:
                            try:
                                setattr(self, cmd_list[0].replace("$", ""), cmd_list[1])
                            except Exception as e:
                                print("cannot set this variable")
                                self.logger.exception("cannot set this variable")

                        self.create_script(test_case_no, cmd_list)

                    elif (
                        cmd_list[0].upper() == "FUNCTION"
                    ):  # This block will call custom function

                        try:
                            getattr(self, cmd_list[1])(*cmd_list[2:])  # function call
                            self.create_script(test_case_no, cmd_list)
                        except Exception as e:
                            print(
                                "function {} not found or improper call".format(
                                    cmd_list[1]
                                )
                            )
                            self.logger.exception(
                                "function {} not found or improper call".format(
                                    cmd_list[1]
                                )
                            )

                    elif cmd_list[0].upper() == "PRINT":
                        print(cmd_list[1])
                        self.take_screenshot = False
                        # self.create_script(test_case_no, cmd_list)

                    elif cmd_list[0].upper() == "CHOOSE":
                        self.CHOOSE(test_case_no, cmd_list)

                    # By default sleep for 10 seconds.
                    elif cmd_list[0].upper() == "SLEEP":
                        if len(cmd_list)==2 and cmd_list[1].isdigit():
                            sleepTime = int(cmd_list[1])
                            print("Sleeping for {} seconds".format(sleepTime))
                            time.sleep(sleepTime)
                        else:
                            print("Sleeping for 10 seconds")
                            time.sleep(10)
                        self.create_script(test_case_no, cmd_list)
                        self.take_screenshot = False

                    elif cmd_list[0].upper() == "SCREENSHOT":
                        if cmd_list[1]:
                            imageExtensions = (".jpg", ".jpeg", ".png")
                            validExtention = (
                                cmd_list[1].endswith(extention)
                                for extention in imageExtensions
                            )
                            directory = self.base_config_dict["required_screenshot_dir"]

                            for i in range(1, len(directory) + 1):
                                if not os.path.exists(os.path.join(*directory[:i])):
                                    print("directory not found but creating one")
                                    os.mkdir(os.path.join(*directory[:i]))

                            if locale in os.listdir(os.path.join(*directory)):
                                directory.append(locale)
                            else:
                                directory.append(locale)
                                os.mkdir(os.path.join(*directory))

                            if any(validExtention):
                                imageName = os.path.join(*directory, cmd_list[1])
                                self.fullpageSnapshot(imageName)
                            else:
                                imageName = os.path.join(
                                    *directory, cmd_list[1] + ".png"
                                )
                                self.fullpageSnapshot(imageName)
                            self.create_script(test_case_no, cmd_list)
                            self.take_screenshot = False

                    elif cmd_list[0].upper() == "PRINT":
                        print(cmd_list[1])
                        self.logger.info(cmd_list[1])
                        self.create_script(test_case_no, cmd_list)
                        self.take_screenshot = False

                    elif cmd_list[0].upper() == "I18N":
                        # print('pass')
                        self.i18n_obj.i18n_get_all_text()
                        if self.base_config_dict["locale"] == "en-US":
                            print("writing I18N in wtscript.")
                            self.logger.info("writing I18N in wtscript.")
                            self.create_script(test_case_no, cmd_list)
                        self.take_screenshot = False

                    else:
                        print("Invalid command passed...")
                        self.logger.error("Invalid command passed...")

                    # Take screentshot after every cmd
                    if self.take_screenshot:
                        self.fullpageSnapshot()
                        self.logger.info("Screenshot clear.")
                    else:
                        self.take_screenshot = True
                    time.sleep(2)

                # print("excuted : "+test_case_no)
                # self.logger.info("executed : {}".format(test_case_no))
                # self.app_self.logger("INFO","executed {}".format(test_case_no))

            if locale == "en-US":
                # print("EStart")
                self.yaml_dump(
                    self.base_config_dict["wtscript_filepath"], self.WTScript
                )
                print("WTScript:- Writing successful")
                self.logger.info("WTScript:- Writing successful")

        except Exception as e:
            self.logger.exception(e)

    def cmd_substitution_stack(self, script):
        """
        This function will reslove the recursive testcase call and return single script
        :param script:
        :return: full script
        """

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
            self.logger.exception("Error in cmd substitution stack")

    def fullpageSnapshot(self, filename=None):
        """
        This function will take entire screenshot.
        :param filename: file to save screenshot image (optional)
        :return: fullpage screenshot image name
        """
        try:
            if not filename:
                filename = self.date_generator()

                self.filepath = self.base_config_dict["all_screenshot_dir"]
                self.filetype = ".png"

                for i in range(1, len(self.filepath) + 1):
                    if not os.path.exists(os.path.join(*self.filepath[:i])):
                        print("directory not found to save screenshot but creating one")
                        self.logger.info("directory not found to save screenshot but creating one")
                        os.mkdir(os.path.join(*self.filepath[:i]))

                FQ_filename = os.path.join(
                    *self.filepath, str(filename) + self.filetype
                )
            else:
                dirPath = filename.split("/")[:-2]
                if filename.split("/")[-1] in os.listdir(os.path.join(*dirPath)):
                    os.remove(filename)
                time.sleep(2)
                FQ_filename = str(filename)
                # print(filename)
                self.logger.info(filename)

            self.driver.get_screenshot_as_file(FQ_filename)

            self.logger.info("Screenshot : {}".format(FQ_filename))
            return FQ_filename

        except Exception as e:
            self.logger.exception(e)
            self.logger.exception("Error in selenium screenshot module")

    def check_broken_links(self, test_case_no, cmd_list):
        """
        This function is used to check if the given link is broken or not.It simply makes a http call and checks response
        :param url: link which you want to check
        :return: True if response is 200 else False
        """

        try:
            url = cmd_list[2]
            if not re.match(r"^www|http", url):
                link_abs_path = self.get_element_abs_path(text=url)
                url = self.driver.find_element_by_xpath(link_abs_path).get_attribute(
                    "href"
                )

                cmd_list[2] = url
                self.create_script(test_case_no, cmd_list)

            self.logger.info("visiting : {}".format(url))
            request = requests.get(url, verify=False)
            if request.status_code == 200:
                print("Web site exists")
                self.logger.info("Web site exists")
                return True
            else:
                print("Web site does not exist")
                self.logger.warning("Web site does not exist")
                return False
        except Exception as e:
            self.logger.exception("cannot access the link")
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

    def report_gen(self, filename):
        raw_report = [line.rstrip("\n") for line in open(filename)]
        for line in raw_report:
            if ":INFO:" in line or ":ERROR:" in line or ":WARNING:" in line:
                with open("report.txt", "a") as the_file:
                    the_file.write("{} \n".format(line))