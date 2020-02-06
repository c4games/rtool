#coding=utf-8
from rtool import utils
from rtool.taskplugin.plugin.SampleAction import SampleAction

logger = logger = utils.getLogger('CustomAction')

def run_with_configs(configs,tp=None):
	logger.debug("Executing CustomAction")
	apaction = CustomPluginDemo()
	apaction.go(configs)
	pass

def clean_output(configs):
	default_output_path = configs["output-dir"]


class CustomPluginDemo(SampleAction):
	"""docstring for CustomPluginDemo"""

	def go(self,config):
		SampleAction.go(self,config)
		print "CustomPluginDemo "+config['options']['opt']
