import sys, os, json
import logging
from wtrobot import commmandParser

def logger_init(filename, dev=False):
    
    format_str = None
    if dev:
        format_str = "%(levelname)s - %(asctime)s - %(filename)s - %(lineno)d - %(message)s"
    else:
        format_str = "%(levelname)s - %(asctime)s - %(message)s"
    
    logging.basicConfig(
        filename=filename,
        level=logging.INFO,
        format=format_str,
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter(format_str)
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)
    # marker to denote new log starting
    logging.info("------------------new---------------------")

def get_abs_filepath(filepath):
    return os.path.join(os.getcwd(),filepath)

def main():
    config_file_name = get_abs_filepath("config.json")
    config = dict()
    count = 0
    try:
        with open(config_file_name) as fobj:
            config = json.load(fobj)
            count = len(config)
    except (OSError, json.decoder.JSONDecodeError):
        print(
            "config file missing or incorrect, please provide following configurations..."
        )

    if config is None or "script_filepath" not in config.keys():
        config["script_filepath"] = (
            input("Test script filename: test.yaml ? ") or "test.yaml"
        )

    if config is None or "browser" not in config.keys():
        config["browser"] = input("Which browser : firefox ? ") or "firefox"

    if config is None or "webdriver_path" not in config.keys():
        config["webdriver_path"] = (
            input("Selenium webdriver : selenium_drivers/geckodriver ? ")
            or "selenium_drivers/geckodriver"
        )

    if config is None or "locale" not in config.keys():
        config["locale"] = input("Which browser locale : en_US ? ") or "en_US"

    if config is None or "log" not in config.keys():
        config["log"] = (
            input("WTRobot execution log file path : wtlog.log ? ") or "wtlog.log"
        )

    # If you are developing the test suit set dev attribute in config to True 
    # dev env not specified then set it to false (default)
    # This flag makes logger less or more verbose
    if config is None or "dev" not in config.keys():
        config["dev"] = False
    
    if config["dev"]:
        logger_init(filename=config["log"], dev=True)
    else:
        logger_init(config["log"])

    if not os.path.exists(get_abs_filepath(config["script_filepath"])):
        logging.error("""
        Invalid script file path.
        There is no script file {} at this location.
        first create one and then execute "wtrobot" command.
        """.format(config["script_filepath"]))
        sys.exit(0)

    if not os.path.exists(get_abs_filepath(config["webdriver_path"])):
        logging.error("""
        Invalid webdriver file path.
        There is no webdriver file {} at this location.
        make sure you have/download one at this location and then execute "wtrobot" command.
        https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/
        """)
        sys.exit(0)

    if count < len(config):
        with open(config_file_name, "w") as fobj:
            json.dump(config, fobj, indent=4)

    obj = commmandParser(config)


if __name__ == "__main__":
    main()
