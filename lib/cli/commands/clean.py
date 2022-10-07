import click
import os
import glob

@click.command()
@click.option('-t','--tmp',default=False,is_flag=True, help="clean tmp dir")
@click.option('-l','--log',default=False,is_flag=True,help="clean entire log file")
def cli(tmp,log):
    '''
    clean tmp dir and/or log file.
    '''
    if not tmp and not log:
        print("invalid command check --help")
    if tmp:
        files = glob.glob('tmp/*')
        for f in files:
            os.remove(f)
    if log:
        open("wtlog.log", "w").close()
