import os
import logging
from time import sleep
import urllib3
urllib3.disable_warnings()
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType

from .browser_options import BrowserOptions

from dotenv import load_dotenv
load_dotenv()

class BrowserInit:
    
    def __init__(self, global_conf) -> None:
        self.driver_dir = r"Drivers"
        self.global_conf = global_conf
        self.browser = global_conf['browser']
        self.browser_locale = global_conf['locale']
        self.wdm=global_conf['web_driver_manager']
        self.logdir= os.path.join(self.global_conf['resultsdir_path'],"logs")

    # init firefox browser
    def _firefox(self):
        log_path= os.path.join(self.logdir,'geckodriver.log')
        # print(log_path)
        # use webdriver manager
        if self.global_conf['web_driver_manager'] is True:
            logging.info("using wdm to init firefox browser session")
            service = FirefoxService(GeckoDriverManager(path = self.driver_dir).install(), log_path=log_path) if self.wdm else None
            self.driver = webdriver.Firefox(
                options=BrowserOptions.firefox_options(self.browser_locale),
                service=service
            )
        # if not using webdriver manager
        else:
            service = FirefoxService(log_path=log_path)
            # use webdriver from system path
            if self.global_conf['web_driver_path'] and self.global_conf['web_driver_path'].lower() == "local":
                logging.info("using syspath driver to init firefox browser session")
                self.driver = webdriver.Firefox(
                    options=BrowserOptions.firefox_options(self.browser_locale),
                    service=service
                )

            # use webdriver from given path
            else:
                logging.info("using custom driver path to init firefox browser session")
                self.driver = webdriver.Firefox(
                    executable_path=self.global_conf['web_driver_path'],
                    options=BrowserOptions.firefox_options(self.browser_locale),
                    service=service
                )
        return self.driver
    
    # init chrome browser
    def _chrome(self):
        
        log_path= os.path.join(self.logdir,'chromedriver.log')

        # use webdriver manager
        if self.global_conf['web_driver_manager'] is True:
            logging.info("using wdm to init chrome browser session")
            service=ChromeService(ChromeDriverManager(path = self.driver_dir).install(), log_path=log_path) if self.wdm else None
            self.driver = webdriver.Chrome(
                options=BrowserOptions.chrome_options(self.browser_locale),
                service=service
            )
        # if not using webdriver manager
        else:
            service = ChromeService(log_path=log_path)
            # use webdriver from system path
            if self.global_conf['web_driver_path'] and self.global_conf['web_driver_path'].lower() == "local":
                logging.info("using syspath driver to init chrome browser session")
                self.driver = webdriver.Chrome(
                    options=BrowserOptions.chrome_options(self.browser_locale),
                    service=service
                )

            # use webdriver from given path
            else:
                logging.info("using custom driver path to init chrome browser session")
                self.driver = webdriver.Chrome(
                    executable_path=self.global_conf['web_driver_path'],
                    options=BrowserOptions.chrome_options(self.browser_locale),
                    service=service
                )
        return self.driver
    
    # init chromium browser
    def _chromium(self):

        log_path= os.path.join(self.logdir, 'chromedriver.log')
        
        # use webdriver manager
        if self.global_conf['web_driver_manager'] is True:
            logging.info("using wdm to init chromium browser session")
            service=ChromeService(ChromeDriverManager(path = self.driver_dir, chrome_type=ChromeType.CHROMIUM).install(),log_path=log_path) if self.wdm else None
            self.driver = webdriver.Chrome(
                options=BrowserOptions.chrome_options(self.browser_locale),
                service=service
            )
        # if not using webdriver manager
        else:
            service = ChromeService(log_path=log_path)
            # use webdriver from system path 
            if self.global_conf['web_driver_path'] and self.global_conf['web_driver_path'].lower() == "local":
                logging.info("using syspath driver to init chromium browser session")
                self.driver = webdriver.Chrome(
                    options=BrowserOptions.chrome_options(self.browser_locale),
                    service=service
                )
            
            # use webdriver from given path
            else:
                logging.info("using custom driver path to init chromium browser session")
                self.driver = webdriver.Chrome(
                    executable_path=self.global_conf['web_driver_path'],
                    options=BrowserOptions.chrome_options(self.browser_locale),
                    service=service
                )
        return self.driver