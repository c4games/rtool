#coding=utf-8
import yaml
import logging
from rtool import utils
import click
import rtool.utils as mut
import os
import os.path
import sys
import json
import copy
import shutil
import plistlib as pl
import rtool.pcutils.md5sum_of_path as mput
from xml.etree import ElementTree
from rtool.tasks import BasePostAction
from rtool.tasks import parse_config_files as pcfg

logger = utils.getLogger('Task_post_action')


class PostActionConfigParse(BasePostAction.BasePostAction):
	"""docstring for PostActionConfigParse"""
	cls_options = None
	cls_recorder = None
	def __init__(self, options,action_recorder):
		super(PostActionConfigParse, self).__init__(options)
		self.action_recorder = action_recorder

	def getPlistForSourceName(self,index_dict,sourceName):
		for plist in index_dict['indices'].keys():
			if sourceName in index_dict['indices'][plist]['items']:
				return plist
		return None

	# @BasePostAction.postProcess(options=cls_options,action_recorder=cls_recorder)
	def go(self):
		BasePostAction.post_process(self.options,self.action_recorder)
		# output_dir = self.options['output']
		# index_path = os.path.join(output_dir,'asset','index.json')
		# ainm_path = os.path.join(output_dir,'asset','anim')
		# index_dict = {}
		# with open(index_path) as f:
		# 	index_dict = json.load(f)
		# plist_to_del = []
		# for file_name in os.listdir(ainm_path):
		# 	if ".mclib" in file_name:
		# 		mclib = {}
		# 		file_path = os.path.join(ainm_path,file_name)
		# 		with open(file_path) as f:
		# 			mclib = json.load(f)
		# 		mclib['textures']=[]

		# 		for key in mclib['libItemDict'].keys():
		# 			if mclib['libItemDict'][key].has_key('sourceName'):
		# 				sourceName = mclib['libItemDict'][key]['sourceName']
		# 				if not sourceName == "":
		# 					plist_name = self.getPlistForSourceName(index_dict,sourceName)
		# 					if plist_name and not plist_name in mclib['textures']:
		# 						mclib['textures'].append(plist_name)
		# 						plist_to_del.append(plist_name)
		# 		with open(file_path,'w') as f:
		# 			f.write(json.dumps(mclib,indent=2))
		# plist_to_del = list(set(plist_to_del))
		# for plist in plist_to_del:
		# 	del index_dict['indices'][plist]
		# 	logger.debug("Deleting index for "+plist)
		# with open(index_path,'w') as f:
		# 	f.write(json.dumps(index_dict,indent=2))

		return True
		pass
