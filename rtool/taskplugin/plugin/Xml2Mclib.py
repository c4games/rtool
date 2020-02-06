#coding=utf-8
import os
import json
import plistlib
from multiprocessing import Process, Manager, Lock
import shutil
import sys
sys.path.append(os.path.split(os.path.realpath(__file__))[0])
import rtool.utils as utils
import rtool.res.action_binaryJson as AJ


logger = utils.getLogger('Xml2Mclib')

def run():
	logger.debug("Xml2Mclib")
	pass

def run_with_configs(configs,tp=None):
	logger.debug("Executing Xml2Mclib")
	apaction = Xml2Mclib()
	apaction.go(configs)
	pass

def safeRemoveDir(dir_path):
	if os.path.exists(dir_path):
		shutil.rmtree(dir_path)
	pass

def clean_output(configs):
	default_output_path = configs["output-root"]
	safeRemoveDir(default_output_path)
	pass


class Xml2Mclib(object):
	"""同步资源目录"""

	default_option = None

	res_root = None
	packing_root = None
	ignore_list=[]

	def __init__(self):
	    super(Xml2Mclib, self).__init__()
	    self.lock = Lock()
	    self.manager = Manager()
	    self.mclibInfos = self.manager.dict()

	def setResRoot(self,root):
		self.res_root = root
		pass
	def setPackingRoot(self,root):
		self.packing_root = root
		pass
	def setDefaultOption(self,option):
		self.default_option = option
		pass
	def trimMclib(self, mclib):
		fileInfo = mclib.get("fileInfo", None)
		if fileInfo:
			if "fileUpdateTime" in fileInfo:
				fileInfo.pop("fileUpdateTime")
			if "anirtoolVer" in fileInfo:
				fileInfo.pop("anirtoolVer")
		return mclib

	def addIndexInfo(self, resName, exportFilename, format, mclib):
		libItemDict = mclib.get("libItemDict", None)
		if not libItemDict:
			return
		mcnames = list(libItemDict.keys())
		with self.lock:
			encoded_exportFilename = utils.encodePath(exportFilename)
			self.mclibInfos[encoded_exportFilename] = (resName, format, mcnames)

	def saveAsJson(self, content, outpath, options):
		isCompactMode = options.get("compact", False)
		if isCompactMode:
			indent = None
			separators = (',', ':')
		else:
			indent = options.get("indent", 4)
			if indent<0: indent = None
			separators = (',', ': ')
		dirname,filename = os.path.split(outpath)
		if not os.path.exists(dirname):
			os.makedirs(dirname)
		with open(outpath, 'w') as f:
			f.write(json.dumps(content,indent = indent,separators = separators, sort_keys = True))

	def saveAsBinary(self,content,outpath,options):
		dirname,filename = os.path.split(outpath)
		if not os.path.exists(dirname):
			os.makedirs(dirname)
		with open(outpath,'wb') as f:
			AJ.writeFileHead()
			AJ.readFileDictX2MC(content)
			AJ.writeContenToFile(f)
		
		pass
	def guessPlistNameByRules(self,sourceName,options):
		nameSplit = sourceName.split(".")[0].split("_")
		plistname = nameSplit[len(nameSplit) -1 ]
		asset = options.get("asset","")
		plists= [] 
		plists.append(os.path.join(asset, plistname + ".plist"))
		return plists

	def go(self,config):

		for inputFilename in config['input']:
			logger.debug("Now converting "+inputFilename)
			name,ext = os.path.splitext(os.path.split(inputFilename)[1])
			outputFilename = os.path.join(utils.decodePath(config['output-root']),name+'.mclib')
			logger.debug("output flie name "+outputFilename)
			mclib = plistlib.readPlist(utils.decodePath(inputFilename))
			mclib = self.trimMclib(mclib)
			mclib['textures'] = []
			
			options = config['options']

			for key in list(mclib['libItemDict'].keys()):
				if 'sourceName' in mclib['libItemDict'][key]:
					sourceName = mclib['libItemDict'][key]['sourceName']
					if not sourceName == "":
						plist_name = self.guessPlistNameByRules(sourceName,options)
						if plist_name:
							for plist in plist_name:
								if not plist in mclib['textures']:
									mclib['textures'].append(plist)
									
			format = options.get("format", "json")
			format = format.lower()
			if format=="json":
				self.saveAsJson(mclib, outputFilename, options)
			elif format=="bin":
				extForOuputFile = ".bobj"
				outputFilename = os.path.join(utils.decodePath(config['output-root']),name+extForOuputFile)
				self.saveAsBinary(mclib,outputFilename, options)
			else:
				logger.error('不支持导出"%s"格式'%(format,))
				return False
