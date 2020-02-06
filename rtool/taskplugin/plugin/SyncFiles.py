#coding=utf-8
#coding=utf-8
import yaml
import os
import os.path
import shutil
import json
import subprocess
import sys
sys.path.append(os.path.split(os.path.realpath(__file__))[0])
import MultiProcessRunner
import rtool.utils as utils

logger = utils.getLogger('SyncFilesAction')

def run():
	logger.debug("SyncFilesAction")
	pass

def run_with_configs(configs,tp=None):
	logger.debug("Executing SyncFilesAction")
	apaction = SyncFilesAction()
	apaction.go(configs)
	pass

def safeRemoveDir(dir_path):
	if os.path.exists(dir_path):
		shutil.rmtree(dir_path)
	pass

def clean_output(configs):
	default_output_path = configs["output-root"]
	safeRemoveDir(default_output_path)
	pass

class SyncFilesAction:
	"""同步资源目录"""
	
	default_option = None

	res_root = None
	packing_root = None
	ignore_list=[]

	def setResRoot(self,root):
		self.res_root = root
		pass
	def setPackingRoot(self,root):
		self.packing_root = root
		pass
	def setDefaultOption(self,option):
		self.default_option = option
		pass

	def go(self,config):
		
		if not os.path.exists(config['outputroot']):
			os.makedirs(config['outputroot'])

		output = os.path.join(config['outputroot'],config['output'])
		source = os.path.join(config['inputroot'],''.join(config['input-dir']))
		if os.path.isdir(source):
		    source = source+os.path.sep
		cmdParams = []
		cmdParams.append('rsync')
		cmdParams.append('-rLptgoD')
		cmdParams.append('--exclude')
		cmdParams.append('.*')
		cmdParams.append(source)
		cmdParams.append(output)
		p = subprocess.Popen(cmdParams,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		returntuple = p.communicate()
		stdoutdata = returntuple[0]
		stderrdata = returntuple[1]
		if p.returncode != 0:
		    logger.error(stderrdata)
		    return False

		pass