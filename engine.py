#!/usr/bin/env python

import time
import logging
from selenium import webdriver
import os
import lib

from lib.zanata_tm_parser import ZANATA_TM_PARSER
from lib.base_manager import UtilityMixin

import argparse

def log(log_file):
    open(log_file,'w').close()
    FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(lineno)d:%(message)s"
    datestr = "%m/%d/%Y %I:%M:%S %p"
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt=FORMAT,datefmt=datestr)
    
    file_handler = logging.FileHandler(filename=log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger

def main():
    '''
    Main function to trigger all the functionalities of WTRobot.
    '''
    util = UtilityMixin()
    config_file = util.config_data
    log_file = config_file["log_file"]
    logger = log(log_file)
    logger.info("Started with WTRobot script.")

    data = {}
    with open("valid_locales.txt") as file:
        locales = [locale.strip() for locale in file.readlines()]

    # arg parser to get filename if any.
    parser = argparse.ArgumentParser(
        description="Welcome to WTRobot, lets make your automation bit simpler."
    )
    parser.add_argument(
        "-f",
        "--file",
        action="store",
        dest="filename",
        help="Please enter absolute path only.",
    )
    parser.add_argument(
        "-t",
        "--get-translation",
        action="store_true",
        dest="translation",
        help="Use this flag to get the translation locally.",
    )
    parser.add_argument(
        "-l",
        "--locale",
        action="store",
        dest="locale",
        help="Enter the lang to update in config and use it further.",
    )
    parser.add_argument("task", help="1) run 2) config.")
    args = parser.parse_args()

    if args.task in ["config", "run"] and args.locale:
        if args.locale not in locales:
            print("Please insert the valid locale.", args.locale, locales)
            exit()
        data["locale"] = args.locale
        util.config_data = data

    else:
        data["locale"] = "en-US"
        util.config_data = data

    if args.task == "config" and args.translation:
        translator = ZANATA_TM_PARSER()
        exit()

    if args.task == "run":

        try:
            profile = webdriver.FirefoxProfile()
            profile.set_preference("intl.accept_languages", data["locale"])
            profile.accept_untrusted_certs = True
            driver = webdriver.Firefox(
                firefox_profile=profile,
                executable_path="./selenium_drivers/geckodriver",
                log_path="./logs/geckodriver.log",
            )
            driver.maximize_window()

        except Exception as e:
            print(e)
            exit()

        obj = lib.WTRobot(driver=driver)

        if args.filename:
            obj.command_parser(filename=args.filename)
        else:
            obj.command_parser()

        time.sleep(5)
        obj.report_gen("./logs/logger.log")
        driver.close()
        logger.info("Completed!")

if __name__ == "__main__":
    main()