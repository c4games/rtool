#coding=utf-8

import click
import sys

CONTEXT_SETTINGS = dict(auto_envvar_prefix='RESLIB',help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
def main(**options):
    """rtool 工具集"""
    print(sys.version)
    print(sys.version_info)
    pass

from rtool import utils
import os
import sys
import importlib


# import project's cmd_extend
project_name = utils.getMainConfig('project_name')
self_dir = os.path.dirname(os.path.abspath(__file__))
project_cmd_path = os.path.join(self_dir, 'projects', project_name, 'cmd_extend.py')
if os.path.exists(project_cmd_path):
    cmd_extend = importlib.import_module('rtool.projects.'+project_name+'.cmd_extend', package=None)
    cmd_extend.run(main)


if __name__ == '__main__':
    main()
