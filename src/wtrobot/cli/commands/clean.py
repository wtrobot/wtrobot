import click
import os
import glob
import shutil

@click.command()
@click.option('-a','--all-runs',default=False,is_flag=True, help="clean all results")
@click.option('-l','--last-run',default=False,is_flag=True,help="clean last result")
@click.option('-r','--run',default=None, help="clean specific run result")
def cli(all_runs,last_run,run):
    '''
    Clean tmp dir and/or log file.
    ''' 

    if all_runs:
        if os.path.exists("./results"):
            shutil.rmtree("./results")
        else:
            print("There are not results to delete")
    elif last_run:
        if os.path.exists("./results/new"):
            shutil.rmtree("./results/new")
        else:
            print("There are no lastest results to delete")
    elif run:
        if os.path.exists("./results/{}".format(run)):
            shutil.rmtree("./results/{}".format(run))
        else:
            print("Specified result dir doesnot exist")
    else:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()
