#coding=utf-8
import sys
import requests
import hashlib
from rtool import utils
from rtool.tasks.Base import Base

logger = utils.getLogger("BaseStatus")

class BaseStatus(Base):
	"""docstring for BaseStatus"""
	def __init__(self,options):
		super(BaseStatus, self).__init__(options)
		self.options = options
		self.key = ""
		self.url = "" 

	def doAPIRequest(self,tid,status):
		game = self.options['game']
		token_str = tid+status+game+self.key
		md5 = hashlib.md5()
		md5.update(token_str.encode('utf-8'))
		token = md5.hexdigest()
		payload={}
		payload['id'] = tid
		payload['status'] = status
		payload['game'] = game
		payload['token'] = token
		r = requests.get(self.url,params=payload)
		print(r.status_code)
		print(r.content)
		if r.status_code == requests.codes.ok:
			logger.debug("任务%s发送状态%s完成"%(tid,status))
		else:
			logger.warning("任务%s发送状态%s失败"%(tid,status))
			logger.debug(r.status_code)
			logger.debug(r.content)

	def doNormalFininsh(self):
		if not self.options['dev'] and not self.options['norc']:
			tid = str(self.options['id'])
			self.doAPIRequest(tid,"2")
			logger.debug("任务正常结束")

	def doError(self):
		if not self.options['dev'] and not self.options['norc']:
			tid = str(self.options['id'])
			self.doAPIRequest(tid,"3")
			logger.error("任务异常")
			sys.exit(1)


if __name__ == '__main__':
	options={}
	options['game'] = 'demos'
	options['id'] = "1"
	bstatus = BaseStatus(options)
	bstatus.doNormalFininsh()
	# bstatus.doError()	