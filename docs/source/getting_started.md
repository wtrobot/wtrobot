# Getting Started 

## How to install

See the [setup and config](setup_and_config.md) for more details.

## User Command

WTRobot has two sub commands run & clean

Run the test suite
    
    $ wtrobot run  --help
    Usage: wtrobot run [OPTIONS]

    run all wtrobot testsuit. It will also take screenshot and log every step.

    Options:
    -s, --no-screenshot            If you don't need screenshots to be captured
    -l, --no-log                   If you don't need logging
    -b, --browser BOOLEAN          browser on which you want to run tests
    -d, --web-driver-path BOOLEAN  selenium webdriver path
    -L, --locale BOOLEAN           browser local in which you want to run tests
    -t, --test-dir-path TEXT       test dir path
    -e, --entry-test-script TEXT   entry test script file
    -D, --dev                      dev logging enable
    -c, --config-file-path TEXT    config file path
    --help                         Show this message and exit.


Clean the tmp dir and old logs

    $ wtrobot clean --help
    Usage: wtrobot clean [OPTIONS]

    clean tmp dir and/or log file.

    Options:
    -t, --tmp  clean tmp dir
    -l, --log  clean entire log file
    --help     Show this message and exit.

## How to write your first test

See the [test syntax](test_syntax.md) for more details.

## How to contribute

Any opensource contribution to this project is most welcomed :)

See the [dev guidelines](dev_guidelines.md) for more project details.


Happy Testing :)
