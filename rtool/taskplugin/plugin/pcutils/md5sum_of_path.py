#coding=utf8
import hashlib
import os


def md5_for_file(orig_data):
    md5 = hashlib.md5()
    block_size=2**20
    f = open(orig_data, 'rb')
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    f.close()
    return md5.hexdigest()


def md5_for_str(s):
    md5 = hashlib.md5()
    md5.update(s.encode('utf-8'))
    return md5.hexdigest()


def md5sum_of_path(paths, extensions = None):
    """计算指定路径下所有文件的  文件名和内容的md5sum

    只有所有文件的内容和文件名都一致时, 得出的md5才会相同
    """
    if type(paths) == str:
        paths = [paths]
    md5_str = ""
    img_list = []
    for fORd in paths:
        if not os.path.exists(fORd):
            # raise Exception(fORd + " not exist") 
            print("fORd not exist "+fORd) 
        if os.path.isfile(fORd):
            img_list.append(fORd)
        else:
            for rt, dirs, files in os.walk(fORd):
                for f in files:
                    suffix = os.path.splitext(f)[1]
                    if extensions == None or suffix in extensions:
                        img_list.append(os.path.join(rt,f))

    if len(img_list) == 0:
        return None

    img_list.sort()
    for img in img_list:
        md5_str += os.path.basename(img)
        md5_str += md5_for_file(img)
    return md5_for_str(md5_str)

def md5sum_of_IOpath(input_file_list,options,paths, extensions = None):
    """
        加入输入文件列表的文件名一起计算，这样输入或输出资源发生变动时都能反应在md5值上
    """
    if type(paths) == str:
        paths = [paths]
    md5_str = ""
    img_list = []
    for fORd in paths:
        if not os.path.exists(fORd):
            if os.path.isfile(fORd):
                img_list.append(fORd)
            else:
                for rt, dirs, files in os.walk(fORd):
                    for f in files:
                        suffix = os.path.splitext(f)[1]
                        if extensions == None or suffix in extensions:
                            img_list.append(os.path.join(rt,f))

    if len(img_list) == 0:
        md5_str = "nooutput"
        if input_file_list:
            for img_path in input_file_list:
                md5_str+= md5_for_file(img_path)
    else:
        img_list.sort()
        for img in img_list:
            md5_str += os.path.basename(img)
            md5_str += md5_for_file(img)
            if input_file_list:
                for img_path in input_file_list:
                    md5_str += md5_for_file(img_path)
    md5_str += str(options)
    return md5_for_str(md5_str)

if __name__ == '__main__':
    print(md5sum_of_path('/data/work/walle/kof/asset/Assets/anim/UI特效/p爬塔/F波动画',['.png']))
    print(md5sum_of_path('/data/work/walle/kof/asset/Assets/anim/UI特效/p爬塔/F波动画',['.plist']))
    print(md5sum_of_path('/data/work/walle/kof/asset/Assets/anim/UI特效/p爬塔/F波动画'))

