#coding=utf-8
import os
import os.path
import xlrd
import json
import shutil
import yaml
from rtool import utils
from rtool.tasks import BasePreAction
from rtool.projects.demos.extraCfg import genExtraConfigs as GEC
from rtool.tasks import parse_config_files as pcfg
from rtool.tasks import action_dispatch as ad

logger = utils.getLogger('Task_Pre_Action_Config_Parse')
dec_options = {}

class PresActionConfigParse(BasePreAction.BasePreAction):
	"""PresActionConfigParse封装了在框架中Actions执行之前需要做的操作，主要负责处理额外的配置解析"""
	def __init__(self, options):
		super(PresActionConfigParse, self).__init__(options)
		dec_options = options
	
	# @BasePreAction.preProcess(options = dec_options)
	def go(self):
		# 有额外的配置信息需要添加至extraCfg中使用以下代码
		if not pcfg.task_settings.has_key('extraCfg'):
			pcfg.task_settings['extraCfg'] = {}		
		# GEC.genExtraCfgs(pcfg.task_settings['extraCfg'])
		# 框架自身需要的前处理操作
		BasePreAction.pre_process(self.options)
		return True		                    
		pass