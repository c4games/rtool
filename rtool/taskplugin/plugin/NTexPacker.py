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
import MultiProcessRunner
import rtool.utils as utils
import TPCache2
from TPTask import TPTask
from pcutils.remove_smartupdate import remove_smartupdate_from_plist_or_json

logger = utils.getLogger('TexPacker')

def relativePath(base_path,path):
	if not base_path == path:
		return path.replace(base_path+os.path.sep,'')
	else:
		return ""
	pass

def run():
	print "TexPacker"
	pass

def run_with_configs(configs,tp=None):
	logger.debug("Executing NTexPacker")
	apaction = TexPacker()
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
			if ui_index_dict['indices'].has_key(key):
				del ui_index_dict['indices'][key]
			plistlib.writePlist(ui_index_dict,ui_index_path)
			with open('%s.json' % ui_index_path, 'w') as f:
			    f.write(json.dumps(ui_index_dict))
			    f.close()
	if os.path.exists(tp_output):
		shutil.rmtree(tp_output)
	pass

class TexPacker():
	"""根据资源配置文件将散图合并为大图"""
	
	process = None
	default_option = None

	res_root = None
	packing_root = None
	ignore_list=[]

	def __new__(cls, *args, **kw):  
	    if not hasattr(cls, '_instance'):  
	        orig = super(Singleton, cls)  
	        cls._instance = orig.__new__(cls, *args, **kw)  
	    return cls._instance 

	def setResRoot(self,root):
		self.res_root = root
		pass
	def setPackingRoot(self,root):
		self.packing_root = root
		pass
	def setDefaultOption(self,option):
		self.default_option = option
		pass

	# tp结束之后将plist中的信息加入ui的index文件中，使用游戏客户端的index机制查找文件
	def gen_index(self,config,src_plist_path,dist_index_path):
		def addVersionInfoForDict(Dict , typeString):
		    dictByVersion = {}
		    fileinfo = {}
		    fileinfo["indexType"] = typeString
		    fileinfo["version"] = "1.0"
		    enable_xml_to_binary = os.getenv('enable_xml_to_binary')
		    if typeString == "MovieClip":
		        if is_true(enable_xml_to_binary):
		            fileinfo["xmlDataFormat"] = "bobj"
		        enable_plist_to_json = os.getenv('enable_plist_to_json')
		        if is_true(enable_plist_to_json):
		            fileinfo["xmlDataFormat"] = "json"

		    dictByVersion["fileinfo"] = fileinfo
		    dictByVersion["indices"] = Dict
		    return dictByVersion

		if os.path.exists(src_plist_path):
			root_dir = config['outputroot']
			index_dict = {}
			if not os.path.exists(dist_index_path):
				index_dict['indices']={}
			else:
				index_dict = plistlib.readPlist(dist_index_path)
			src_plist = plistlib.readPlist(src_plist_path)
			# print "outputroot"+root_dir
			# print "output-root"+config["output-root"]
			# print src_plist_path
			src_plist_relative_path = relativePath(root_dir,src_plist_path)			
			index_dict['indices'][src_plist_relative_path]={}
			index_dict['indices'][src_plist_relative_path]['frames']=[]
			for frame_name in src_plist['frames'].keys():
				index_dict['indices'][src_plist_relative_path]['frames'].append(frame_name)
			index_dict['indices'][src_plist_relative_path]['realTextureFileName'] = src_plist['metadata']['realTextureFileName']
			index_dict['indices'][src_plist_relative_path]['textureFileName'] = src_plist['metadata']['textureFileName']
			if not index_dict.has_key('fileinfo'):
				index_dict = addVersionInfoForDict(index_dict['indices'],'ImageAltas')
				pass
			with open('%s.json' % dist_index_path, 'w') as f:
			    f.write(json.dumps(index_dict))
			    f.close()
			plistlib.writePlist(index_dict,dist_index_path)
		pass

	# kox类游戏index生成
	def gen_kox_index(self,config,src_plist_path,dist_index_path):
		def addVersionInfoForDict(Dict , typeString):
		    dictByVersion = {}
		    fileinfo = {}
		    fileinfo["indexType"] = typeString
		    fileinfo["version"] = "1.0"
		    enable_xml_to_binary = os.getenv('enable_xml_to_binary')
		    if typeString == "MovieClip":
		        if is_true(enable_xml_to_binary):
		            fileinfo["xmlDataFormat"] = "bobj"
		        enable_plist_to_json = os.getenv('enable_plist_to_json')
		        if is_true(enable_plist_to_json):
		            fileinfo["xmlDataFormat"] = "json"

		    dictByVersion["fileinfo"] = fileinfo
		    dictByVersion["indices"] = Dict
		    return dictByVersion

		if os.path.exists(src_plist_path):
			root_dir = utils.decodePath(config['outputroot'])
			index_dict = {}
			if not os.path.exists(dist_index_path):
				index_dict['indices']={}
			else:
				index_dict = plistlib.readPlist(dist_index_path)
			all_Images = []
			for key in index_dict['indices'].keys():
				all_Images.extend(index_dict['indices'][key]['items'])
			src_plist = plistlib.readPlist(src_plist_path)
			# print "outputroot"+root_dir
			# print "output-root"+config["output-root"]
			# print src_plist_path
			src_plist_relative_path = relativePath(root_dir,src_plist_path)
			cache_pack = os.path.join(config['cachedir'],'pack')
			store_plist_path_key = utils.encodePath(relativePath(cache_pack,src_plist_path))
			index_dict['indices'][store_plist_path_key]={}
			index_dict['indices'][store_plist_path_key]['items']=[]
			for frame_name in src_plist['frames'].keys():
				# if frame_name in all_Images:
				# 	logger.debug(u'index中存在重复文件 %s',frame_name)
				index_dict['indices'][store_plist_path_key]['items'].append(frame_name)
			index_dict['indices'][store_plist_path_key]['realTextureFileName'] = src_plist['metadata']['realTextureFileName']
			index_dict['indices'][store_plist_path_key]['textureFileName'] = src_plist['metadata']['textureFileName']
			if not index_dict.has_key('fileinfo'):
				index_dict = addVersionInfoForDict(index_dict['indices'],'ImageAltas')
				pass
			with open('%s.json' % dist_index_path, 'w') as f:
			    f.write(json.dumps(index_dict))
			    f.close()
			plistlib.writePlist(index_dict,dist_index_path)
		pass

	def gen_package_info(self,config,src_plist_path,dst_file_path):
		input_dirs = config['input-dir']

		pass

	# tp生成的plist中frame的名称形如xxx.png,而csd/csb中形如aaa/bbb/xxx.png,修改plist使其一致
	def modify_plist_frame_path(self,config,plist_path):
		if os.path.exists(plist_path):
			plist_dict = plistlib.readPlist(plist_path)
			modified_plist_dict = {}
			modified_plist_dict['frames']={}
			for frame in plist_dict['frames'].keys():
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
	def modif_plist_scale_factor(self,config,plist_path):
		if os.path.exists(plist_path) and config['options'].has_key('scale'):
			plist_dict = plistlib.readPlist(plist_path)
			if not plist_dict['metadata'].has_key('scale'):
				plist_dict['metadata']['scale'] = str(config['options']['scale'])
			plistlib.writePlist(plist_dict,plist_path)
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
		if config['options'].has_key('extendFileName') and not config['options']['extendFileName']:
			extend_dir_for_name = ""

		if config['options'].has_key('multipack'):
			tp_output = os.path.join(utils.decodePath(config['output-root']),extend_dir_for_name+config['output']+"{n}")
		else:
			tp_output = os.path.join(utils.decodePath(config['output-root']),extend_dir_for_name+config['output'])
		option_list =[]
		for key in config['options'].keys():
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

			tp_cache = TPCache2.TPCache2(tp)
			tp_cache.command_arrange([TPTask.task_from_command(tp_command.split())])
	        # self.modify_plist_frame_path(config,tp_output+".plist")
	        self.modif_plist_scale_factor(config,tp_output+'.plist')
	        if not config['options'].has_key('multipack'):
	        	remove_smartupdate_from_plist_or_json(tp_output+".plist")
	        	# index_dir,b_dir = os.path.split(config['outputroot'])
	        	index_dir = config['cachedir']
	        	# self.gen_kox_index(config,tp_output+".plist",os.path.join(index_dir,'index'))
	        else:	        	
	        	dirname,filename = os.path.split(tp_output)
	        	file_name_prifx = filename.replace('{n}','')
	        	if os.path.exists(dirname):
	        		for item in os.listdir(dirname):
	        			if os.path.isfile(os.path.join(dirname,item)):
	        				if '.plist' in item and file_name_prifx in item:
	        					remove_smartupdate_from_plist_or_json(os.path.join(dirname,item))
	        					# index_dir = config['outputroot']
	        					# self.gen_kox_index(config,os.path.join(dirname,item),os.path.join(index_dir,'index'))
					

		pass
