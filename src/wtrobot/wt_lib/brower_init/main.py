# selenium 4
import os
import logging
from time import sleep
import urllib3
urllib3.disable_warnings()
from selenium import webdriver

from .browser_init import BrowserInit
from .grid_init import GridInit
from dotenv import load_dotenv
load_dotenv()

class Browser:
    
    # here wdm is webdriver_manager you want to enable or disable/use local driver 
    def __init__(self, global_conf) -> None:
        self.global_conf = global_conf
        # self.browser_init()
        # getattr(self, "_"+self.browser)()

    
    def browser_init(self):
        '''
        call respective browser function and init webdriver 
        '''
        browser_obj = BrowserInit(self.global_conf)
        if self.global_conf['selenium_grid']:
            return GridInit(self.global_conf)._browser()
        else:
            bobj= BrowserInit(self.global_conf) 
            return getattr(bobj, "_"+self.global_conf['browser'])()
            
        if self.global_conf['browser_fullscreen']:
            self.driver.fullscreen_window()
        else:
            self.driver.maximize_window()

if __name__ == "__main__":
    obj=Browser(browser="firefox",locale="hi_IN",dir=r"Drivers").driver
    obj.get("https://google.com")
    obj.close()
