import click
import os
from wtrobot.utils.util import Utils

@click.command()
@click.option('-d','--display',default=False,is_flag=True,help="Display all the default config from the config file")
@click.option('-e','--edit',help="Display all the default config from the config file")
def cli(display,edit):
    '''
    Manage defult configuration
    '''
    
    if display:
        global_conf = Utils.json_load("./config.json") #load config.json file into dict
        for conf, value in global_conf.items():
            print("{} = {}".format(conf,value))
    elif edit:
        global_conf = Utils.json_load("./config.json") #load config.json file into dict
        key,val = edit.split("=")
        global_conf[key] = val
        Utils.json_dump(filename="./config.json",data=global_conf)
    else:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()