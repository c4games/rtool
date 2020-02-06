#coding=utf-8
import rtool.utils
from Base import Base
from BaseParseConfigs import BaseParseConfigs
from BaseParseConfigs import global_cfg_dict
from BaseActionDispatch import BaseActionDispatch
from BaseLocalChange import BaseLocalChange
from BaseConfigCollect import BaseConfigCollect
from BaseLocalChange import BaseLocalChange
from time import time
import rtool.utils as mut
import os
import os.path
import json

class BaseParse(Base):
	"""docstring for BaseParse"""
	def __init__(self, options):
		super(BaseParse, self).__init__(options)
		self.bpc = BaseParseConfigs()
		self.bpc.gen_all_white_dict(options)
		self.bpc.parseConfig(self.cache_dir,options)
		self.bd = BaseActionDispatch()
		pwd = os.path.dirname(os.path.abspath(__file__))
		root,_ = os.path.split(pwd)
		project_name = options['game']
		procfgdir = os.path.join(root,'projects',project_name,'taskplugin')
		mtlcfgdir = os.path.join(root,'taskplugin','plugin')
		plugindir = [procfgdir,mtlcfgdir]
		self.bd.set_plugin_dir(plugindir)
		self.run_cfg_dict = {}

	def parseResHash(self,res_yaml_hash,global_cfg_dict):
		for dir_path,info in res_yaml_hash.items():
			if info == 'renew':
				print "renew "+dir_path
				self.renew_from_parent_yaml(dir_path,global_cfg_dict)
			elif info == 'stored':
				print "stored "+dir_path
				self.use_stored_res_result(dir_path,global_cfg_dict)
			elif info == 'deleted':
				print "deleted "+dir_path
				self.delete_dir_from_RC(dir_path,global_cfg_dict)
			else:
				# use new cfg to run res over by default
				self.renew_from_parent_yaml(dir_path,global_cfg_dict)
				# print "using yaml "+info
		pass

	def renew_from_parent_yaml(self,dir_path,global_cfg_dict):
		cfg_item = global_cfg_dict.get(dir_path,None)
		if cfg_item:
			cfg_item['run_state'] = "renew"
			self.run_cfg_dict[dir_path] = cfg_item
		pass

	def use_stored_res_result(self,dir_path,global_cfg_dict):
		cfg_item = global_cfg_dict.get(dir_path,None)
		if cfg_item:
			cfg_item['run_state'] = "stored"
			self.run_cfg_dict[dir_path] = cfg_item
		pass 

	def delete_dir_from_RC(self,dir_path,global_cfg_dict):
		cfg_item = global_cfg_dict.get(dir_path,None)
		if cfg_item:
			cfg_item['run_state'] = "deleted"
			self.run_cfg_dict[dir_path] = cfg_item
		pass

	def get_run_cfg_dict(self):
		return self.run_cfg_dict


if __name__ == '__main__':
	options={}
	options['path']=''
	options['input']=''
	options['output']=''
	options['cachedir']=''
	options['game']=''
	input_root = mut.getProjectConfig('input_root')
	rtool_root = mut.getProjectConfig('rtool_root')
	output_root = mut.getProjectConfig('output_root')
	cache_dir = mut.getProjectConfig('cache_dir')
	if options['path'] == '':
	    options['path'] = rtool_root
	if options['input'] == '':
	    options['input'] = os.path.join(input_root)
	if options['output'] == '':
	    options['output'] = os.path.join(output_root)
	if options['cachedir'] =='':
	    options['cachedir'] = cache_dir
	if options['game'] == '':
	    options['game'] = mut.getMainConfig('project_name')
	options['target']='iOS'
	print options.get("input","")

	bpc = BaseParseConfigs(options)
	bpc.gen_all_white_dict(options)

	bpc.parseConfig(options.get("input",""),options)
	bd = BaseActionDispatch()
	pwd = os.path.dirname(os.path.abspath(__file__))
	root,_ = os.path.split(pwd)
	project_name = options['game']
	procfgdir = os.path.join(root,'projects',project_name,'taskplugin')
	mtlcfgdir = os.path.join(root,'taskplugin','plugin')
	plugindir = [procfgdir,mtlcfgdir]
	bd.set_plugin_dir(plugindir)
	# blc = BaseLocalChange(options)
	# blc.getAllFilesAsAdded(options['input'])
	# res_diff_dict = blc.getResDiffDict()
	# yaml_diff_dict = blc.getYamlDiffDict()
	# bcc = BaseConfigCollect(options)
	# res_yaml_hash = bcc.genResYamlHash(yaml_diff_dict,res_diff_dict)

	# bp = BaseParse(options)
	# bp.parseResHash(res_yaml_hash,global_cfg_dict)
	# print bp.get_run_cfg_dict()

	with open(os.path.join("/Users/playcrab/Desktop/",'global_cfg_dict.json'),'w') as f:
		f.write(json.dumps(global_cfg_dict,indent=4))
	for item in global_cfg_dict.items():
		if item[1].has_key(options['target']):
			for action in item[1][options['target']].keys():
				config = bpc.translate_config_item(item,options['target'],action,options)
				if not config == {}:
					# print json.dumps(config,indent=4)
					pass

				

		


		 
		
