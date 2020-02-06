#coding=utf-8
import yaml
import os
import os.path
import shutil
import json
import subprocess
import tempfile
import sys
import plistlib
sys.path.append(os.path.split(os.path.realpath(__file__))[0])
import rtool.taskplugin.plugin.MultiProcessRunner
import rtool.utils as utils
import rtool.taskplugin.plugin.TPCache2 as TPCache2
from rtool.taskplugin.plugin.TPTask import TPTask
from rtool.taskplugin.plugin.pcutils.remove_smartupdate import remove_smartupdate_from_plist_or_json
from rtool.taskplugin.plugin.pcutils.remove_smartupdate import remove_smartupdate_from_plist_or_json_then_rename

logger = utils.getLogger('AnimPacker')
logger.setLevel("DEBUG")

def relativePath(base_path,path):
	if not base_path == path:
		return path.replace(base_path+os.path.sep,'')
	else:
		return ""
	pass

def run():
	print("AnimPacker")
	pass

def run_with_configs(configs,tp=None):
	logger.debug("Executing NAnimPacker")
	apaction = AnimPacker()
	apaction.pack(configs,tp)
	pass

def clean_output(configs):
	default_output_path = configs["outputroot"]
	tp_output = os.path.join(default_output_path,configs['output'])
	png_path = os.path.join(tp_output,configs['output']+'.png')
	plist_path = os.path.join(tp_output,configs['output']+'.plist')
	ui_index_path = os.path.join(configs['outputroot'],'ui.index')
	# key = utils.relativePath(configs['outputroot']+'/',plist_path)
	cache_pack = os.path.join(configs['cachedir'],'pack')
	key = "asset"+os.path.sep+relativePath(cache_pack,plist_path)
	ui_index_dict={}
	if os.path.exists(png_path):
		os.remove(png_path)
	if os.path.exists(plist_path):
		os.remove(plist_path)
		if os.path.exists(ui_index_path):
			ui_index_dict = plistlib.readPlist(ui_index_path)
			if key in ui_index_dict['indices']:
				del ui_index_dict['indices'][key]
			plistlib.writePlist(ui_index_dict,ui_index_path)
			with open('%s.json' % ui_index_path, 'w') as f:
			    f.write(json.dumps(ui_index_dict))
			    f.close()
	if os.path.exists(tp_output):
		shutil.rmtree(tp_output)
	pass

