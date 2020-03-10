#!/usr/bin/python
import json
import glob
import argparse
parser = argparse.ArgumentParser(description='Update nodes json file')

parser.add_argument('--output', dest='output', action='store',
                                required=True,
                                                   help='output file')

parser.add_argument('--input', dest='input', action='store',
                                required=True,
                                                   help='input file patern')

args = parser.parse_args()


inputFiles = glob.glob(args.input)
data = {}
for i in inputFiles:
    try:
        with open(i,"rb") as fp:
            j = json.load(fp)
        data.update(j)
    except:
        print("Unable to open %s "%(i))
        pass


des_all = open(args.output,"wb")
des_all.write( json.dumps(data,sort_keys=True, indent=4, separators=(',', ': ')))
des_all.close()
