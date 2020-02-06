#coding=utf-8
import yaml
import os
import os.path
import shutil
import json
import subprocess
import sys
sys.path.append(os.path.split(os.path.realpath(__file__))[0])
import rtool.taskplugin.plugin.MultiProcessRunner as MultiProcessRunner
import rtool.utils as utils

logger = utils.getLogger('CSD2CSB')

def run():
	logger.debug("Executing CsdPublish")
	pass

def run_with_configs(configs,tp=None):
	logger.debug("Executing CsdPublish")
	# os.system('mtl ccs')
	apaction = CsdPublishAction()
	apaction.pack(configs)
	pass

def clean_output(configs):
	default_output_path = configs["output-root"]

	pass

class CsdPublishAction:
	"""根据资源配置文件发布ccb"""
	
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

	def pack(self,config):

		cocos_tool_path = "/Applications/Cocos/Cocos\ Studio\ 2.app/Contents/MacOS/Cocos.Tool"
		ccs_input = ' '.join(config['input'])
		ccs_output = config['output-root']
		ccs_options = ' '.join(list(config['options'].keys()))

		ccs_command_template = "$cocos_tool_path publish $options -f $input -o $output"

		ccs_command = ccs_command_template
		ccs_command = ccs_command.replace('$cocos_tool_path',cocos_tool_path)
		ccs_command = ccs_command.replace('$options',ccs_options)
		ccs_command = ccs_command.replace('$input',ccs_input)
		ccs_command = ccs_command.replace('$output',ccs_output)
		logger.debug(ccs_command)
		os.system(ccs_command)

		pass