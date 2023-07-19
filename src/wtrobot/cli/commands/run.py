from re import A
import sys
import click
from wtrobot.utils import Utils
from wtrobot.wt_lib.testfile_parser import Parser
import os
import logging
from wtrobot.utils import LogGen
import datetime

@click.command()
@click.option('-s','--no-screenshot', default=False, is_flag=True, help="If you don't need screenshots to be captured")
@click.option('-l','--no-log', default=False,is_flag=True, help="If you don't need logging")
@click.option('-b','--browser', default='firefox', help="browser on which you want to run tests")
@click.option('-g','--selenium-grid', default=False, is_flag=True, help="Run tests on standalone selenium grid")
@click.option('-i','--selenium-grid-ip', default='http://localhost:4444/wd/hub', help="Specify selenium grid IP")
@click.option('-w','--web-driver-manager', default=False, is_flag=True, help="use webdriver manager insted of local selenium webdriver")
@click.option('-d','--web-driver-path', help="selenium webdriver path or set value to 'local' to use syspath drivers")
@click.option('-L','--locale', default="en", help="browser locale in which you want to run tests")
@click.option('-t','--test-dir-path', default='tests', help="test dir path")
@click.option('-e','--entry-test-script', default='test.yaml', help="entry test script file")
@click.option('-D','--dev', default=False, is_flag=True, help="dev logging enable")
@click.option('-c','--config-file-path', default="config.json", help="config file path")
@click.option('-f','--browser-fullscreen', default=False, is_flag=True, help="Set your browser window to fullscreen mode else it will only maximize")
@click.option('-r','--results-dir', default='./results', help="dir store your wtlogs and screenshot")
def cli(no_screenshot, no_log, browser, selenium_grid, selenium_grid_ip, web_driver_manager, web_driver_path, locale, test_dir_path, entry_test_script, dev, config_file_path, browser_fullscreen, results_dir):
    '''
    Run all wtrobot testsuit.
    It will also take screenshot and log every step. 
    '''
    # keywords to terminate testrun
    wt_exit_keywords = ["quit","close","exit","end"]

    # arg_exclude=('no_screenshot','no_log')
    arg_exclude=["global_conf","wt_exit_keywords","arg_exclude"]

    # check if tests dir and entry test script exist
    test_dir_path = Utils.get_abs_filepath(test_dir_path)
    if not os.path.isdir(test_dir_path):
        testfile= os.path.join(test_dir_path, entry_test_script)
        if not os.path.isfile(entry_test_script):
            print("Invalid test dir path => '{0}' or entry test script path => '{1}' given.".format(test_dir_path, entry_test_script))
            sys.exit(1)

    # check if given config file exist if not then create one.
    if not os.path.isfile(config_file_path):
        open(config_file_path, 'a').close()

    global_conf = Utils.json_load(config_file_path) #load config.json file into dict
    function_args = locals().keys()  #get all arguments passed to current function
    
    # print(function_args)
    
    for arg in list(function_args):
        '''
        check if arguments is
        - not in exclude list
        - is false
        - also not in config file
        then ask user to enter input
        '''
        
        # print(arg+" : "+str(locals().get(arg)))
        
        if (arg not in arg_exclude):
            # print("\n"+arg, locals().get(arg), end=" ")
            if ( locals().get(arg) is None) and global_conf.get(arg) == None:
                
                # check if arg is web driver path and wdm is false then ask user to input else skip
                if web_driver_manager is True and arg == "web_driver_path":
                    pass
                
                elif selenium_grid is True and arg == "web_driver_path":
                    pass

                # if selenium grid it true then ask for selenium grid ip
                elif selenium_grid and arg == "selenium_grid_ip":
                    global_conf[arg] = input("Input "+arg+" :")

                else:
                    # if user hits any exit keyword in input exit the test run
                    global_conf[arg] = input("Input "+arg+" :")
                    if global_conf[arg].lower() in wt_exit_keywords:
                        logging.error("Exit keyword found hence exiting test run")
                        sys.exit(1)

                    elif arg == "web_driver_path" and global_conf[arg].lower() != 'local':
                        while not Utils.check_file_exist(global_conf[arg]):
                            global_conf[arg] = input("Input "+arg+" :")
                            
                            # exit if any exit keyword entered
                            if global_conf[arg].lower() in wt_exit_keywords:
                                logging.error("Exit keyword found hence exiting test run")
                                sys.exit(1)
            else:
                global_conf[arg] = locals().get(arg)
    
    # Save global config to config.json file for next run
    Utils.json_dump(config_file_path, global_conf)

    # Get current timestamp and create a dir inside wtlogs dir to store current run logs and screenshots
    ctime = str(datetime.datetime.now())
    resultsdir_path = os.path.join(global_conf['results_dir'],"new")
    
    # rename 'new' dir i.e the old runs dir to its run timestamp  
    if os.path.exists(resultsdir_path):
        tmp_str = None
        with open(resultsdir_path+"/logs/wtlog.log","r") as fobj:
            tmp_str = fobj.readline()
        tmp_str = tmp_str.split("-")[1].strip().replace("/","-")
        os.rename(resultsdir_path, os.path.join(global_conf['results_dir'],tmp_str))

    # create result dirs 
    os.makedirs(resultsdir_path)
    os.makedirs(resultsdir_path+"/screenshots")
    os.makedirs(resultsdir_path+"/logs")
    
    global_conf["resultsdir_path"] = resultsdir_path

    # init logging
    LogGen.loggen(filename= resultsdir_path+"/logs/wtlog.log", dev=global_conf['dev'])
    logging.info("---------- Test Run @ {} -----------".format(ctime))

    # init Parser and pass global config
    Parser(global_conf)
    