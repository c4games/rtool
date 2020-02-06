#coding=utf-8
# lixu 20180621
import yaml
import logging
# from .. import utils
import click
import rtool.utils as mut
import os
import os.path
import sys
import json
import copy
import plistlib as pl
from xml.etree import ElementTree
import rtool.pcutils.md5sum_of_path as mput
import shutil
import time
import rtool.tasks.BaseActionDispatch as BaseActionDispatch
from rtool.tasks.BaseLocalChange import BaseLocalChange
from rtool.tasks import BaseSync as BS
from time import time

global_cfg_dict ={}
task_settings ={}
white_dict = {}
# img_in_csd_list = []
# img_in_csd_dict = {}
old_global_cfg_dict ={}
ncfg_dict = {}
run_dict = {}


logger = mut.getLogger('Task_parse_config')

def modifyPathWithPattern(pattern,path_part,path):
	# print "modifyPathWithPattern" + pattern+ "  "+path_part
	# print path	
	if pattern in path:
		return path.replace(pattern,path_part)
	return path


class BaseParseConfigs(object):
	"""docstring for BaseParseConfigs"""
	def __init__(self,options):
		super(BaseParseConfigs, self).__init__()
		self._executeActionFunc = None
		self._options = options

	def parseGlobalConfig(self,filename,options):
		f = open(filename,'rb')
		configs = yaml.load(f)
		if 'input' in options and 'output' in options:
			# res_root = configs["resroot"].replace('$MYDIR',os.path.dirname(filename))
			# pack_cache_path=options['input']+'/temp'
			pack_cache_path = os.path.join(options['input'],'temp','pack')
			# compress_cache_path=options['input']+'/temp/compress/'+options['target']
			compress_cache_path = os.path.join(options['input'],'temp','compress',options['target'])
			if options['cachedir']:
				# pack_cache_path = options['cachedir']
				pack_cache_path = os.path.join(options['cachedir'],'pack')
				# compress_cache_path = options['cachedir']+'/compress/'+options['target']
				compress_cache_path = os.path.join(options['cachedir'],'compress',options['target'])
			res_root = options['input']		
			plugin_dir = configs["plugindir"].replace('$MYDIR',os.path.dirname(filename))
			configs["resroot"] = res_root
			configs["plugindir"] = plugin_dir 
			configs["actionbase"] = os.path.dirname(filename)
			input_root = options.get('input') 
			rtool_root = options.get('path')
			output_root = options.get('output') 
			cache_dir = options.get('cachedir')
			project_name = options.get('game','project_name')
			target = options.get('target','iOS')		    	
			for key in list(configs['taskdefs'].keys()):
				configs['taskdefs'][key]['input-root'] = modifyPathWithPattern('$input_root',input_root,configs['taskdefs'][key]['input-root'])
				configs['taskdefs'][key]['input-root'] = modifyPathWithPattern('$rtool_root',rtool_root,configs['taskdefs'][key]['input-root'])
				configs['taskdefs'][key]['input-root'] = modifyPathWithPattern('$output_root',output_root,configs['taskdefs'][key]['input-root'])
				configs['taskdefs'][key]['input-root'] = modifyPathWithPattern('$cache_dir',cache_dir,configs['taskdefs'][key]['input-root'])
				configs['taskdefs'][key]['input-root'] = modifyPathWithPattern('$project_name',project_name,configs['taskdefs'][key]['input-root'])
				configs['taskdefs'][key]['input-root'] = modifyPathWithPattern('$target',target,configs['taskdefs'][key]['input-root'])
				configs['taskdefs'][key]['output-root'] = modifyPathWithPattern('$input_root',input_root,configs['taskdefs'][key]['output-root'])
				configs['taskdefs'][key]['output-root'] = modifyPathWithPattern('$rtool_root',rtool_root,configs['taskdefs'][key]['output-root'])
				configs['taskdefs'][key]['output-root'] = modifyPathWithPattern('$output_root',output_root,configs['taskdefs'][key]['output-root'])
				configs['taskdefs'][key]['output-root'] = modifyPathWithPattern('$cache_dir',cache_dir,configs['taskdefs'][key]['output-root'])
				configs['taskdefs'][key]['output-root'] = modifyPathWithPattern('$project_name',project_name,configs['taskdefs'][key]['output-root'])
				configs['taskdefs'][key]['output-root'] = modifyPathWithPattern('$target',target,configs['taskdefs'][key]['output-root'])
			pass
		else:
			logger.error("输入或输出跟目录未配置，请检查config.xxx.yaml或命令行参数是否有误")
		for key in list(configs.keys()):
			if not key == 'taskdefs':
				task_settings[key] = configs[key]
		if 'taskdefs' not in task_settings:
			task_settings['taskdefs']={}
		for key in list(configs['taskdefs'].keys()):
			task_settings['taskdefs'][key] = configs['taskdefs'][key]
		f.close()
		pass

	def init_task_settings(root,options):
		mtlcfgdir = root+"/.rtool"
		if(os.path.exists(mtlcfgdir)):
		    self.parseConfig(mtlcfgdir+"/settings.yaml",options)
		else:
			logger.warning("[警 告] 未找到 .rtool 目录 "+mtlcfgdir)
		pass

	def registExecuteActionFunc(self,func):
		self._executeActionFunc = func

	def check_and_regist_ncfg(self,dir_path):
		if os.path.isdir(dir_path):
			for filename in os.listdir(dir_path):
				if '.ncfg.yaml' in filename:
					file_path = os.path.join(dir_path,filename)
					if dir_path not in ncfg_dict:
						ncfg_dict[dir_path] = []
					ncfg_dict[dir_path].append(file_path)
			self.inflate_config_for_cur_dir(dir_path)
		pass

	def regist_ncfg(self,dir_path,filename):
		file_path = os.path.join(dir_path,filename)
		if dir_path not in ncfg_dict:
			ncfg_dict['dir_path'] = []
		ncfg_dict[dir_path].append(file_path)
		self.inflate_config_for_cur_dir(dir_path)


	def add_config_for_parent_and_children(self,dir_path,action_dir_path,item,target,config_file_path):
		if action_dir_path not in global_cfg_dict:
			global_cfg_dict[action_dir_path] = {}
		if target not in global_cfg_dict[action_dir_path]:
			global_cfg_dict[action_dir_path][target]={}
		action = item['type']
		options = item['options']
		options = self.fill_default_options(action_dir_path,target,action,options)
		ignore_path_list=[]
		if 'ignore' in item:
			ignore_path_list = [os.path.join(action_dir_path,rpath) for rpath in item['ignore']]
		if action not in global_cfg_dict[action_dir_path][target]:
			global_cfg_dict[action_dir_path][target][action]={}
		global_cfg_dict[action_dir_path][target][action]['options']=options
		global_cfg_dict[action_dir_path][target][action]['config-root']=dir_path
		global_cfg_dict[action_dir_path][target][action]['config-file']=config_file_path
		for parent,dirnames,_, in os.walk(dir_path):
			dirnames[:] = [d for d in dirnames if mut.getRelPathWithOtherRoot(os.path.join(parent,d),dir_path,action_dir_path) not in ignore_path_list and '.svn' not in d]
			for dirname in dirnames:
				config_dir_path = os.path.join(parent,dirname)
				child_dir_path = ""
				if not config_dir_path == dir_path:
					# rel_path = config_dir_path.replace(dir_path+os.sep,"")
					rel_path = os.path.relpath(config_dir_path,dir_path)
					if sys.platform == 'win32':
						#rel_path = rel_path.decode('gbk')
						try:
							rel_path = rel_path.decode('gbk')
						except Exception:
							pass
						else:
							pass
					child_dir_path = os.path.join(action_dir_path,rel_path)
				else:
					child_dir_path = action_dir_path				
				if child_dir_path not in global_cfg_dict:
					global_cfg_dict[child_dir_path]={}
				if target not in global_cfg_dict[child_dir_path]:
					global_cfg_dict[child_dir_path][target]={}
				if action not in global_cfg_dict[child_dir_path][target]:
					global_cfg_dict[child_dir_path][target][action]={}
				global_cfg_dict[child_dir_path][target][action]['options']=options
				global_cfg_dict[child_dir_path][target][action]['config-root']=dir_path
				global_cfg_dict[child_dir_path][target][action]['config-file']=config_file_path 
		pass

	def add_config_for_one_dir(self,dir_path,item,target,config_root,config_file_path):
		if not os.path.exists(dir_path):
			return
		if dir_path not in global_cfg_dict:
			global_cfg_dict[dir_path] = {}
		if target not in global_cfg_dict[dir_path]:
			global_cfg_dict[dir_path][target]={}
		action = item['type']
		options = item['options']
		options = self.fill_default_options(dir_path,target,action,options)
		if action not in global_cfg_dict[dir_path][target]:
			global_cfg_dict[dir_path][target][action]={}
		global_cfg_dict[dir_path][target][action]['options']=options
		global_cfg_dict[dir_path][target][action]['config-root']=config_root
		global_cfg_dict[dir_path][target][action]['config-file']=config_file_path
		# print global_cfg_dict[dir_path]
		pass

	def add_config_for_multiple_dir(self,inputs,input_root,item,target,config_root,config_file_path):
		full_path_list = [os.path.join(config_root,path) for path in inputs]
		dir_path = full_path_list[0]
		if dir_path not in global_cfg_dict:
			global_cfg_dict[dir_path] = {}
		if target not in global_cfg_dict[dir_path]:
			global_cfg_dict[dir_path][target]={}
		action = item['type']
		options = item['options']
		options = self.fill_default_options(dir_path,target,action,options)
		if action not in global_cfg_dict[dir_path][target]:
			global_cfg_dict[dir_path][target][action]={}
		global_cfg_dict[dir_path][target][action]['options']=options
		global_cfg_dict[dir_path][target][action]['input_list'] = full_path_list
		global_cfg_dict[dir_path][target][action]['config-root'] = config_root
		global_cfg_dict[dir_path][target][action]['config-file'] = config_file_path
		# 父目录中配置对列表中目录生效的项目需要删除
		for path in full_path_list:
			if not path == dir_path:
				if path in global_cfg_dict:
					if target in global_cfg_dict[path]:
						if action in global_cfg_dict[path][target]:
							del global_cfg_dict[path][target][action]
							if len(list(global_cfg_dict[path][target].keys()))==0:
								del global_cfg_dict[path][target]
								if len(list(global_cfg_dict[path].keys()))==0:
									del global_cfg_dict[path]
		pass

	def fill_default_options(self,dir_path,target,action,cfg_options):
		if action in task_settings['taskdefs'] and target in task_settings['taskdefs'][action]['options']:
			default_options = task_settings['taskdefs'][action]['options'][target]
			for key,value in list(default_options.items()):
				if not key in list(cfg_options.keys()):
					cfg_options[key]=value
			# cfg_options = copy.deepcopy(task_settings['taskdefs'][action]['options'][target])
		else:
			logger.warning("Can not find options for action "+action+" with target "+target+"at "+dir_path)
			logger.warning("Try check your local cofnigs")
		return cfg_options

	def inflate_config_for_cur_dir(self,dir_path):
		if dir_path in ncfg_dict:
			global_input_root = self._options.get('input',"")
			if dir_path not in global_cfg_dict:
				# print "init "+dir_path
				# print ncfg_dict
				global_cfg_dict[dir_path]={}
			for file_path in ncfg_dict[dir_path]:
				configs=[]
				with open(file_path,'rb') as f:
					configs = list(yaml.load_all(f))
				for config in configs:
					target = config['target']
					items = config['items']
					for item in items:
						if item['type'] in task_settings['taskdefs']:
							inputs = item['input']
							input_root = task_settings['taskdefs'][item['type']]['input-root']
							if len(inputs) == 0:
								rel_dir = ""
								if not dir_path == global_input_root:
									# rel_dir = dir_path.replace(global_input_root+os.path.sep,'')
									rel_dir = os.path.relpath(dir_path,global_input_root)
									action_dir_path = os.path.join(input_root,rel_dir)
								else:
									action_dir_path = input_root								
								self.add_config_for_parent_and_children(dir_path,action_dir_path,item,target,file_path)
							elif len(inputs) == 1:
								relative_input = ''.join(inputs)
								input_dir_path = os.path.join(dir_path,relative_input)
								self.add_config_for_one_dir(input_dir_path,item,target,dir_path,file_path)
								#TO DO
							elif len(inputs) >1:
								#TO DO
								self.add_config_for_multiple_dir(inputs,input_root,item,target,dir_path,file_path)
		pass
	#TO DO:white list
	def gen_white_dict_for_single_dir(self,cur_dir):
		white_file_path = os.path.join(cur_dir,'.white')
		white_items={}
		if os.path.exists(white_file_path):
			with open(white_file_path,'rb') as f:
				white_items = yaml.load(f)
			for key in list(white_items.keys()):
				white_dict[key] = white_items[key]
		else:
			logger.debug("文件类型白名单未找到: "+white_file_path)
		pass

	def gen_all_white_dict(self,options):
		pwd = os.path.dirname(os.path.abspath(__file__))
		root,_ = os.path.split(pwd)
		project_name = options['game']
		procfgdir = os.path.join(root,'projects',project_name,'taskplugin')
		mtlcfgdir = os.path.join(root,'taskplugin')
		self.gen_white_dict_for_single_dir(mtlcfgdir)
		self.gen_white_dict_for_single_dir(procfgdir)
		# print json.dumps(white_dict,indent=4)

	def gen_input_file_list_for_single_dir(self,cur_dir,action):
		white_list=[]
		input_list=[]
		if action in white_dict:
			white_list = white_dict[action]
		for pattern in white_list:
			for filename in os.listdir(cur_dir):
				if(pattern[0]=='.' and os.path.splitext(filename)[1] == pattern) or pattern == filename or pattern == '*':
						if os.path.isfile(os.path.join(cur_dir,filename)):
							input_list.append(os.path.join(cur_dir,filename))
		return input_list


	#TO DO: 兼容之前版本的插件，将生成配置项翻译成插件所需格式
	def translate_config_item(self,item,target,action,option):
		# dr = data_recorder
		config = {}
		# rel_dir = item[0].replace(option['input']+os.path.sep,'')
		# rel_dir = os.path.relpath(item[0],option['input'])
		# input_root=task_settings['taskdefs'][action]['input-root']
		# dir_path=os.path.join(input_root,rel_dir)
		dir_path = item[0]
		input_list = []
		other = item[1]
		if not os.path.exists(dir_path):
			return config
		if 'input_list' not in other[target][action]:
			input_list=self.gen_input_file_list_for_single_dir(dir_path,action)
		else:
			for input_dir_path in other[target][action]['input_list']:
				input_list.extend(self.gen_input_file_list_for_single_dir(input_dir_path,action))
		if not len(input_list)==0:			
			input_root = task_settings['taskdefs'][action]['input-root']
			config['config-root'] = other[target][action]['config-root']
			config['config-file'] = other[target][action]['config-file']
			config['options'] = other[target][action]['options']
			config['inputroot'] = input_root
			config['input'] = input_list
			if 'input_list' in other[target][action]:
				config['input-dir'] = [os.path.relpath(dir,input_root) for dir in other[target][action]['input_list']]
			else:
				config['input-dir'] = [os.path.relpath(dir_path,input_root)]
	
			# output_root = os.path.join(option['cachedir'],'work',option['game'],target)
			output_root = task_settings['taskdefs'][action]['output-root']
			if not dir_path == input_root:
				# output_dir = os.path.join(output_root,dir_path.replace(input_root+os.path.sep,''))
				output_dir = os.path.join(output_root,os.path.relpath(dir_path,input_root))
			else:
				output_dir = output_root
			config['outputroot']= output_root	
			config['output-root']= output_dir
			if 'output' in other[target][action]:
				config['output'] = other[target][action]['output']
			else:
				config['output'] = os.path.split(dir_path)[1]
		return config
		pass

	#TO DO: 兼容之前版本的插件，将生成配置项翻译成插件所需格式，windows下中文路径支持
	# windows下路径主要有两点问题，1使用\而非/ 2中文编码对于cp1252和utf-8都有问题，需要处理
	def translate_config_item_win(self,item,target,action,option):
		# dr = data_recorder
		config = {}
		rel_dir = item[0].replace(option['input']+os.path.sep,'')
		input_root=task_settings['taskdefs'][action]['input-root']
		dir_path=os.path.join(input_root,rel_dir)
		input_list = []
		other = item[1]
		if not os.path.exists(dir_path):
			return config
		if 'input_list' not in other[target][action]:
			input_list=self.gen_input_file_list_for_single_dir(dir_path,action)
		else:
			for input_dir_path in other[target][action]['input_list']:
				input_list.extend(self.gen_input_file_list_for_single_dir(input_dir_path,action))
		if not len(input_list)==0:			
			other = item[1]
			input_root = task_settings['taskdefs'][action]['input-root']
			config['config-root'] = other[target][action]['config-root'].replace('/',os.path.sep)
			config['config-file'] = other[target][action]['config-file'].replace('/',os.path.sep)
			config['options'] = other[target][action]['options']
			config['inputroot'] = input_root.replace('/',os.path.sep)
			config['input'] = input_list
			if 'input_list' in other[target][action]:
				config['input-dir'] = [dir.replace(input_root+os.path.sep,'').replace('/',os.path.sep) for dir in other[target][action]['input_list']]
			else:
				config['input-dir'] = [dir_path.replace(input_root+os.path.sep,'').replace('/',os.path.sep)]
	
			# output_root = os.path.join(option['cachedir'],'work',option['game'],target)
			output_root = task_settings['taskdefs'][action]['output-root']
			rel_dir_path = dir_path.replace(input_root+os.path.sep,'')
			output_dir = os.path.join(output_root,rel_dir_path)
			
			config['outputroot']= output_root.replace('/',os.path.sep)	
			config['output-root']= output_dir.replace('/',os.path.sep)
			if 'output' in other[target][action]:
				config['output'] = other[target][action]['output'].replace('/',os.path.sep)
			else:
				config['output'] = os.path.split(dir_path)[1].replace('/',os.path.sep)
			for key,value in list(config.items()):
				if isinstance(value,str):
					config[key] =  mut.encodePath(config[key])
				if isinstance(value,list):
					for i in range(0,len(config[key])):
						if not isinstance(config[key][i],str):
							config[key][i] = mut.encodePath(config[key][i])		
		return config
		pass

	def cleanWorkDir(self,runorder,task_settings):
		for action in runorder:
			action_output_root = task_settings['taskdefs'][action]['output-root']
			needClean = task_settings['taskdefs'][action].get('clean',True)
			if os.path.exists(action_output_root) and needClean:
				shutil.rmtree(action_output_root)
				logger.debug(action+" removing "+action_output_root)

	def configNeedToRun(self,blc,config,action,modified_rel_dirs):
		# input_dir_list = list(set([os.path.join(config['inputroot'],d) for d in config['input-dir']]))
		input_dir_list = config['input-dir']
		need_to_run = False
		ncfg_path = config['config-file']

		print(blc.modified_dir_list)
		if os.path.normpath(ncfg_path) in blc.modified_ncfg_list:
			need_to_run = True
		for input_dir in input_dir_list:
			print(os.path.normpath(input_dir))
			if os.path.normpath(input_dir) in modified_rel_dirs:
				print(input_dir)
				print("in blc.modified_dir_list")
				need_to_run = True
			for deleted_ncfg_path in blc.deleted_ncfg_list:
				if os.path.normpath(input_dir) in deleted_ncfg_path:
					need_to_run = True

		return need_to_run
		pass

	# def retriveResFormRC(self,bs,config,action,lsc_result_rows):
	# 	return bs.syncLSCResult(config,action,lsc_result_rows)
	# 	pass

	def getRunOrder(self,runorder_tag):
		ro_dict = mut.getProjectConfig('runorder_version')
		if ro_dict:
			return ro_dict.get(runorder_tag,None)
		else:
			return None

	# svn diff 信息需要结合global_cfg_dict 来更新完整的变更信息，用于处理有依赖的action变更的情况
	def updateDiffList(self,blc):
		for item in list(global_cfg_dict.items()):
			cur_dir = item[0]
			if self._options['target'] in item[1]:
				for action in list(item[1][self._options['target']].keys()):
					ncfg_path = item[1][self._options['target']][action]['config-file']
					if os.path.normpath(ncfg_path) in blc.modified_ncfg_list:
						input_root = task_settings['taskdefs'][action]['input-root']
						rel_path = os.path.relpath(cur_dir,input_root)
						input_path = os.path.join(self._options['input'],rel_path)
						if not os.path.normpath(input_path) in blc.modified_dir_list:
							blc.modified_dir_list.append(os.path.normpath(input_path))

		pass

	def clearOuputDir(self):
		output_root = self._options['output']
		if os.path.exists(output_root):
			shutil.rmtree(output_root)
		os.makedirs(output_root)

	def run(self):
		blc = BaseLocalChange(self._options)
		if not self._options['dev'] and not self._options['norc']:
			blc.processDiff()
		bs = None
		if not self._options['dev'] and not self._options['norc']:
			bs = BS.BaseSync(self._options)
			bs.get_db_conn(BS.DB_CONFIG)
			bs.clearReadyDir()
		if not self._options['dev'] and not self._options['norc']:
			self.clearOuputDir()
		need_run_all = self._options.get('all',self._options['dev'] or self._options['norc'])
		self.gen_all_white_dict(self._options)
		input_root = self._options['input']
		self.parseConfig(input_root,self._options)
		if 'runversion' in self._options:
			runorder_list = None
			runorder_list = self.getRunOrder(self._options['runversion'])
			print("runorder_list")
			print(runorder_list)
			if runorder_list:
				task_settings['runorder'] = runorder_list
		project_name = self._options['game']
		logger.debug("Gen GDict Complete")
		bd = BaseActionDispatch.BaseActionDispatch()
		pwd = os.path.dirname(os.path.abspath(__file__))
		root,_ = os.path.split(pwd)
		project_name = self._options['game']
		procfgdir = os.path.join(root,'projects',project_name,'taskplugin')
		mtlcfgdir = os.path.join(root,'taskplugin','plugin')
		plugindir = [procfgdir,mtlcfgdir]
		bd.set_plugin_dir(plugindir)
		cache_dir = self._options['cachedir']
		tpcache_path = os.path.join(cache_dir,'tpchache')
		action_run_order = task_settings['runorder']
		action_run_order = self._options.get('runorder',action_run_order)
		# print "runorder"
		# print action_run_order
		self.updateDiffList(blc)
		modified_rel_dirs = [os.path.normpath(os.path.relpath(path,input_root)) for path in blc.modified_dir_list]
		run_counter = 0
		self.cleanWorkDir(action_run_order,task_settings)
		# print json.dumps(global_cfg_dict,indent=2)
		for action in action_run_order:
			need_rc_cache = True
			if "wait" in task_settings['taskdefs'][action]:
				from time import sleep
				logger.debug("sleep "+str(task_settings['taskdefs'][action]['wait'])+"seconds")
				sleep(task_settings['taskdefs'][action]['wait'])
			if "rccache" in task_settings['taskdefs'][action]:
				need_rc_cache = task_settings['taskdefs'][action]["rccache"] 

			for item in list(global_cfg_dict.items()):
				if self._options['target'] in item[1]:
					for item_action in list(item[1][self._options['target']].keys()):
						if item_action == action:
							module = self.getActionModuleByType(action)
							if sys.platform == 'win32':
								config = self.translate_config_item_win(item,self._options['target'],action,self._options)
							else:
								config = self.translate_config_item(item,self._options['target'],action,self._options)						
							if not config=={}:
								if len(config['input'])==0:
									continue
									
								if need_run_all or self.configNeedToRun(blc,config,action,modified_rel_dirs) or not need_rc_cache:
									print("config need to run")
									print(action)
									print(config)
									config['cachedir'] = cache_dir
									bd.invokeAction(module,config,tpcache_path)
									run_counter = run_counter+1
									if action not in run_dict:
										run_dict[action]=[]
									run_dict[action].append(config)
		# bs.syncReadyFilesRc()
		logger.debug("Change List has "+str(len(blc.modified_dir_list))+" dirs")
		logger.debug("Ncfg list has "+str(len(blc.modified_ncfg_list))+" items")
		logger.debug("Run action for "+str(run_counter)+" times")
		return run_dict

	def isToGo(self,cur_dir,cfg_ops,data_recorder,options):
		dr = data_recorder
		data_fectch_result = dr.fetch_timestamp_for_single_dir(cur_dir,options['target'],cfg_ops)
		# print "is_to_go"
		# print data_fectch_result.get('res_id')+"   |    "+dr.md5_for_str(cur_dir+options['target']+json.dumps(cfg_ops))
		is_options_changed= data_fectch_result.get('res_id')!=dr.md5_for_str(cur_dir+options['target']+json.dumps(cfg_ops))
		is_dir_changed= data_fectch_result.get('timestamp')<os.stat(cur_dir).st_mtime
		if is_dir_changed or is_options_changed:
			return True
		return False

	def getActionModuleByType(self,type):
		if task_settings:
			return task_settings['taskdefs'][type]['module']
		return None

	def parseConfig(self,res_root,options):
		pwd = os.path.dirname(os.path.abspath(__file__))
		root,_ = os.path.split(pwd)
		project_name = options['game']
		procfgdir = os.path.join(root,'projects',project_name,'taskplugin')
		mtlcfgdir = os.path.join(root,'taskplugin')
		if(os.path.exists(mtlcfgdir) and os.path.exists(procfgdir)):
		    self.parseGlobalConfig(os.path.join(mtlcfgdir,'settings.yaml'),options)
		    self.parseGlobalConfig(os.path.join(procfgdir,'settings.yaml'),options)
		else:
			logger.warning("[警 告] 未找到插件目录 \n"+mtlcfgdir+'\n'+procfgdir)
			return
		# print json.dumps(task_settings,indent=2)
		self.check_and_regist_ncfg(res_root)
		for parent,dirnames,filenames in os.walk(res_root):
			dirnames[:] = [d for d in dirnames if not '.svn' in d]
			for dirname in dirnames:
				cur_dir = os.path.join(parent,dirname)
				self.check_and_regist_ncfg(cur_dir)

		logger.debug("global config with %d items"%(len(list(global_cfg_dict.keys()))))


	def moveResToDestination(self,task_settings,global_cfg_dict,options,data_recorder):
		dr = data_recorder
		target = options['target']
		for item in list(global_cfg_dict.items()):
			cur_dir = item[0]
			cur_dir_mtime = os.stat(cur_dir).st_mtime
			if target in item[1]:
				for action in list(item[1][target].keys()):
					re_orin_path = dr.get_most_recent_dir(cur_dir,target,item[1])
					if re_orin_path:
						orin_dir = os.path.join(options['cachedir'],'work',target,re_orin_path)
						if os.path.exists(orin_dir):
							file_list = [os.path.join(orin_dir,filename) for filename in os.listdir(orin_dir) if os.path.isfile(os.path.join(orin_dir,filename))]
							dest_dir = task_settings['taskdefs'][action]['output-root']
							if not os.path.exists(dest_dir):
								os.makedirs(dest_dir)
							for src_file in file_list:							 
								shutil.copy2(src_file,dest_dir)
								# print ""+action+"move src_file "+src_file+" to "+dest_dir




if __name__ == "__main__":
	begin = time()
	logger.debug("Begin Gen GDict test")
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
	bpc = BaseParseConfigs(options)		
	bpc.run()
	with open('/Users/playcrab/Desktop/global_cfg_dict.json','w') as f:
		f.write(json.dumps(global_cfg_dict,indent=2))
	with open('/Users/playcrab/Desktop/run_dict.json','w') as f:
		f.write(json.dumps(run_dict,indent=2))									

				
	
		
