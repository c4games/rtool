#coding=utf-8

import click
import sys
import os
import os.path
from rtool import utils
from rtool.pcutils import cache_tool

# from tkinter import *
# from tkinter.filedialog import askdirectory
logger = utils.getLogger('Demo')

def run(click_group):
    from rtool.tasks import task
    click_group.add_command(task.run_dev,name='task_dev')
    click_group.add_command(task.run,name='task')
