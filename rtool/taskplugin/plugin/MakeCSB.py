#coding=utf-8
# 使用CCSUIExporter将csd转化为csb
import yaml
import os
import os.path
import shutil
import json
import subprocess
import sys
import re
sys.path.append(os.path.split(os.path.realpath(__file__))[0])
import rtool.taskplugin.plugin.MultiProcessRunner as MultiProcessRunner
import rtool.utils as utils


logger = utils.getLogger('MakeCSBAction')

def run():
	logger.debug("MakeCSBAction")
	pass

def run_with_configs(configs,tp=None):
	logger.debug("Executing MakeCSBAction")
	apaction = MakeCSBAction()
	apaction.go(configs)
	pass

def clean_output(configs):
	default_output_path = configs["output-root"]
	
	pass

class MakeCSBAction:
	"""使用CCSUIExporter将csd转化为csb"""

	def go(self,config):

		opt = config['options']
		# print config

		texture_prefix = opt['texture_prefix']
		texture_type = opt['texture_type']
		csb_prefix = opt['csb_prefix']
		font_prefix = opt['font_prefix']
		output_root = os.path.join(config['outputroot'])
		if not os.path.exists(output_root):
			os.makedirs(output_root)

		CCSUIExporter_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'standalone','CocosStudioExporter','bin')
		CCSUIExporter_path = CCSUIExporter_dir+os.path.sep+'CCSUIExporter'
		# print CCSUIExporter_path
		command_template = CCSUIExporter_path+" --texture-prefix $texture-prefix --texture-type $texture-type --csb-prefix $csb-prefix --font-prefix $font-prefix --output $output $input"

		for input_path in config['input']:

			csd_dir,csd_name = os.path.split(input_path)
			name,ext = os.path.splitext(csd_name)
			csb_name = name+'.csb'
			output_path = os.path.join(output_root,csb_name)

			if os.path.exists(input_path):
				args = []
				args.append(CCSUIExporter_path)
				if not texture_prefix =='':
					args.extend(['--texture-prefix',texture_prefix])
				if not texture_type =='':
					args.extend(['--texture-type',texture_type])
				if not csb_prefix =='':
					args.extend(['--csb-prefix',csb_prefix])
				if not font_prefix =='':
					args.extend(['--font-prefix',font_prefix])
				args.extend(['--output',output_path,input_path])

				showExporterOutputs = True
				p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
				outs = p.communicate()
				if p.returncode!=0:
					logger.error('由%s生成csb出错：\n%s' % (input_path, outs[0]))
					print(args)
					return False
				elif showExporterOutputs:
					placeholders = outs[0]
					if placeholders and re.search(r'\S', placeholders):
						logger.warning('CCSUIExporter输出：\n%s' % (placeholders,))
		
		pass