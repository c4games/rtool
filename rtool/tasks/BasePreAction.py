#coding=utf-8
import os
import os.path
import json
import shutil
import yaml
from .. import utils
from rtool.tasks.Base import Base
from rtool.tasks.BaseLocalChange import BaseLocalChange
from functools import wraps

idle_name_list = []

logger = utils.getLogger('Task_Pre_Action_Config_Parse')

class BasePreAction(Base):
	"""针对不同项目实现parseCustom方法，生成额外配置"""
	def __init__(self, options):
		super(BasePreAction, self).__init__(options)

	def parseCustom(self):

		pass

	def run(self):
		pass
