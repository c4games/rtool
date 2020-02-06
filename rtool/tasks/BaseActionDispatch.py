#coding=utf-8
import os
import os.path
import imp
import rtool.utils as mut

logger = mut.getLogger('BaseActionDispatch')

class BaseActionDispatch(object):
	"""docstring for BaseActionDispatch"""
	def __init__(self):
		super(BaseActionDispatch, self).__init__()
		self.plugindir=[]

	def set_plugin_dir(self,plugindir):
		self.plugindir = plugindir

	def invokeAction(self,module,configs,tp=None,plugindir=[]):
		dirlist=[]
		if len(plugindir)>0:
			dirlist = plugindir
		else:
			dirlist = self.plugindir
		if not len(dirlist)>0:
			logger.warning(u"插件目录未设置")
			return
		file,pathname,dec = imp.find_module(module,dirlist)
		taskModule = imp.load_module(module,file,pathname,dec)
		taskModule.run_with_configs(configs,tp)
		pass

	def invokeClean(self,module,configs,plugindir=[]):
		dirlist=[]
		if len(plugindir)>0:
			dirlist = plugindir
		else:
			dirlist = self.plugindir
		if not dirlist>0:
			logger.warning(u"插件目录未设置")
			return
		file,pathname,dec = imp.find_module(module,dirlist)
		taskModule = imp.load_module(module,file,pathname,dec)
		taskModule.clean_output(configs)
		pass
