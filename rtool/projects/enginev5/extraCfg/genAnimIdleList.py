#coding:utf-8
import os
import os.path
import xlrd
import json
import shutil
from . import extraCfg
from rtool import utils

logger = utils.getLogger('GenAnimIdleList')

class GenAnimIdleList(extraCfg.ExtraCfg):
	"""docstring for GenAnimIdleList"""
	def __init__(self, arg):
		super(GenAnimIdleList, self).__init__(arg)
		self.idle_name_list = []

	def getIdleNameList(self,input_file_name):
		xls_file = xlrd.open_workbook(input_file_name)
		input_table = xls_file.sheets()[0]
		for i in range(input_table.ncols):
			value = input_table.cell_value(1,i)
			if value == "pinyinID[string]":
				for j in range(2,input_table.nrows):
					self.idle_name_list.append(str(input_table.cell_value(j,i)))

		pass

	def getAllIdleName(self,item_config_path=''):
		if item_config_path =='':
			proj_root = utils.getMainConfig('project_root')
			if proj_root == None:
				item_config_path = utils.getMainConfig('config_input_path')
			else:
				item_config_path = os.path.join(proj_root,"svn","config")
		item_hero = os.path.join(item_config_path,"item.hero.xlsx")
		item_npc = os.path.join(item_config_path,"item.npc.xlsx")	
		self.getIdleNameList(item_hero)
		self.getIdleNameList(item_npc)
		pass

	def genCfg(self,option):
		anim_cfg_path = os.path.join(utils.getMainConfig('project_root'),'svn','config')
		logger.debug("Gen Anim Idle List From "+anim_cfg_path)
		self.getAllIdleName(anim_cfg_path)
		self.cfg = self.idle_name_list
		if not option.has_key(self.cfg_name):
			option[self.cfg_name] = []
		option[self.cfg_name] = self.cfg
		pass

