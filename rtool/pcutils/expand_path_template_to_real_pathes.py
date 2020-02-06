#coding=utf8
import os

def expand_path_template_to_real_pathes(path_template):
    if path_template.find('{n}') == -1:
        return [ path_template ]

    pathes = []
    i=0
    path_i = path_template.replace('{n}',str(i))
    while os.path.exists(path_i):
        pathes.append(path_i)
        i+=1
        path_i = path_template.replace('{n}',str(i))
    return pathes

def expand_path_template_to_pathes(path_template,cnt):
    if path_template.find('{n}') == -1:
        return [ path_template ]
    pathes = []
    for i in range(cnt):
        path_i = path_template.replace('{n}',str(i))
        pathes.append(path_i)
    return pathes
