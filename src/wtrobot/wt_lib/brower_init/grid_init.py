from .browser_options import BrowserOptions
from selenium import webdriver

class GridInit:
    
    def __init__(self, global_conf) -> None:
        self.global_conf = global_conf

    # init firefox browser
    def _browser(self):
        
        return webdriver.Remote(
            command_executor=self.global_conf['selenium_grid_ip'],
            # options= BrowserOptions.firefox_options(self.global_conf['locale'])
            options = getattr(BrowserOptions, self.global_conf['browser']+"_options")(self.global_conf['locale'])
        )
