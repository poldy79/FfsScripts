'''
Created on Oct 20, 2016

@author: leonard
'''

import json
import types
import sys

def importJson():
    fp = open("test.json","rb")
    data = json.load(fp)
    fp.close()
    return data

def walk(input, prefix = None):
    output = []
    if prefix == None:
        prefix = ""
    for item in input:
        d = input[item]
        if type(d) is types.IntType:
            output.append((prefix+"."+item,d))
        elif type(d) is types.DictType:
            output += walk(d,prefix+"."+item)
        elif type(d) is types.UnicodeType:
            output.append((prefix+"."+item,d))
        elif type(d) is types.ListType:
            if len(d) >0:
                output.append(((prefix+"."+item,d[0])))
            #print "list: %s %s"%(item,d)
        elif type(d) is  types.NoneType:
            output.append((prefix+"."+item,"None"))
        else:
            print "Unknown Type"
            print type(d)            
            sys.exit(1)
            
    return output

if __name__ == '__main__':
    data = importJson()
    result = walk(data,"fastd")
    for i in result:
        print i