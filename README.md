<a href="http://wtrobot.rtfd.io"><img alt="downloads" src ="https://img.shields.io/badge/WTRobot-025E8C?style=for-the-badge&logoColor=white"></a>  <a href="https://pypi.org/project/wtrobot"><img alt="downloads" src="https://img.shields.io/pypi/v/wtrobot?style=for-the-badge&color=green" target="_blank" /></a>

## Introduction

The web automation framework inspired from [behave](https://behave.readthedocs.io/en/latest) and [robot](https://robotframework.org) framework. Its an No-Code testing framework.

[Learn more](https://wtrobot.readthedocs.io/en/latest/getting_started.html)

## Setup

### Install

```console
$ pip install wtrobot
```

> NOTE

- Selenium_drivers folders have your selenium webdrivers geckodrivers(for firefox) and chromedrivers(for chrome and chromium)
- If script fails due to drivers issue, you need to find appropriate selenium webdriver according to your browser version
  - [firefox](https://github.com/mozilla/geckodriver/releases) & [chrome/chromium](https://chromedriver.chromium.org/downloads)
- Unzip or untar the executable and place in selenium_drivers dir.

### Package Maintainers Guide
1. Install all dependencies to build & push package to pypi
```console
$ pip install -r dev-requirements.txt
``` 
also install `make`
> NOTE: password less login to pypi creare .pypirc as mentioned in https://packaging.python.org/en/latest/specifications/pypirc/ 

2. Build & Push to pypi
```console
$ make build-push     (default push to pypi repo) 
$ make build-push PUSH_TO=testpypi      (one can specify where to push package)
```
## Executing Script

- Write all your test cases into test.yaml and execute

```console
$ wtrobot
```

> NOTE : On initial run script will ask you for few configuration question and create config.json file.

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
