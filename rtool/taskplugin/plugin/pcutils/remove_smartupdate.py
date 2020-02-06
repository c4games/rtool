#coding=utf8
import plistlib
import json

def remove_smartupdate_from_plist_or_json(filename):
    try:
        d = plistlib.readPlist(filename)
        d['metadata']['smartupdate'] = ''
        plistlib.writePlist(d,filename)
    except Exception as ex:
        # xml.parsers.expat.ExpatError: not well-formed (invalid token): line 1, column 0
        if ex.message.startswith('not well-formed'):
            with open(filename) as f:
                d = json.load(f)
                d['meta']['smartupdate'] = ''
                json.dump(d,open(filename,'w'))
        else:
            raise ex

def remove_smartupdate_from_plist_or_json_then_rename(filename,rename):
    try:
        d = plistlib.readPlist(filename)
        d['metadata']['smartupdate'] = ''
        d['metadata']['textureFileName'] = rename+'.png'
        d['metadata']['realTextureFileName'] = rename+'.png'
        plistlib.writePlist(d,filename)
    except Exception as ex:
        # xml.parsers.expat.ExpatError: not well-formed (invalid token): line 1, column 0
        if ex.message.startswith('not well-formed'):
            with open(filename) as f:
                d = json.load(f)
                d['meta']['smartupdate'] = ''
                d['meta']['textureFileName'] = rename+'.png'
                d['meta']['realTextureFileName'] = rename+'.png'
                json.dump(d,open(filename,'w'))
        else:
            raise ex
