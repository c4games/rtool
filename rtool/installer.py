#coding=utf-8

import click
from rtool import utils
import os
import sys
import importlib

def run(cmd_name):
	project_name = utils.getMainConfig('project_name')
	self_dir = os.path.dirname(os.path.abspath(__file__))
	project_cmd_path = os.path.join(self_dir, 'projects', project_name, 'cmd_extend.py')
	project_cmd_dir = os.path.join(self_dir,'projects', project_name)
	print(project_cmd_path)
	# if os.path.exists(project_cmd_path):
	from rtool.projects.tkw import cmd_extend
	cmd_extend = importlib.import_module('rtool.projects.'+project_name+'.cmd_extend', package=None)
	if cmd_name == 'cfg':
		if project_name == "demos":
			cmd_extend.export_config_dev()
		else:
			cmd_extend.export_config()
		pass
	if cmd_name == 'checksame':
		if project_name == "demos":
			cmd_extend.check_same_filename()
		else:
			print("checksame is not implemented")