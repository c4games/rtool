#coding=utf-8
import yaml
import os
import os.path
import shutil
import json
import subprocess
import sys
import tempfile
import plistlib
import zlib
import struct
from time import sleep
sys.path.append(os.path.split(os.path.realpath(__file__))[0])
import rtool.taskplugin.plugin.MultiProcessRunner as MultiProcessRunner
import rtool.utils as utils
import rtool.taskplugin.plugin.TPtemplates as TPtemplates

from rtool.taskplugin.plugin.TPTask import TPTask
import rtool.taskplugin.plugin.TPCache2 as TPCache2


logger = utils.getLogger('Compresser')

def run():
	logger.debug("Executing Image Compress Action")
	pass

def run_with_configs(configs,tp=None):
	logger.debug("Executing Image Compress Action")
	apaction = CompressAction()
	apaction.go(configs,tp)
	pass

def safeRemove(path):
	if os.path.exists(path):
		os.remove(path)
	pass

def clean_output(configs):
	default_output_path = configs["output-root"]
	input_list = configs['input']
	for input_file_path in input_list:
		input_file = os.path.split(input_file_path)[-1]
		input_file_name = os.path.splitext(input_file)[0]		
		png_path = input_file_name+'.png'
		pnt_alpha_path = input_file_name+'_alpha.png'
		plist_path = input_file_name+'plist'
		safeRemove(png_path)
		safeRemove(pnt_alpha_path)
		safeRemove(plist_path)
	if os.path.exists(default_output_path):
		shutil.rmtree(default_output_path)
	logger.debug(default_output_path+" deleted")
	pass

