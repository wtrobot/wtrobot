from re import A
import sys
import click
from lib.utils.util import Utils
from lib.wt_lib.commad_parser import commmandParser
import os
import logging
from lib.utils.logger import LogGen

@click.command()
@click.option('-s','--no-screenshot',default=False,is_flag=True,help="If you don't need screenshots to be captured")
@click.option('-l','--no-log',default=False,is_flag=True,help="If you don't need logging")
@click.option('-b','--browser',default=False,help="browser on which you want to run tests")
@click.option('-d','--web-driver-path',default=False,help="selenium webdriver path")
@click.option('-L','--locale',default=False,help="browser local in which you want to run tests")
@click.option('-t','--test-dir-path',default='tests',help="test dir path")
@click.option('-e','--entry-test-script',default='test.yaml',help="entry test script file")
@click.option('-D','--dev',default=False,is_flag=True,help="dev logging enable")
@click.option('-c','--config-file-path',default="config.json",help="config file path")
def cli(no_screenshot, no_log, browser, web_driver_path, locale, test_dir_path, entry_test_script, dev, config_file_path):
    '''
    run all wtrobot testsuit.
    It will also take screenshot and log every step. 
    '''
    arg_exclude=('no_screenshot','no_log')
    
    # check if tests dir and entry test script exist
    test_dir_path = Utils.get_abs_filepath(test_dir_path)
    if not os.path.isdir(test_dir_path):
        testfile= os.path.join(test_dir_path, entry_test_script)
        if not os.path.isfile(entry_test_script):
            print("invalid test dir path or entry test script path given.")
            sys.exit(1)

    # check if given config file exist if not then create one.
    if not os.path.isfile(config_file_path):
        open(config_file_path, 'a').close()

    global_conf = Utils.json_load(config_file_path) #load config.json file into dict
    function_args = locals().keys()  #get all arguments passed to current function
    for arg in list(function_args):
        '''
        check if arguments is
        - not in exclude list
        - is false
        - not in config file
        then ask user to enter input
        '''
        if (arg not in arg_exclude) and ( locals().get(arg) is False) and global_conf.get(arg) == None:
            global_conf[arg] = input("Input "+arg+" :")
        elif locals().get(arg):
            global_conf[arg] = locals().get(arg)
    
    for arg in arg_exclude:
        '''
        add exclude list args into global config dict
        '''
        global_conf[arg] = locals().get(arg)
    
    # init logging
    LogGen.loggen(global_conf['log'], global_conf['dev'])
    logging.info("---------- new run -----------")

    # init commandParser and pass global config
    commmandParser(global_conf)
    # print(global_conf)
    # util.json_dump(config_file_path, global_conf)