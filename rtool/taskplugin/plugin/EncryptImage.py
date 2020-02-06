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

from rtool.taskplugin.plugin.TPTask import TPTask
import rtool.taskplugin.plugin.TPCache2 as TPCache2

logger = utils.getLogger('EncryptImage')

def run_with_configs(configs,tp=None):
	logger.debug("Executing Image Compress Action")
	apaction = EncryptImage()
	apaction.go(configs,tp)
	pass

def clean_output(configs):

	pass

class EncryptImage:
	"""图片加密"""

	def Encrpt(self,input_path,output_dir,key="DEMOKEY123456789",ext=".png"):
		# KEY = "PLAYCRAB00000000"
		KEY = key
		filename = os.path.split(input_path)[1]
		if os.path.exists(input_path):
			with open('%s' % input_path,'rb') as ReadFileData:
				buff = ReadFileData.read()
				ReadFileData.close()
				if not os.path.exists(output_dir):
					os.makedirs(output_dir)
				with open('%s' % os.path.join(output_dir,filename.split('.')[0]+ext),'wb') as WriteFileData:
					WriteFileData.write(KEY)
					for i in range(0,16):
					    WriteFileData.write( chr(ord(buff[i]) ^ ord(KEY[i])))
					WriteFileData.write(buff[16:])
					WriteFileData.close()
		pass

	def Decrypt(self, input_dir, key="DEMOKEY123456789"):
	    logger.debug("Decrypt image under "+input_dir)
	    KEY = key
	    imagefile_list = [os.path.join(p,fn) for p,fns,_ in os.walk(input_dir) for fn in fns if '.png' in fn]
	    for imagefile in imagefile_list :
	        logger.debug('Decrypt image: {}'.format(imagefile))
	        with open('%s' % imagefile, 'rb') as f:
	            streamBuff = f.read()
	            f.close()
	            with open('%s' % imagefile, 'wb') as f:  
	                buff = streamBuff[16:]
	                for i in range(0,16):
	                    f.write( chr(ord(buff[i]) ^ ord(KEY[i])))
	                f.write(buff[16:])
	                f.close()

	def EncrptNoZip(self,filename,alpha_file_name):
		KEY = "PLAYCRAB00000000"		
		if os.path.exists(filename):
			png_alpha_name = filename.split('.')[0]+"_alpha"+'.png'
			if os.path.exists(png_alpha_name):
				os.remove(png_alpha_name)
			with open('%s' % filename,'rb') as ReadFileData:
				buff = ReadFileData.read()
				ReadFileData.close()
				with open('%s' % filename.split('.')[0]+'.png','wb') as WriteFileData:
					WriteFileData.write(KEY)
					for i in range(0,16):
					    WriteFileData.write( chr(ord(buff[i]) ^ ord(KEY[i])))
					WriteFileData.write(buff[16:])
					WriteFileData.close()					
					os.remove(filename)
			if os.path.exists(alpha_file_name):
				with open('%s' % alpha_file_name,'rb') as ReadFileData:
					buff = ReadFileData.read()
					ReadFileData.close()
					with open('%s' % filename.split('.')[0]+'.pnga','wb') as WriteFileData:
						WriteFileData.write(KEY)
						for i in range(0,16):
						    WriteFileData.write( chr(ord(buff[i]) ^ ord(KEY[i])))
						WriteFileData.write(buff[16:])
						WriteFileData.close()
						os.remove(alpha_file_name)
		pass

	def zipAndEncrypt(self,file_name,alpha_file_name,width,height):
		KEY = "PLAYCRAB#MASTER#"

		outFile1 = file_name.split(".")[0]+'.png'
		outFile2 = outFile1 + "a"
		pkmFile = file_name
		alphaFile = alpha_file_name

		png_alpha_name = outFile1.split('.')[0]+"_alpha"+'.png'

		if os.path.exists(png_alpha_name):
			os.remove(png_alpha_name)

		# 压缩文件

		size = os.path.getsize(pkmFile)
		pkmData = open(pkmFile, "rb").read(size)
		cczFile = open(outFile1, "wb")

		cczFile.write(struct.pack(">4sHHII", "CCZ!", 0, 1, 0, size))
		cczFile.write(zlib.compress(pkmData))
		cczFile.close()
		os.remove(pkmFile)

		h = "h"
		c = "c"
		m = "m"
		str = struct.pack("HHccc", width, height, h, c, m)

		WriteFileData = open(outFile1,'rb')
		data = WriteFileData.read(os.path.getsize(outFile1))
		WriteFileData.close()
		WriteFileData = open(outFile1,'wb')

		WriteFileData.write(str)
		for i in range(0,16):
		    WriteFileData.write( chr(ord(data[i]) ^ ord(KEY[i])) )

		WriteFileData.write(data[16:])
		# WriteFileData.write(data[:])
		WriteFileData.close()

		if os.path.exists(alphaFile):
		    size = os.path.getsize(alphaFile)
		    alphaData = open(alphaFile, "rb").read(size)
		    cczFile = open(outFile2, "wb")

		    cczFile.write(struct.pack(">4sHHII", "CCZ!", 0, 1, 0, size))
		    cczFile.write(zlib.compress(alphaData))
		    cczFile.close()
		    os.remove(alphaFile)

		    WriteFileData = open(outFile2,'rb')
		    data = WriteFileData.read(os.path.getsize(outFile2))
		    WriteFileData.close()
		    WriteFileData = open(outFile2,'wb')

		    WriteFileData.write(str)
		    for i in range(0,16):
		        WriteFileData.write( chr(ord(data[i]) ^ ord(KEY[i])) )

		    WriteFileData.write(data[16:])
		    WriteFileData.close()
		pass


	def go(self,configs,tp):
		input_path_list = configs['input']
		output_dir = configs['output-root']
		KEY = configs['options']['key']
		for input_path in input_path_list:
			self.Encrpt(input_path,output_dir,KEY)

		pass




		
