#coding=utf-8
# 最简示例，用于展示action插件的编写方法
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

logger = utils.getLogger('SampleAction')

def run():
	logger.debug("SampleAction")
	pass

def run_with_configs(configs,tp=None):
	logger.debug("Executing SampleAction")
	apaction = SampleAction()
	apaction.go(configs)
	pass

def clean_output(configs):
	default_output_path = configs["output-root"]
	
	pass

class SampleAction:
	"""示例"""
	


	def go(self,config):

		opt = config['options']['opt']

		logger.debug("Opt is "+opt+" configs:")
		print config
		
		pass