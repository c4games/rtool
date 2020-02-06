#coding=utf-8
import imp 
def invokeAction(taskname,module,plugindir,configs,tp=None):
	dirlist=[]
	dirlist.append(plugindir)
	file,pathname,dec = imp.find_module(module,dirlist)
	taskModule = imp.load_module(module,file,pathname,dec)
	taskModule.run_with_configs(configs,tp)
	pass

def invokeClean(taskname,module,plugindir,configs):
	dirlist=[]
	dirlist.append(plugindir)
	file,pathname,dec = imp.find_module(module,dirlist)
	taskModule = imp.load_module(module,file,pathname,dec)
	taskModule.clean_output(configs)
	pass
