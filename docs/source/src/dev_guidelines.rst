.. _DevGuidelines:

Developer Guidelines
####################

.. contents::

Setup
*****

.. code-block::
    :caption: setup a virtual environment 

    $ pip install virtualenv
    $ virtualenv venv
    $ activate venv/bin/activate

.. code-block::
    :caption: clone repo and install

    $ git clone <repo url>
    $ cd <project dir>
    $ pip install -e .

Project Structure
*****************

Our WTRobot library lives in :code:`lib` dir.

.. code-block::

    lib/
    ├── cli/                  // all click based file are here
    │   ├── commands/         // if you want to add any new subcommand just add a new file here   
    │   │   ├── clean.py
    │   │   └── run.py
    │   |── main.py
    |
    ├── utils/               // All utility scripts are here 
    │   ├── logger.py        // project logger script
    │   └── util.py          // simple utility scripts like File I/O, etc
    |
    └── wt_lib/              // WTRobot core lib files    
        ├── action.py        // takes care of all selenium actions like click, input, etc
        ├── brower_init/     // initialize browser instance 
        │   ├── browser_options.py      // set brower options like locale, etc
        │   ├── grid_init.py            // config if you are using selenium grid    
        |   ├── init.py                 // brower init, this also uses weddriver_manager 
        |
        ├── commad_parser.py            // parser your test.yaml file
        ├── operations.py               // xpath parser, locate elements, etc
        |

Pull Requests
*************

:code:`Dev` is the Development branch and contributors are requested to raise PR against dev branch only.
