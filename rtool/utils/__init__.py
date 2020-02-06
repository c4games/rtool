#coding=utf-8

import yaml
import os
import logging
import sys
import json
import subprocess
# reload(sys)
# sys.setdefaultencoding('utf8')
import rtool.ansistrm as am
import rtool.utils.MLogger


try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logger_list = []

def getLogger(name):
    logger = MLogger.MLogger(name)
    logger_list.append(logger)
    return logger


def setLoggerLevel(logger_level):
    for i in range(len(logger_list)):
        logger = logger_list[i]
        logger.setLevel(logger_level or logging.INFO)

main_config = None

logger = getLogger(__name__)

def dumpOptions(obj, logger):
    logger.info('Input Options:')
    for k in obj:
        v = obj[k]
        logger.info(k + " = " + str(v))

def is_true(v):
    return v=='1' or v=='yes' or v=='true' or v == True

def getMainConfig(key = None):
    global main_config
    if main_config == None:
        self_dir = os.path.dirname(os.path.abspath(__file__))
        self_dir = os.path.split(self_dir)[0]
        rc_group_dir =  os.path.dirname(os.path.dirname(self_dir))
        config_path = os.path.join(self_dir, 'config.yaml')
        # print(config_path)
        if not os.path.exists(config_path):
            config_path = os.path.join(rc_group_dir,'config.yaml')
            if not os.path.exists(config_path):
                logger.error(config_path)
                logger.error(u"config.yaml 文件不存在，需要将 config.example.yaml 复制为 config.yaml 并进行配置")
                exit()
        stream = open(config_path, 'rb')
        main_config = yaml.load(stream)
    if key != None:
        if key in main_config:
            return main_config[key]
        else:
            return None
    return main_config

project_config = None
personal_config = None

def getProjectConfig(key):
    global project_config
    global personal_config

    if personal_config == None:
        self_dir = os.path.dirname(os.path.abspath(__file__))
        self_dir = os.path.split(self_dir)[0]
        config_path = os.path.join(self_dir, 'config.personal.yaml')
        if os.path.exists(config_path):
            stream = open(config_path, 'rb')
            personal_config = yaml.load(stream)
        if personal_config == None:
            personal_config = {}
    if project_config == None:
        config = getMainConfig()
        project_name = config['project_name']
        self_dir = os.path.dirname(os.path.abspath(__file__))
        self_dir = os.path.split(self_dir)[0]
        config_path = os.path.join(self_dir, 'config.' + project_name + '.yaml')
        # print config_path
        if not os.path.exists(config_path):
            logger.error(config_path)
            logger.error("config.yaml 文件不存在，需要将 config.example.yaml 复制为 config.yaml 并进行配置")
            exit()
        stream = open(config_path, 'rb')
        project_config = yaml.load(stream)
        if project_config == None:
            project_config = {}
    if key != None:
        if key in personal_config:
            return personal_config[key]
        elif key in project_config:
            return project_config[key]
        else:
            return None
    return project_config

def setConfigRules(file_path):
    global config_rules
    config_rules = None
    if os.path.exists(file_path):
        stream = open(file_path, 'rb')
        config_rules = yaml.load(stream)
    if config_rules == None:
        logger.warning("未找到rules.cfg文件，使用默认配置")
        config_rules = {}
    return config_rules

def getConfigRules(key = None):
    global config_rules
    if key != None:
        if key in config_rules:
            return config_rules[key]
    else:
        return config_rules
    return None

def delete_file_by_name(filePath):
    if os.path.isfile(filePath):
        os.remove(filePath)

def remove_dir(dir_path):
    if not os.path.exists(dir_path):
        return
    dir_path = dir_path + os.sep
    list = os.listdir(dir_path)
    for li in list:
        filepath = os.path.join(dir_path,li)
        if os.path.isdir(filepath):
            remove_dir(filepath)
        elif os.path.isfile(filepath):
            os.remove(filepath)

        if os.path.exists(filepath):
            os.rmdir(filepath)

def getMtlCurPath():
    path = os.getcwd()
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

def writeJsonFileByDic(mainFileName,mainDic,formatJson=False):
    if not os.path.exists(os.path.dirname(mainFileName)):
        os.makedirs(os.path.dirname(mainFileName))

    mainFile = open(mainFileName,"w")
    if formatJson:
        jsonData = json.dumps(mainDic,sort_keys=True, indent=2)
    else:
        jsonData = json.dumps(mainDic,sort_keys=True)
    mainFile.truncate()
    mainFile.write(jsonData)
    mainFile.close()

def getJsonFileByFileName(fileName):
    dic_list={}
    #print fileName
    if os.path.exists(fileName):
        jsonFile = open(fileName)
        while True:
            line = jsonFile.readline()
            if len(line) == 0:
                break
            decoded = json.loads(line)
            for key,value in list(decoded.items()):
                dic_list[key] = value
        jsonFile.close()
    return dic_list

