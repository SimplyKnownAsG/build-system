
import click
import sys

import bs
from bs import config

command = sys.argv[1] if len(sys.argv) >= 2 else 'build'

# load the current user configuration
config.load()

@click.group(name='bs', help='build system')
def cli():
    pass

@cli.command()
def demo():
    '''Copy the demos into the current directory'''
    demo_root = os.path.join(os.path.dirname(__file__), 'demos')
    # shutil.copytree(demo_root, '.')
    for base, dirs, files in os.walk(demo_root):
        for ff in files:
            src = os.path.join(base, ff)
            dest = os.path.join(base.replace(demo_root, '.'), ff)
            if not os.path.exists(os.path.dirname(dest)):
                os.makedirs(os.path.dirname(dest))
            print('  copy {} -> {}'.format(src, dest))
            shutil.copy(src, dest)


@cli.command()
@click.option('-l', '--list', is_flag=True, help='list configuration items')
def config(list_):
    '''Edit or intiialize the local configration'''
    if args.list:
        config.print_config()
    else:
        config.save()

@cli.command()
@click.option('--debug', '-d',
        help='use the debug compiler (and configuration)',
        is_flag=True)
def build(debug):
    '''build whatever build-system knows about'''
    bs.BUILD = True
    exec(compile(open(bs.TARGETS_FILE).read(), bs.TARGETS_FILE, 'exec'))


@cli.command()
@click.option('--flatten', '-F',
        help='Also list flattened objectives (ignores the absence of --all)',
        is_flag=True)
@click.option('--list', '-l',
        help='list known objectives, excluding object files, and exit',
        is_flag=True)
@click.option('--graph', '-g',
        help='graph known objectives, excluding object files, and exit',
        is_flag=True)
@click.option('--all', '-a',
        help='modifies the behavior of list and graph to include all objectives',
        is_flag=True)
def list(flatten, graph, all_):
    '''build whatever build-system knows about'''
    bs.LIST = True
    exec(compile(open(bs.TARGETS_FILE).read(), bs.TARGETS_FILE, 'exec'))


@cli.command()
@click.option('--dry-run', '-n',
        help="don't actually delete anything, just echo'",
        is_flag=True)
def clean(dry_run):
    '''clean all output files'''
    bs.CLEAN = True
    exec(compile(open(bs.TARGETS_FILE).read(), bs.TARGETS_FILE, 'exec'))

cli(prog_name='bs')

