import time
import logging
from selenium.common.exceptions import (
    ElementNotInteractableException,
    ElementNotVisibleException,
    TimeoutException,
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from wtrobot.utils.util import Utils
from wtrobot.wt_lib.operations import Operations
from wtrobot.wt_lib.brower_init.main import Browser

class Actions():

    def __init__(self, global_conf):
        self.global_conf = global_conf
        self.driver = Browser(global_conf).browser_init()
        self.opr_obj = Operations(self.driver, global_conf)
    
    def logger_decorator(function):
        def logger_wrapper(*args):
            self = args[0]
            test_data = args[1]

            # If no name key in step then add empty string
            name  = ""
            _sep = ""
            if "name" in test_data.keys():
                name = test_data["name"]
                _sep = ":"
            logging.info(
                "TestCase:{0} - Step:{1}{2}{3}".format(
                    test_data["testcase_no"], test_data["step_no"],_sep,name
                )
            )

            # If sleep key mentioned in steps
            if "sleep" in test_data.keys():
                logging.info(
                    "Sleep for {0} seconds before {1} ".format(
                        test_data["sleep"], test_data["action"]
                    )
                )
                time.sleep(test_data["sleep"])

            # If wait before action mentioned in steps
            elif "wait before action" in test_data.keys():
                logging.info("waiting before action")
                self.opr_obj.wait(test_data["wait before action"])

            # method call
            test_result_data = function(*args)

            # If wait before action mentioned in steps
            if "wait after action" in test_data.keys():
                logging.info("waiting after action")
                self.opr_obj.wait(test_data["wait after action"])

            # assert or check anything after performing the current action
            if "assert" in test_data.keys():
                logging.info("asserting after action")
                # split value at "=" to get assertion criteria and value
                assert_by, assert_data =test_data["assert"].split("=",1)
                
                if assert_by.lower() == "text" or assert_by.lower() == "xpath":
                    logging.info("check if text/xpath {0} is present on page".format(assert_by))
                    if self.opr_obj.get_element_by_xpath_or_text(assert_data):
                        logging.info("assertion passed")
                    else:
                        logging.info("assertion failed")
                        test_data["error"] = True

                elif assert_by.lower() == "locator":
                    logging.info("check if locator {0} is present on page".format(assert_by))
                    if self.opr_obj.get_element(assert_data):
                        logging.info("assertion passed")
                    else:
                        logging.info("assertion failed")
                        test_data["error"] = True
                        
                elif assert_by.lower() == "link" or assert_by.lower() == "goto":
                    logging.info("check if we are redirected to {0}".format(assert_by))
                    if self.driver.current_url == assert_data:
                        logging.info("assertion passed")
                    else:
                        logging.info("assertion failed")
                        test_data["error"] = True
                else:
                    logging.info("Invalid assertion type passed")
                    test_data["error"] = True

            # screenshot after every action
            screenshot_file_name = None
            if "screenshot_name" not in test_data.keys():
                screenshot_file_name = "{0}_{1}_{2}_{3}".format(
                    test_data["testcase_no"],
                    test_data["step_no"],
                    self.global_conf["locale"],
                    str(int(round(time.time() * 1000))),
                )
            else:
                screenshot_file_name = "{0}_{1}".format(
                    self.global_conf["locale"], test_data["screenshot_name"]
                )
            self.opr_obj.full_page_screenshot(screenshot_file_name)

            return test_result_data

        return logger_wrapper


    @logger_decorator
    def alertmessage(self, test_data):
        """
        This function will handle all alert messages
        """
        try:
            WebDriverWait(self.driver, 10).until(
                EC.alert_is_present(), "Waiting for alert timed out"
            )
            alert = self.driver.switch_to.alert
            if test_data["value"] == "ok":
                alert.accept()
            elif test_data["value"] == "cancel":
                alert.dismiss()
            else:
                alert.accept()
        except TimeoutException:
            test_data["error"] = True
        return test_data

    @logger_decorator
    def scroll(self, test_data):
        """
        This function will scroll given page as per given params
        specify target or x,y 
        default it will do page down
        """
        try:

            if "target" in test_data.keys():
                test_data = self.opr_obj.get_element(test_data)
                self.driver.execute_script(
                    "arguments[0].scrollIntoView();", test_data["element_obj"]
                )
            elif "x" in test_data.keys() or "y" in test_data.keys():
                if "x" not in test_data.keys():
                    test_data["x"] = 0
                elif "y" not in test_data.keys():
                    test_data["y"] = 0
                self.driver.execute_script(
                    "window.scrollTo(arguments[0], arguments[1]);",
                    test_data["x"],
                    test_data["y"],
                )
            else:
                test_data["values"] = "Keys.PAGE_DOWN"
                test_data = self.sendkeys(test_data)

        except Exception as e:
            logging.error(e)
            test_data["error"] = True
        return test_data

    @logger_decorator
    def sendkeys(self, test_data):
        """
        https://seleniumhq.github.io/selenium/docs/api/py/webdriver/selenium.webdriver.common.keys.html
        """
        try:
            print(test_data)
            if "values" in test_data.keys():
                actions = ActionChains(self.driver)

                if "Keys" in test_data["values"]:
                    actions.send_keys(getattr(Keys, test_data["values"].split(".")[1]))
                else:
                    actions.send_keys(test_data["values"])
                actions.perform()

            else:
                logging.error("values attribute not specified/invalid")
                test_data["error"] = True
        except Exception as e:
            logging.error(e)
            test_data["error"] = True
        return test_data

    @logger_decorator
    def goto(self, test_data):
        """
        This function will visit the URL specified
        :param test_data:
        :return: None
        """
        try:
            if test_data["target"]:
                if Utils.check_url(test_data["target"]):
                    self.driver.get(test_data["target"])
                else:
                    logging.error("Target URL not specified/invalid")
            else:
                logging.error("Target URL not specified/invalid")
                test_data["error"] = True
        except Exception as e:
            logging.error(e)
            test_data["error"] = True
        return test_data

    @logger_decorator
    def click(self, test_data):
        try:
            test_data = self.opr_obj.get_element(test_data)
            test_data["element_obj"].click()
            # self.driver.switch_to_default_content()
        except (ElementNotVisibleException, ElementNotInteractableException):
            click_obj = None
            for locator in test_data["targets"]:
                if not click_obj:
                    test_data["target"] = locator
                    logging.info(
                        "finding element for actionchain click using locator: {0} ".format(
                            locator
                        )
                    )
                    try:
                        click_obj = WebDriverWait(self.driver, 10).until(
                            EC.visibility_of_element_located(
                                (By.XPATH, test_data["target"])
                            )
                        )
                    except Exception:
                        click_obj = None
                else:
                    break
            if click_obj:
                ActionChains(self.driver).move_to_element(click_obj).perform()
            else:
                logging.exception("error")
                test_data["error"] = True
        except:
            logging.exception("error")
            test_data["error"] = True

        return test_data

    @logger_decorator
    def hover(self, test_data):
        try:
            test_data = self.opr_obj.get_element(test_data)
            ActionChains(self.driver).move_to_element(
                test_data["element_obj"]
            ).perform()
        except Exception as e:
            logging.exception(e)
            test_data["error"] = True

        return test_data

    @logger_decorator
    def input(self, test_data):
        try:
            test_data = self.opr_obj.get_element(test_data)
            test_data["element_obj"].send_keys(test_data["value"])
        except Exception as e:
            logging.exception(e)
            test_data["error"] = True

        return test_data

    @logger_decorator
    def screenshot(self, test_data):
        try:
            screenshot_file_name = None
            if "screenshot_name" not in test_data.keys():
                screenshot_file_name = "{0}_{1}_{2}_{3}".format(
                    test_data["testcase_no"],
                    test_data["step_no"],
                    self.global_conf["locale"],
                    str(int(round(time.time() * 1000))),
                )
            else:
                screenshot_file_name = "{0}_{1}".format(
                    self.global_conf["locale"], test_data["screenshot_name"]
                )

            self.opr_obj.full_page_screenshot(screenshot_file_name)
        except Exception as e:
            logging.exception(e)
            test_data["error"] = True

        return test_data

    @logger_decorator
    def sleep(self, test_data):
        try:
            time.sleep(test_data["value"])
        except Exception as e:
            logging.exception(e)
            test_data["error"] = True
        return test_data

    @logger_decorator
    def validate(self, test_data):

        xpath_denoter = ("//", "/html", "/")

        if test_data["target"].startswith(xpath_denoter):
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, test_data["target"]))
                )
            except:
                logging.error("Element not found")
                test_data["error"] = True
        else:
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//*[contains(text(), '{0}')]".format(test_data["target"]),
                        )
                    )
                )
            except:
                logging.error("Element not found")
                test_data["error"] = True

        return test_data

    @logger_decorator
    def function(self, test_data):
        print("yet to implement")
        return test_data

    def closebrowser(self, test_data):
        try:
            logging.info("Closing browser...")
            self.driver.close()
        except Exception as e:
            logging.exception(e)
        return test_data
