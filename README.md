# *WTRobot*

------------------

## Introduction

The web automation framework inspired from [behave](https://behave.readthedocs.io/en/latest) and [robot](https://robotframework.org) framework. It is a tool to minimize your dependencies on XPATHs for writing end to end automation.

The tool follows a yml scripting which you will find below.

## Setup

### Install

```console
> pip install wtrobot
```

### Build from source

```console
> git clone <this repo>
> cd <repo directory>
> python setup.py install
```

> NOTE

- Selenium_drivers folders have your selenium webdrivers geckodrivers(for firefox) and chromedrivers(for chrome and chromium)
- If script fails due to drivers issue, you need to find appropriate selenium webdriver according to your browser version
  - [firefox](https://github.com/mozilla/geckodriver/releases) & [chrome/chromium](https://chromedriver.chromium.org/downloads)
- Unzip or untar the executable and place in selenium_drivers dir.

## Executing Script

- Write all your test cases into test.yaml and execute

```console
> wtrobot
or 
python3 -m wtrobot
```

> NOTE

- On initial run script will ask you for few configuration question and create config.json file.

## Syntax of test.yaml file

- Write your WTRobot test cases in test.yaml files
  - [detailed syntax](https://raw.githubusercontent.com/wtrobot/wtrobot/main/examples/syntax_docs.rst)
  - [example](https://raw.githubusercontent.com/wtrobot/wtrobot/main/examples/test.yaml)

- Scenario and name are just detailed text description about your test case scenario and steps, they are useful for detailed logging
- There are only three important section to be considered while writing this script file
  - action: what to perform (e.g. click, input and etc)
  - target: on what to perform (e.g. Text widget on web page, xpath of widget and etc)
  - value: with what data (e.g. if an input field then what value to input)

## License

This application is licensed under the MIT License.
Please read file [LICENSE](LICENSE) for details.

## Credits

Please read file [CONTRIBUTORS](CONTRIBUTORS.md) for list of contributors.

### *Happy Testing :)*