def get_all_file_list(find_dir, all_file_name, ext = None):
    file_list = os.listdir(find_dir)
    for file_name in file_list:
        file_path = os.path.join(find_dir,file_name)
        if os.path.isdir(file_path):
            get_all_file_list(file_path, all_file_name, ext)
        elif os.path.isfile(file_path):
            if ext == None or ext in os.path.splitext(file_path)[1]:
                all_file_name.append(file_path)

# 检测path_a是否是path_b的父路径
def is_parent_path(path_a,path_b):
    if path_a=="" or path_b=="":
        return False
    return path_b.replace(path_a,"***").split(os.path.sep)[0] == "***"
    pass

def get_username_from_tor_config(path):
    with open(path) as fp:
        line = fp.readline()
        while not line.strip()=="username" and not line=="":
            line = fp.readline()
        fp.readline()
        username = fp.readline()
        if not username=="":
            return username
    return None
def get_username_for_tortoiseSVN():
    username = None
    svn_config_dir = os.path.join(os.environ['APPDATA'],"Subversion","auth","svn.simple")
    if os.path.exists(svn_config_dir):
        file_list = os.listdir(svn_config_dir)
        for file in file_list:
            path = os.path.join(svn_config_dir,file)
            username = get_username_from_tor_config(path)
    return username

def get_svn_username(svn_path):
    username = "user"
    if sys.platform =="win32":
        username = get_username_for_tortoiseSVN()
        if not username:
            logger.warning("请输入用户名:")
            username = str(input())
    else:
        svn_root = runShell("svn info " + svn_path + " | awk -F 'Repository Root:' '{print $2}'|grep -v '^$'", False)
        svn_root = svn_root.strip()
        username = runShell("svn auth " + str(svn_root).split('/')[2] + " | awk -F 'Username:' '{print $2}'|grep -v '^$'", False)
        username = username.split('\n')
        if isinstance(username,(list)):
            return username[0].strip();
    return username.strip()

def get_svn_info(svn_path):
    if sys.platform =='win32':
        import pysvn
        entry = pysvn.Client().info(svn_path)
        svn_version = entry.commit_revision.number
        status = pysvn.Client().status(svn_path)
        svn_status = "\\n".join([st.path for st in status if st.text_status == pysvn.wc_status_kind.modified or st.text_status == pysvn.wc_status_kind.added])
        svn_status.replace(svn_path,'')
        return str(svn_version),svn_status
    else:
        svn_version = runShell("svn info " + svn_path + " | awk -F 'Revision:' '{print $2}'|grep -v '^$'", False)
        svn_version = svn_version.strip()
        svn_status = runShell("svn st " + svn_path + " | awk '{print $2}'|grep -v '^$'", False)
        svn_status = svn_status.replace(svn_path, '').replace('\n', '\\n')
        return svn_version, svn_status

def get_svn_diff_list(svn_path,revison_from,revison_to,options):
    username = options.get('svn_username',"")
    password = options.get('svn_password',"")
    auth_str=""
    if not username == "" and not password == "":
        auth_str = " --non-interactive --no-auth-cache --username "+username+" --password "+password
    cmd_r_str = runShell("svn diff -r "+revison_from+":"+revison_to+" --summarize "+svn_path+auth_str,False)
    st_p_list = []
    if cmd_r_str.startswith('svn: '):
        log.warning(cmd_r_str)
        log.warning("svn diff -r "+revison_from+":"+revison_to+" --summarize "+svn_path)
    else:
        # 由于美术资源命名不规范，可能在文件名中带有空格，因此要按下面方式处理diff_list
        item_list = cmd_r_str.split('\n')
        st_p_list = [(item.split('       ')[0],item.split('       ')[1]) for item in item_list if not item=='']
    return st_p_list
    pass

def get_svn_diff_xml_list(svn_path,revison_from,revison_to,options):
    username = options.get('svn_username',"")
    password = options.get('svn_password',"")
    auth_str=""
    if not username == "" and not password == "":
        auth_str = " --non-interactive --no-auth-cache --username "+username+" --password "+password
    cmd_r_str = runShell("svn diff -r "+revison_from+":"+revison_to+" --xml --summarize "+svn_path+auth_str,False)
    st_p_list = []
    if cmd_r_str.startswith('svn: '):
        log.warning(cmd_r_str)
        log.warning("svn diff -r "+revison_from+":"+revison_to+" --xml --summarize "+svn_path)
    else:
        # 由于美术资源命名不规范，可能在文件名中带有空格，因此要按下面方式处理diff_list
        root = ET.fromstring(cmd_r_str)
        for child in root:
            if child.tag == "paths":
                for p_child in child:
                    item = p_child.attrib['item']
                    kind = p_child.attrib['kind']
                    path = p_child.text
                    marker = 'M'
                    if item == 'deleted':
                        marker = 'D'
                    else:
                        marker = 'M'
                    st_p_list.append((marker,path))
    return st_p_list    
    pass

