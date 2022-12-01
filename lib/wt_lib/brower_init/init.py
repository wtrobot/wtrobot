# selenium 4
from time import sleep
import urllib3
urllib3.disable_warnings()
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from lib.wt_lib.brower_init.browser_options import firefox_options, chrome_options
from dotenv import load_dotenv
load_dotenv()

class Browser_Init:
    
    # here wdm is webdriver_manager you want to enable or disable/use local driver 
    def __init__(self,browser,locale,dir=r"Drivers",wdm=True) -> None:
        self.browser = browser
        self.driver_dir = dir
        self.browser_locale = locale
        self.wdm=wdm
        getattr(self, "_"+self.browser)()

    # init firefox browser
    def _firefox(self):
        service = FirefoxService(GeckoDriverManager(path = self.driver_dir).install()) if self.wdm else None
        self.driver = webdriver.Firefox(
            options=firefox_options(self.browser_locale),
            service=service
        )

    # init chrome browser
    def _chrome(self):
        service=ChromeService(ChromeDriverManager(path = self.driver_dir).install()) if self.wdm else None
        self.driver = webdriver.Chrome(
            options=chrome_options(self.browser_locale),
            service=service
        )

    # init chromium browser
    def _chromium(self):
        service=ChromeService(ChromeDriverManager(path = self.driver_dir, chrome_type=ChromeType.CHROMIUM).install()) if self.wdm else None
        self.driver = webdriver.Chrome(
            options=chrome_options(self.browser_locale),
            service=service
        )

    def browser_init(self):
        getattr(self, "_"+self.browser)()

if __name__ == "__main__":
    obj=Browser_Init(browser="firefox",locale="hi_IN",dir=r"Drivers").driver
    obj.get("https://google.com")
    obj.close()
