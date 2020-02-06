#coding=utf-8
import yaml
import logging
import click
import rtool.utils as mut
import os
import os.path
import sys
import json
import imp

import rtool.pcutils.md5sum_of_path as mput
import rtool.res.TPCache2 as TPCache2
import rtool.res.TPTask as TPTask
import rtool.tasks.BaseSync as BS
import rtool.tasks.BaseStatus as BStatus

import rtool.taskplugin.plugin.TPDirFormater as TPDF


logger = mut.getLogger('Task')

class TaskContext(object):
    def __init__(self):
        self.taskName=""
        # self.logger = mut.getLogger(self.taskName)
        self.settings = None
        self.options = None
        pass

    def getLogger(self):
        return logger

    def getEnv(self, name):
        # get environment variable with `name`
        return os.getenv(name)

    # `settings`: a dict that contains project settings
    def setSettings(self, settings):
        self.settings = settings
    def getSettings(self):
        return self.settings
    def getSettingValue(self, name):
        # return setting value with `name`
        if self.settings!=None and name in self.settings:
            return self.settings[name]
        return None

    # `options`: a dict that contains task options
    def setOptions(self, options):
        self.options = options
    def getOptions(self):
        return self.options
    def getOptionValue(self, name):
        if self.options!=None and name in self.options:
            return self.options[name]
        return None