def runShell(cmd, noRet=True):
    if noRet:
        subprocess.check_call(cmd, shell=True);
    else:
        try:
            return str(subprocess.check_output(cmd, shell=True), encoding = "utf8");
        except Exception:
            return ""

def isGit(filePath):
	nums = runShell("cd %s"%filePath  + "  && git ls-files | awk '{print NR}' | tail -n1",False)
	if nums.strip() == '':
		return False;
	else:
		gitBranch = runShell('cd %s'%filePath + "&& git branch | grep '^\*' | awk '{print $2}'",False)
		return True;

def zipDir(source_dir,zip_name):
    import zipfile
    with zipfile.ZipFile(zip_name,"w",zipfile.ZIP_DEFLATED) as zip:
        for parent,dirnames,filenames in os.walk(source_dir):
            for filename in filenames:
                # print "压缩 "+filename
                zip.write(os.path.join(parent,filename),os.path.relpath(os.path.join(parent,filename),source_dir))
    pass
    
def getChangedDirs(path,timestamp):
    _dir = path
    dirs = (os.path.join(rt,dirname) for rt, dirnames, _ in os.walk(_dir) for dirname in dirnames if os.path.isdir(os.path.join(rt, dirname)) and os.stat(os.path.join(rt, dirname)).st_mtime - timestamp >10)
    return list(dirs)

# 获取a路径相对于b路径的相对路径在新的根目录下，组合生成的新路径，主要用于资源处理依赖其他资源生成操作产生的资源路径
def getRelPathWithOtherRoot(a_path,b_path,new_root):
    rel_path_other_root = ""
    if not a_path == b_path:
        rel_path = a_path.replace(b_path+os.sep,'')
        if sys.platform == 'win32':
            try:
                rel_path = rel_path.decode('gbk')
            except Exception:
                pass
            else:
                pass
        rel_path_other_root = os.path.join(new_root,rel_path)
    else:
        rel_path_other_root = new_root
    return rel_path_other_root
# os.path 的相对路径函数在生成相对路径时会有路径有时带分割符有时不带的问题，因此需要自己写一个
def getRelPath(a_path,b_path):
    rel_path =""
    if not a_path == b_path:
        rel_path = a_path.replace(b_path+os.sep,'')
    return rel_path
""" 
lixu 20180130
windows默认的编码是cp1252，windows的控制台程序需要此编码路径，python中的数据结构在存储字符串时是以assii形式存储的
因此json，yaml，plist，logger等库在处理汉字路径时会遇到不同的问题，例如路径截断或编码错误
目前的解决方案是在需要内部结构－》序列化结构的时候用encodePath处理路径，在使用控制台工具时使用decodePath
lixu 20181126
更新：根据最新的测试，python3中window上的编码问题已经消失，不再需要手动进行编解码
"""
def encodePath(text):
    # if sys.platform == "win32":
    #     return text.decode('cp936').encode('utf-8')
    # else:
    return text

def decodePath(text):
    # if sys.platform == "win32":
    #     return text.decode('utf-8').encode('cp936')
    # else:
    return text

def getMergeCfg(merge_dict_path):
    # config = getMainConfig()
    # project_name = config['project_name']
    # self_dir = os.path.dirname(os.path.abspath(__file__))
    # merge_dict_path = os.path.join(self_dir,'projects',project_name,'config',file_name)
    logger.info(merge_dict_path);
    merge_dict = None
    if os.path.exists(merge_dict_path):
        with open(merge_dict_path,'rb') as f:
            merge_dict = yaml.load(f)
    return merge_dict

def parseJsonOptions(json_str,options):
    options['dev']=False
    if not json_str == '':
        json_dict = json.loads(json_str)
        for key in list(json_dict.keys()):
            options[key] = json_dict[key]
        # 对于有主升级序列的情况使用主升级序列，插队没有主升级序列的情况使用当前升级序列名称
        options['upgrade_path'] = json_dict.get('coreUpgradePath',options['target'])
        options['target'] = json_dict.get('os_platform','iOS')
        runorder = []
        raw_runorder = json_dict.get('runorder',"").split(',')
        runorder = [action.strip() for action in raw_runorder]
        if not runorder == ['']:
            options['runorder'] = runorder
    return options

# subprocess.commmunicate()返回结果的处理方法，根据参数类型返回适合输出log的字符串
def getStrFromOutput(obj):
    if isinstance(obj,str):
        return obj
    elif isinstance(obj,bytes):
        return str(obj.decode('utf-8'))
    else:
        return str(obj)

