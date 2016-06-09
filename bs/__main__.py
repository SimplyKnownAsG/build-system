import sys

import click
import sys

import bs
from bs.config import load as load_config
from bs import logger

command = sys.argv[1] if len(sys.argv) >= 2 else 'build'


@click.group(name='bs')
def cli():
    '''
    BUILD SYSTEM

    an extraordinarily dumb build tool.
    '''
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
            logger.info('  copy {} -> {}'.format(src, dest))
            shutil.copy(src, dest)


@cli.command()
@click.option('-l', '--list', is_flag=True, help='list configuration items')
def config(list_):
    '''Edit or intiialize the local configration'''
    bs.cd_root()
    load_config()
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
    bs.cd_root()
    load_config()
    bs.BUILD = True
    exec(compile(open(bs.TARGETS_FILE).read(), bs.TARGETS_FILE, 'exec'))


@cli.command()
@click.option('--flatten', '-F',
        help='Also list flattened objectives (ignores the absence of --all)',
        is_flag=True)
@click.option('--graph', '-g',
        help='graph known objectives, excluding object files, and exit',
        is_flag=True)
@click.option('--all', '-a',
        help='show all objectives',
        is_flag=True)
def list(flatten, graph, all):
    '''build whatever build-system knows about'''
    bs.cd_root()
    load_config()
    bs.LIST = True
    exec(compile(open(bs.TARGETS_FILE).read(), bs.TARGETS_FILE, 'exec'))


@cli.command()
@click.option('--dry-run', '-n',
        help="don't actually delete anything, just echo'",
        is_flag=True)
def clean(dry_run):
    '''clean all output files'''
    load_config()
    bs.cd_root()
    bs.CLEAN = True
    exec(compile(open(bs.TARGETS_FILE).read(), bs.TARGETS_FILE, 'exec'))

cli(prog_name='bs', args=['build'] if len(sys.argv) == 1 else sys.argv[1:])