class AnimPacker():
	"""根据资源配置文件将散图合并为大图"""
	
	process = None
	default_option = None

	res_root = None
	packing_root = None
	ignore_list=[]

	# def __new__(cls, *args, **kw):  
	#     if not hasattr(cls, '_instance'):  
	#         orig = super(Singleton, cls)  
	#         cls._instance = orig.__new__(cls, *args, **kw)  
	#     return cls._instance 

	def setResRoot(self,root):
		self.res_root = root
		pass
	def setPackingRoot(self,root):
		self.packing_root = root
		pass
	def setDefaultOption(self,option):
		self.default_option = option
		pass


	# tp生成的plist中frame的名称形如xxx.png,而csd/csb中形如aaa/bbb/xxx.png,修改plist使其一致
	def modify_plist_frame_path(self,config,plist_path):
		if os.path.exists(plist_path):
			plist_dict = plistlib.readPlist(plist_path)
			modified_plist_dict = {}
			modified_plist_dict['frames']={}
			for frame in list(plist_dict['frames'].keys()):
				for input_path in config['input']:
					dirname,filename = os.path.split(input_path)
					if frame == filename or frame == relativePath(config['inputroot'],input_path):						
						#print "modify_plist_frame_path"+config['inputroot']+"|||| "+input_path
						modified_frame = relativePath(config['inputroot'],input_path)
						#print "modify_plist_frame_path frame "+modified_frame
						modified_plist_dict['frames'][modified_frame] = plist_dict['frames'][frame]
			modified_plist_dict['metadata'] = plist_dict['metadata']
			#print "modify_plist_frame_path "+"plistlib.writePlist "+plist_path
			plistlib.writePlist(modified_plist_dict,plist_path)
		pass

	def pack(self,config,tp):
		input_dir_list = []
		tp_option =None
		tp_input =None
		tp_outout =None
		tp_output_path = None

		default_tp_format = None
		default_tp_scale = None
		default_tp_opt =None

		tp_command_template = 'TexturePacker --sheet $sheet --data $data $options $input --border-padding 2 --shape-padding 2'
		
		tp_format = config['options']
		# extendFileName不配或配置为True时输出文件名会连接上层目录名，配置为False时则不会
		extend_dir_for_name = utils.decodePath(config['output-root']).split(os.path.sep)[-2]+'_'
		if 'extendFileName' in config['options'] and not config['options']['extendFileName']:
			extend_dir_for_name = ""

		if 'multipack' in config['options']:
			tp_output = os.path.join(utils.decodePath(config['output-root']),extend_dir_for_name+config['output']+"{n}")
		else:
			tp_output = os.path.join(utils.decodePath(config['output-root']),extend_dir_for_name+config['output'])
		option_list =[]
		for key in list(config['options'].keys()):
			if key == "extendFileName":
				continue
			option = "--"+key+" "+str(config['options'][key])
			option_list.append(option)
		tp_option = ' '.join(option_list)
		tp_input = ' '.join(config['input'])
		input_list =[]
		for i in range(0,len(config['input'])):
			input_list.append(utils.decodePath(config['input'][i]))
		tp_input = ' '.join(input_list)
		if len(tp_input.strip())>0:
		# print tp_option
			tp_command = tp_command_template
			tp_command = tp_command.replace('$options',tp_option)
			tp_command = tp_command.replace('$sheet',tp_output+".png")
			tp_command = tp_command.replace('$data',tp_output+".plist")
			tp_command = tp_command.replace('$input',tp_input)
			logger.debug(tp_command)
			if sys.platform == 'win32':
				tp_command = tp_command.encode(sys.stdout.encoding or 'gbk')

			tp_cache = TPCache2.TPCache2(tp)
			tp_cache.command_arrange([TPTask.task_from_command(tp_command.split())])
			# self.modify_plist_frame_path(config,tp_output+".plist")
			if 'multipack' not in config['options']:
				remove_smartupdate_from_plist_or_json(tp_output+".plist")
			else:
				dirname,filename = os.path.split(tp_output)
				file_name_prifx = filename.replace('{n}','')
				if os.path.exists(dirname):
					items = os.listdir(dirname)
					plists = [item for item in items if '.plist' in item and file_name_prifx in item and not '_temp' in item]
					print(plists)
					len_plists = len(plists)
					if len_plists>1:
						plist_name = file_name_prifx+'.plist'
						plist_dict={}
						plist_dict['multiplists']=True
						plist_dict['items']=[]
						for plist in plists:
							plist_dict['items'].append(plist)
							remove_smartupdate_from_plist_or_json(os.path.join(dirname,plist))
						plistlib.writePlist(plist_dict,os.path.join(dirname,plist_name))
					elif len_plists == 1:
						item = plists[0]
						name,ext = os.path.splitext(item)
						rename = name[:-1]
						# multipack后如果出现了两位数的合图结果是不对的，项目组需要检查一下自己的图集是不是出了什么问题
						ori_plist = os.path.join(dirname,item)
						ori_png = os.path.join(dirname,name+'.png')
						rename_plist = os.path.join(dirname,rename+'.plist')
						rename_png = os.path.join(dirname,rename+'.png')
						remove_smartupdate_from_plist_or_json_then_rename(ori_plist,rename)
						os.rename(ori_plist,rename_plist)
						os.rename(ori_png,rename_png)
					else:
						logger.error("NO PLIST FOUND in "+dirname)					

		pass

if __name__ == '__main__':
	logger.debug("helllooo")

