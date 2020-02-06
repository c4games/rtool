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

logger = utils.getLogger('CopyRes')

def run():
	logger.debug("CopyRes")
	pass

def run_with_configs(configs,tp=None):
	logger.debug("Executing NCopyRes")
	apaction = CopyResAction()
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

class CopyResAction:
	"""根据资源配置文件直接复制资源到目标目录"""
	
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

		ext_list = []
		input_list = config['input']
		if not config['options']['cpall']:
			if 'cpextlist' in config['options']:
				ext_list = config['options']['cpextlist'].split(',')
				for input_file_path in input_list:
					basedir,filename = os.path.split(input_file_path)
					name,fext = os.path.splitext(filename)
					for ext in ext_list:						
						if ext == fext:
							# 保留目录结构的为相对于配置项根目录的层级
							input_file_dir = os.path.dirname(input_file_path)
							dest_dir = os.path.join(config['outputroot'],os.path.relpath(input_file_dir,config['config-root']))
							dest_dir = config['output-root']
							# d_dir = config['output']
							if 'dst' in config['options']:
								d_dir = config['options']['dst']
								dest_dir = os.path.join(config['outputroot'],d_dir,os.path.relpath(input_file_dir,config['config-root']))
							if not os.path.exists(dest_dir):
								os.makedirs(dest_dir)
							logger.debug("[CopyRes]copy "+input_file_path+" to "+dest_dir)
							shutil.copy2(input_file_path,dest_dir)
			if 'filenames' in config['options']:
				filenames_list = config['options']['filenames'].split(',')
				for filename in filenames_list:
					for input_file_path in input_list:
						dirname,input_file_name = os.path.split(input_file_path)
						if filename==input_file_name:
							# 保留目录结构的为相对于配置项根目录的层级
							input_file_dir = os.path.dirname(input_file_path)
							dest_dir = os.path.join(config['outputroot'],os.path.relpath(input_file_dir,config['config-root']))
							dest_dir = config['output-root']
							# d_dir = config['output']
							if 'dst' in config['options']:
								d_dir = config['options']['dst']
								dest_dir = os.path.join(config['outputroot'],d_dir,os.path.relpath(input_file_dir,config['config-root']))
							if not os.path.exists(dest_dir):
								os.makedirs(dest_dir)
							logger.debug("[CopyRes]copy "+input_file_path+" to "+dest_dir)
							shutil.copy2(input_file_path,dest_dir)
		else:
			for input_file_path in input_list:
				# 保留目录结构的为相对于配置项根目录的层级
				input_file_dir = os.path.dirname(input_file_path)
				dest_dir = os.path.join(config['outputroot'],os.path.relpath(input_file_dir,config['config-root']))
				dest_dir = config['output-root']
				# d_dir = config['output']
				if 'dst' in config['options']:
					d_dir = config['options']['dst']
					dest_dir = os.path.join(config['outputroot'],d_dir,os.path.relpath(input_file_dir,config['config-root']))
				if not os.path.exists(dest_dir):
					os.makedirs(dest_dir)
				logger.debug("[CopyRes]copy "+input_file_path+" to "+dest_dir)
				shutil.copy2(input_file_path,dest_dir)
			pass
		pass