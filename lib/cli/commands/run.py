from re import A
import click
from lib.utils import util
from lib.wt_lib.commad_parser import commmandParser
from lib.utils.logger import logger_init

@click.command()
@click.option('-s','--no-screenshot',default=False,is_flag=True,help="If you don't need screenshots to be captured")
@click.option('-l','--no-log',default=False,is_flag=True,help="If you don't need logging")
@click.option('-b','--browser',default=False,help="browser on which you want to run tests")
@click.option('-d','--web-driver-path',default=False,help="selenium webdriver path")
@click.option('-L','--locale',default=False,help="browser local in which you want to run tests")
@click.option('-t','--test-script-path',default=False,help="test script file path")
@click.option('-D','--dev',default=False,is_flag=True,help="dev logging enable")

def cli(no_screenshot, no_log, browser, web_driver_path, locale, test_script_path, dev):
    '''
    run all wtrobot testsuit.
    It will also take screenshot and log every step. 
    '''
    arg_exclude=('no_screenshot','no_log')
    global_conf = util.json_load() #load config.json file into dict
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
    
    logger_init(global_conf['log'], global_conf['dev'])
    obj = commmandParser(global_conf)