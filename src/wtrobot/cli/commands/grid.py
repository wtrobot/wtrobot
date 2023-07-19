import click
import os
import subprocess
from wtrobot.wt_lib.scripts import grid

@click.command()
@click.option('-s','--start',default=False,is_flag=True, help="start selenium standalone grid")
@click.option('-t','--stop',default=False,is_flag=True,help="stop selenium standalone grid")
@click.option('-r','--remove',default=False,is_flag=True,help="remove selenium standalone grid")
@click.option('-S','--status',default=False,is_flag=True,help="status selenium standalone grid")
def cli(start,stop,remove,status):
    '''
    Manage selenium standalone grid container
    '''
    function_args = locals().keys()  #get all arguments passed to current function
    if True in locals().values():
        for arg in list(function_args):
            if locals().get(arg) is True:
                grid(arg)
    else:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()