class AbstractTask(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.logger = self.ctx.getLogger()
    def log(level, msg):
        if self.logger!=None:
            # TODO add log item to logger
            pass
    def runCommand(self, cmd, options):

        pass
    def execAction(self, options):

        return True
    def preAction(self,options):
        return True
    def postAction(self,options):
        return True


class TaskRegistry(object):
    def __init__(self):
        pass
    def registTask(self, name, taskClazzOrCreateFunc):
        pass
    def createTask(self, name, ctx):
        return None

class TaskFactory(object):
    """docstring for TaskFactory"""
    def __init__(self,task_context):
        super(TaskFactory, self).__init__()
        self.ctx = task_context

    def genTask(self,project_name=None):

        task_name = self.ctx.taskName
        options = self.ctx.options

        if not project_name:
            project_name = mut.getMainConfig('project_name')

        if project_name:
            dir_list = []
            pwd = os.path.dirname(os.path.abspath(__file__))
            rtool_dir = os.path.dirname(pwd)
            project_dir = os.path.join(rtool_dir,'projects',project_name)
            print("project_dir" + project_dir)
            dir_list.append(project_dir)
            file,pathname,dec  = imp.find_module("task",dir_list)
            task_module = imp.load_module("task",file,pathname,dec)
            return task_module.getInstance(self.ctx)


        pass


@click.command()
@click.option('-i','--input',required=True,help='资源根目录(必须)')
@click.option('-o','--output',required=True,help='资源处理的输出路径根目录（必须）')
@click.option('-g','--game',required=True,help='执行哪一个游戏项目的task（必须）')
@click.option('-p','--path',default="",help='rtool路径')
@click.option('-sc','--svn_commit',default="0",help='最近一次svn提交')
@click.option('-lsc','--last_svn_commit',default="0",help='上一次svn提交')
@click.option('-svn','--svn',default="",help="svn地址")
@click.option('-su','--svn_username',default="",help="svn登录用户名")
@click.option('-sp','--svn_password',default="",help="svn登录密码")
@click.option('-t','--target',default='iOS',help='资源处理对应的平台，默认为‘iOS’，可以是iOS,Android,ANY等,在.rtool目录中的settings.yaml中设置')
@click.option('-c','--clean',default=False,help='清理资源输出')
@click.option('-fcc','--forcecleancache',default=False,help='强制清理缓存')
@click.option('-ic','--imgincsd',default='',help='根据传入目录路径递归遍历子目录分析csd文件中使用的图片')
@click.option('-ig','--ignore',default='',help='根据传入路径生成.ignore文件，用于各个action中屏蔽文件或目录')
@click.option('-d/-nd', '--debug', default = False, help='默认为False，设置默认是否输出DEBUG级的log')
@click.option('-cd', '--cachedir', default = '', help='缓存路径')
@click.option('-cp','--configpath',default = '',help='策划配置文件资源路径')
@click.option('-an','--actionName',default = '',help='指定执行Action的名称，可以用,分隔，按照传入顺序执行')
@click.option('-ck/-nck','--check',default=False,help='检测局部配置文件是否有格式错误，并将globalDict输出至globaldictXLS.xlsx')
@click.option('-wj','--walle_json',default = '',help='walleui向rtool传递参数使用json传递')
@click.option('-rv','--run_version',default = 'publish',help='task执行插件的顺序，覆盖settings.yaml中的runorder设置，配置名称在config.xxx.yaml中runorder_version')
@click.option('-nrc','--norc',default=False,help='不使用rc并且进行全量执行')
def run(**options):
    '''
        发布模式, 需要配置路径，例如：
        rtl task -p /Users/xxxxxx/Desktop/TaskExample/SampleAssets/svn -i /Users/xxxxxx/Desktop/TaskExample/SampleAssets -t android -o /Users/xxxxxx/Desktop/TaskExample/SampleAssets/svn/output -cd /data/work/src/dzm2/svn/tmp
    '''
    # logger.setLevel(options['debug'] and logging.DEBUG or logging.INFO)
    options = mut.parseJsonOptions(options.get('walle_json',''),options)
    options['dev'] = False
    if options['path'] =="":
        pwd = os.path.dirname(os.path.abspath(__file__))
        rtool_dir = os.path.dirname(pwd)
        options['path'] = rtool_dir
    if not options.get('actionname',"")=="":
        options['runorder'] = [act.strip() for act in options['actionname'].split(',')]
    if options.get('cachedir')=='':
        output_path = options['output']
        output_base = os.path.split(output_path)[0]
        options['cachedir']=os.path.join(output_base,'temp')
    logger.debug("-----rtool command line arguments----")
    logger.debug(json.dumps(options,indent=2))
    logger.debug("-------------------------------------")
    # tpcache_root = os.path.join(options['cachedir'],'tpchache')
    # TPDF.format_tp_dir(tpcache_root)
    # TPDF.format_local_db(tpcache_root)
    # print "task.run"
    # print mut.getMtlCurPath()
    # detectConfigPaths(options["path"])
    if options.get('norc',False) == True:
        # 如果不使用RC处理，那就是全量处理
        options['all'] == True

    bstatus = None
    if not options.get('norc',False):
        bstatus = BStatus.BaseStatus(options)
        # 由于rc是在svndiff的基础上做增量的，因此历史版本号和当前版本号相同的情况是错误的
        if options['last_svn_commit'] == options['svn_commit']:
            logger.error("last_svn_commit should not equal to svn_commit!")
            bstatus.doError()

    tp_task_ctx = TaskContext()
    tp_task_ctx.setOptions(options)
    # tp_task = TPTask(tp_task_ctx)
    tf = TaskFactory(tp_task_ctx)
    tp_task = tf.genTask(options['game'])
    if not options.get('norc',False):
        bs = BS.BaseSync(options)
        bs.get_db_conn(BS.DB_CONFIG)
        logger.debug("get db conn")
        bs.init_db()
        bs.init_local_db()    
        logger.debug("init_db")
        bs.RC2TPLocal()
        logger.debug("sync TPCache2 files to local finished")
        bs.syncCacheDataLocal()
        logger.debug("sync TPCache2 data to local finished")
        if options.get("clone","0") == "1":
            bs.deleteAssetsWithTag(options['svn_commit'])
    tp_task.preAction(options)
    logger.debug("preAction")    
    tp_task.execAction(options)
    logger.debug("execAction")
    tp_task.postAction(options)
    logger.debug("postAction")
    if not options.get('norc',False):    
        bs.syncAssetsRcFast()
        logger.debug("sync assets finished")
        bs.TPLocal2RC()
        logger.debug("sync TPCache2 files to rc finished")
        bs.syncCacheDataRemote()
        logger.debug("sync TPCache2 data to remote finished")
        bs.close_db_conn()
        logger.debug("db conn closed")
        bstatus = BStatus.BaseStatus(options)
        bstatus.doNormalFininsh()


def runflash_dev(options):

    logger.setLevel(options['debug'] and logging.DEBUG or logging.INFO)
    mut.dumpOptions(options, logger)

    input_root = mut.getProjectConfig('input_root')
    if options["mode"] != None :
        tempPath = input_root  + "_" + options["mode"]
        if os.path.exists(tempPath):
            input_root = tempPath
            
    rtool_root = mut.getProjectConfig('rtool_root')
    output_root = mut.getProjectConfig('output_root')
    cache_dir = mut.getProjectConfig('cache_dir')
    if options['path'] == '':
        options['path'] = rtool_root
    if options['input'] == '':
        options['input'] = os.path.join(input_root)
    if options['output'] == '':
        options['output'] = os.path.join(output_root)
    if options['cachedir'] =='':
        options['cachedir'] = cache_dir
    if options['game'] == '':
        options['game'] = mut.getMainConfig('project_name')
    options['dev'] = True
    options['norc'] = True
    options['all'] = True
    tp_task_ctx = TaskContext()
    tp_task_ctx.setOptions(options)
    # tp_task = TPTask(tp_task_ctx)
    tf = TaskFactory(tp_task_ctx)
    tp_task = tf.genTask(options['game'])
    tp_task.preAction(options)
    if not options['check']:
        tp_task.execAction(options)
        tp_task.postAction(options)

    #upload(pathData)

@click.command()
@click.option('-i','--input',default="",help='资源根目录(必须)')
@click.option('-o','--output',default="",help='资源处理的输出路径根目录（必须）')
@click.option('-g','--game',default="",help='执行哪一个游戏项目的task（必须）')
@click.option('-p','--path',default="",help='rtool路径')
@click.option('-sc','--svn_commit',default="0",help='最近一次svn提交')
@click.option('-lsc','--last_svn_commit',default="0",help='上一次svn提交')
@click.option('-svn','--svn',default="",help="svn地址")
@click.option('-su','--svn_username',default="",help="svn登录用户名")
@click.option('-sp','--svn_password',default="",help="svn登录密码")
@click.option('-t','--target',default='iOS',help='资源处理对应的平台，默认为‘iOS’，可以是iOS,Android,ANY等,在.rtool目录中的settings.yaml中设置')
@click.option('-c','--clean',default=False,help='清理资源输出')
@click.option('-fcc','--forcecleancache',default=False,help='强制清理缓存')
@click.option('-ic','--imgincsd',default='',help='根据传入目录路径递归遍历子目录分析csd文件中使用的图片')
@click.option('-ig','--ignore',default='',help='根据传入路径生成.ignore文件，用于各个action中屏蔽文件或目录')
@click.option('-d/-nd', '--debug', default = False, help='默认为False，设置默认是否输出DEBUG级的log')
@click.option('-cd', '--cachedir', default = '', help='缓存路径')
@click.option('-an','--actionname',default = '',help='指定执行Action的名称，可以用,分隔，按照传入顺序执行')
@click.option('-ck/-nck','--check',default=False,help='检测局部配置文件是否有格式错误，并将globalDict输出至globaldictXLS.xlsx')
@click.option('-wj','--walle_json',default = '',help='walleui向rtool传递参数使用json传递')
def run_dev(**options):
    '''
        开发模式, 用于线下开发
        请于config.yaml中配置input_root，output_root，rtool_root和cache_dir
    '''
    runflash_dev(options)

def main():
    print("hello, world")

if __name__ == '__main__':
    main()
