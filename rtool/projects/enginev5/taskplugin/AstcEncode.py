#coding=utf-8
from rtool import utils
from rtool.taskplugin.plugin.SampleAction import SampleAction

logger = logger = utils.getLogger('CustomAction')

def run_with_configs(configs,tp=None):
	logger.debug("Executing CustomAction")
	apaction = AstcEncode()
	apaction.go(configs)
	pass

def clean_output(configs):
	default_output_path = configs["output-dir"]


class AstcEncode(SampleAction):
	"""docstring for AstcEncode"""

	def go(self,config):
		SampleAction.go(self,config)
		logger.debug("AstcEncode "+config['options']['opt'])
