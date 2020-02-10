#coding:utf-8
import os
import os.path
import xlrd
import json
import shutil
from . import extraCfg
from rtool import utils

class GenDemoExtraCfg(extraCfg.ExtraCfg):
	"""docstring for GenDemoExtraCfg"""
	def __init__(self, arg):
		super(GenDemoExtraCfg, self).__init__(arg)
		self.arg = arg

	def genCfg(self,option):
		self.cfg = "Demo extra config"
		option[self.arg] = self.cfg
		pass
