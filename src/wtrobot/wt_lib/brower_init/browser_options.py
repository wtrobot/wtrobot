from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

class BrowserOptions:
    
    @staticmethod
    def firefox_options(locale):
        options = FirefoxOptions()
        options.set_preference("intl.accept_languages", locale)
        options.accept_untrusted_certs = True
        return options
    
    @staticmethod
    def chrome_options(locale):
        options = ChromeOptions()
        options.add_experimental_option(
            "prefs",
            {"intl.accept_languages": "{0}".format(locale)},
        )
        return options
