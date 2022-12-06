.. _Getting_Started:

Getting Started 
###############

.. contents::

WTRobot is no-code test automation framework.
It uses some powerful python libraries like selenium, requests, unittest, etc to create this magic.


How to install
**************

See the :doc:`setup_and_config` for more details.

User Command
************
WTRobot has two sub commands run & clean

.. code-block::
    :caption: Run the test suite
    
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


.. code-block::
    :caption: Clean the tmp dir and old logs

    $ wtrobot clean --help
    Usage: wtrobot clean [OPTIONS]

    clean tmp dir and/or log file.

    Options:
    -t, --tmp  clean tmp dir
    -l, --log  clean entire log file
    --help     Show this message and exit.


How to write your first test
****************************

See the :doc:`test_syntax` for more details.

How to contribute
*****************

Any opensource contribution to this project is most welcomed :)

See the :doc:`dev_guidelines` for more project details.


Happy Testing :)