class CompressAction:
	"""根据配置文件将图片压缩为需要的格式"""
	
	default_option = None

	res_root = None
	packing_root = None
	ignore_list=[]

	def setResRoot(self,root):
		self.res_root = root
		pass
	def setPackingRoot(self,root):
		self.packing_root = root
		pass
	def setDefaultOption(self,option):
		self.default_option = option
		pass

	def go(self,config,tp):
		from PIL import Image	

		pngquant_command_template = TPtemplates.pngquant_command_template
		pngquant_command_nq_template = TPtemplates.pngquant_command_nq_template
		tp_command_template = TPtemplates.tp_command_template
		tp_2pic_rgb_command_template = TPtemplates.tp_2pic_rgb_command_template
		alpha_command_template = TPtemplates.alpha_command_template
		alpha_etc1_command_template = TPtemplates.alpha_etc1_command_template
		png8_command_template = TPtemplates.png8_command_template
		pvr_RGBA8888_command_template = TPtemplates.pvr_RGBA8888_command_template
		etcpack_template = TPtemplates.etcpack_command_template

		command = ""

		# if not config['options'].has_key('zip'):
		# 	config['options']['zip']=True
		ext_hash={}
		ext_hash["png"] = ".png"
		ext_hash["pvr3ccz"] = ".pvr.ccz"
		ext_hash["jpg"] = ".jpg"
		ext_hash["pvr3"] = ".pvr"
		ext_hash["pkm"] = ".pkm"
		ext_hash["pvr2"] = ".pvr"
		ext_hash["pvr2ccz"] = ".pvr.ccz"

		def isImage(file_name):
			try:
				fp = open(file_name,'rb')
				image = Image.open(fp)
				if image.format == "PNG":
					return True
				elif image.format == "JPEG":
					return True
				else:
					return False
			except Exception as e:
				return False
			pass 

		input_list = config['input']
		if 'type' in config['options']:
			for input_file_path in config['input']:
				if isImage(input_file_path):
					input_dir,png_file_name = os.path.split(input_file_path)
					fp = open(input_file_path,'rb')
					image = Image.open(fp)
					width = image.width
					height = image.height
					fp.close()

					if config['options']['type']=='png8':
						command = pngquant_command_nq_template
						command = command.replace('$output',input_file_path)
						command = command.replace('$input',input_file_path)
						# command = command.replace('$quality',config['options']['quality'])
						f = tempfile.TemporaryFile()
						print(("Compresser pngquant "+command))
						if sys.platform == 'win32':
							command = command.encode(sys.stdout.encoding)
						process = subprocess.Popen(command.split(),stdout=f, stderr=f, stdin=subprocess.PIPE)
						process.wait()
						if not process.returncode ==0:
							f.seek(0)
							output = f.read()
							print(("[ERROR] "+output))
						pass
					if config['options']['type']=='png':

						if not os.path.exists(config['output-root']):
							os.makedirs(config['output-root'])
						shutil.copy2(input_file_path,config['output-root'])
						pass
					if config['options']['type']=='pvr2p':
						textureformat = config['options']['textureformat']
						ext = ext_hash.get(textureformat,".pvr.ccz")

						pot = config['options'].get('pot','POT')

						command = tp_2pic_rgb_command_template
						command = command.replace("$dstname",os.path.join(config['output-root'],png_file_name.split('.')[0]+ext))
						command = command.replace("$opt",config['options']["opt"])
						command = command.replace("$srcname",input_file_path)
						command = command.replace("$textureformat",textureformat)
						command = command.replace("$plist",input_file_path.split('.')[0]+"_temp.plist")
						command = command.replace("$extra",config['options'].get('extra',''))
						command = command.replace("$pot",pot)
						tp_cache = TPCache2.TPCache2(tp)
						logger.debug("Compresser pvr2pic "+command)
						if sys.platform == 'win32':
							command = command.encode(sys.stdout.encoding)
						tp_cache.command_arrange([TPTask.task_from_command(command.split())])
					
						command = alpha_command_template
						command = command.replace("$dstname",os.path.join(config['output-root'],png_file_name.split('.')[0]+'_alpha.png'))
						command = command.replace("$srcname",input_file_path)
						command = command.replace("$plist",input_file_path.split('.')[0]+"_temp.plist")
						command = command.replace("$pot",pot)
						tp_cache = TPCache2.TPCache2(tp)
						logger.debug("Compresser ALPHA "+command)
						if sys.platform == 'win32':
							command = command.encode(sys.stdout.encoding)
						tp_cache.command_arrange([TPTask.task_from_command(command.split())])						

						command = tp_command_template
						command = command.replace("$dstname",os.path.join(config['output-root'],png_file_name.split('.')[0]+'_alpha'+ext))
						command = command.replace("$srcname",os.path.join(config['output-root'],png_file_name.split('.')[0]+'_alpha.png'))
						command = command.replace("$plist",input_file_path.split('.')[0]+"_temp.plist")						
						command = command.replace("$opt",config['options']["opt"])
						command = command.replace("$textureformat",textureformat)
						command = command.replace("$extra",config['options'].get('extra',''))					
						tp_cache = TPCache2.TPCache2(tp)
						logger.debug("Compresser ALPHA Compressed"+command)
						if sys.platform == 'win32':
							command = command.encode(sys.stdout.encoding)
						tp_cache.command_arrange([TPTask.task_from_command(command.split())])

						png_alpha_path = os.path.join(config['output-root'],png_file_name.split('.')[0]+'_alpha.png')
						if os.path.exists(png_alpha_path):
							os.remove(png_alpha_path)
						pass

					if config['options']['type']=='pvr':

						textureformat = config['options']['textureformat']
						ext = ext_hash.get(textureformat,".pvr")

						command = tp_command_template

						command = command.replace("$dstname",os.path.join(config['output-root'],png_file_name.split('.')[0]+ext))
						command = command.replace("$opt",config['options']["opt"])
						command = command.replace("$srcname",input_file_path)
						command = command.replace("$plist",input_file_path.split('.')[0]+"_temp.plist")
						command = command.replace("$textureformat",textureformat)
						command = command.replace("$extra",config['options'].get('extra',''))
						tp_cache = TPCache2.TPCache2(tp)
						logger.debug("Compresser pvr "+command)
						if sys.platform == 'win32':
							command = command.encode(sys.stdout.encoding)
						tp_cache.command_arrange([TPTask.task_from_command(command.split())])

						if os.path.exists(os.path.join(config['output-root'],png_file_name)):
							os.remove(os.path.join(config['output-root'],png_file_name))

						pass

					if config['options']['type']=='etc2p':

						textureformat = config['options']['textureformat']
						ext = ext_hash.get(textureformat,".pvr")

						# command = tp_command_template
						# command = command.replace("$dstname",os.path.join(config['output-root'],png_file_name.split('.')[0]+ext))
						# command = command.replace("$opt",config['options']["opt"])
						# command = command.replace("$srcname",input_file_path)
						# command = command.replace("$plist",input_file_path.split('.')[0]+"_temp.plist")
						# command = command.replace("$textureformat",textureformat)
						# command = command.replace("$extra",config['options'].get('extra',''))
						# tp_cache = TPCache2.TPCache2(tp)
						# logger.debug("Compresser ETC1 "+command)
						# tp_cache.command_arrange([TPTask.task_from_command(command.split())])
						if not os.path.exists(config['output-root']):							
							os.makedirs(config['output-root'])
						img = Image.open(os.path.normpath(input_file_path))
						ppm_path = os.path.join(os.path.split(input_file_path)[0],os.path.splitext(png_file_name)[0]+".ppm")
						logger.warning(ppm_path)
						img.save(ppm_path)
						command = etcpack_template
						command = command.replace("$dstname",os.path.normpath(config['output-root']))
						command = command.replace("$srcname",os.path.normpath(ppm_path))
						logger.debug("Compresser ETCPACK "+command)
						f = tempfile.TemporaryFile()
						process = subprocess.Popen(command.split(),stdout=f, stderr=f, stdin=subprocess.PIPE)
						process.wait()
						if not process.returncode ==0:
							f.seek(0)
							output = f.read()
							print("[ERROR] "+str(output))

						# f = tempfile.TemporaryFile()
						# if sys.platform == 'win32':
						# 	command = command.encode(sys.stdout.encoding)

						command = tp_command_template
						command = command.replace("$dstname",os.path.join(config['output-root'],png_file_name.split('.')[0]+'_alpha'+ext))
						command = command.replace("$srcname",input_file_path)
						command = command.replace("$opt",'ETC1_A')
						command = command.replace("$textureformat",textureformat)
						command = command.replace("$extra",config['options'].get('extra',''))
						command = command.replace("$plist",input_file_path.split('.')[0]+"_temp.plist")
						tp_cache = TPCache2.TPCache2(tp)
						# if sys.platform == 'win32':
						# 	command = command.encode(sys.stdout.encoding)
						# logger.debug("Compresser ALPHA Compressed"+str(command))
						tp_cache.command_arrange([TPTask.task_from_command(command.split())])

						if os.path.exists(ppm_path):
							os.remove(ppm_path)

						pass
					if config['options']['type']=='etc':

						textureformat = config['options']['textureformat']
						ext = ext_hash.get(textureformat,".pvr")

						command = tp_command_template
						command = command.replace("$dstname",os.path.join(config['output-root'],png_file_name.split('.')[0]+ext))
						command = command.replace("$opt",config['options']["opt"])
						command = command.replace("$srcname",input_file_path)
						command = command.replace("$plist",input_file_path.split('.')[0]+"_temp.plist")
						command = command.replace("$textureformat",textureformat)
						command = command.replace("$extra",config['options'].get('extra',''))
						tp_cache = TPCache2.TPCache2(tp)
						logger.debug("Compresser ETC1 "+command)
						if sys.platform == 'win32':
							command = command.encode(sys.stdout.encoding)
						tp_cache.command_arrange([TPTask.task_from_command(command.split())])
						pass
					
				if '.plist' in input_file_path:
					if os.path.exists(input_file_path):
						temp=""
						temp=input_file_path.split('.')[0]
						temp=temp.replace(temp.split('_')[0],'')
						if temp == "temp":
							os.remove(input_file_path)
						else:
							dirname,filename = os.path.split(input_file_path)
							plist_dict = plistlib.readPlist(input_file_path)
							origin_texture_name = plist_dict['metadata']['realTextureFileName']
							name,ext = os.path.splitext(origin_texture_name)
							texture_name = origin_texture_name
							textureformat = textureformat = config['options']['textureformat']
							ext = ext_hash.get(textureformat,".pvr") 
							if config['options']['type']=='pvr':
								actual_name = name.split('.')[0]
								texture_name = actual_name+ext
								pass
							if config['options']['type']=='pvr':
								actual_name = name.split('.')[0]
								texture_name = actual_name+ext
								pass
							if config['options']['type']=='etc2p':
								actual_name = name.split('.')[0]
								texture_name = actual_name+ext
							if config['options']['type']=='etc':
								actual_name = name.split('.')[0]
								texture_name = actual_name+ext
							plist_dict['metadata']['realTextureFileName'] = texture_name
							plist_dict['metadata']['textureFileName'] = texture_name
							if not os.path.exists(config['output-root']):
								os.makedirs(config['output-root'])
								with open(os.path.join(config['output-root'],filename),'a'):
									os.utime(os.path.join(config['output-root'],filename),None)
							plistlib.writePlist(plist_dict,os.path.join(config['output-root'],filename))
					pass

