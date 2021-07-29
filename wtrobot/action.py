import re
import time
import logging

from requests import check_compatibility
from wtrobot import Operations, ActionChains, webdriver, WebDriverWait, EC, By
from selenium.common.exceptions import (
    ElementNotInteractableException,
    ElementNotVisibleException,
    TimeoutException,
)
from selenium.webdriver.common.keys import Keys


class Actions(Operations):
    def __init__(self, global_conf):
        self.global_conf = global_conf
        self.browser_init()

    def logger_decorator(function):
        def logger_wrapper(*args):
            self = args[0]
            test_data = args[1]

            # If no name key in step then add none to avoid execption
            if "name" not in test_data.keys():
                test_data["name"] = None

            logging.info(
                "TestCase:{0} - Step:{1} - {2}".format(
                    test_data["testcase_no"], test_data["step_no"], test_data["name"]
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
                self.wait(test_data["wait before action"])

            # check if target element is pseudo translated
            if "check pseudo translated" in test_data.keys():
                if test_data["check pseudo translated"]:
                    def check_pseudo_translated(test_data):
                        pseudo_translate_regex =  "\[[^\]]*\]"
                        test_data = self.get_element(test_data)
                        target_str = test_data["element_obj"].text
                    
                        if not re.search(pseudo_translate_regex, target_str):
                            test_data["error_pseudo_translated_check"] = True
                            test_data["error_pseudo_translated_str"] = target_str
                            #print("Not Pseudo Translated")
                        else:
                            #print("Pseudo translated")
                            pass
                    check_pseudo_translated(test_data)

            # check if target element is translated
            if "check translated" in test_data.keys():
                if test_data["check translated"]:
                    def check_translated(test_data):
                        test_data = self.get_element(test_data)
                        target_str = test_data["element_obj"].text
                    
                        target_text = target_str.encode('unicode_escape')
                        if self.global_conf["locale"] != "en_US":
                            # check unicode pattern string
                            if b"\\u" not in target_text:
                                test_data["error_translated_check"] = True
                                test_data["error_translated_str"] = target_str
                    check_translated(test_data)

            # method call
            test_result_data = function(*args)

            # If wait before action mentioned in steps
            if "wait after action" in test_data.keys():
                logging.info("waiting after action")
                self.wait(test_data["wait after action"])

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
            self.full_page_screenshot(screenshot_file_name)

            return test_result_data

        return logger_wrapper

    def browser_init(self):
        """
        init all selenium browser session and create driver object
        """
        if (
            not self.global_conf["webdriver_path"]
            and self.global_conf["browser"].lower() == "firefox"
        ):
            self.global_conf["webdriver_path"] = "./selenium_drivers/geckodriver"
        elif (
            not self.global_conf["webdriver_path"]
            and self.global_conf["browser"].lower() == "chrome"
        ):
            self.global_conf["webdriver_path"] = "./selenium_drivers/chromedriver"

        if self.global_conf["browser"].lower() == "firefox":
            profile = webdriver.FirefoxProfile()
            profile.set_preference("intl.accept_languages", self.global_conf["locale"])
            profile.accept_untrusted_certs = True
            self.driver = webdriver.Firefox(
                firefox_profile=profile,
                executable_path=self.global_conf["webdriver_path"],
            )
        elif self.global_conf["browser"].lower() == "chrome":
            options = webdriver.ChromeOptions()
            options.add_experimental_option(
                "prefs",
                {"intl.accept_languages": "{0}".format(self.global_conf["locale"])},
            )
            self.driver = webdriver.Chrome(
                executable_path=self.global_conf["webdriver_path"],
                chrome_options=options,
            )

        self.driver.maximize_window()

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
                test_data = self.get_element(test_data)
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
                if self.check_url(test_data["target"]):
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
            test_data = self.get_element(test_data)
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
            test_data = self.get_element(test_data)
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
            test_data = self.get_element(test_data)
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

            self.full_page_screenshot(screenshot_file_name)
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
