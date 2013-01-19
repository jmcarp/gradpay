# 
import json
import argparse

parser = argparse.ArgumentParser(description='Combine JSON files.')
parser.add_argument('files', nargs='+')

args = parser.parse_args()

jdata = []
for jfile in args.files:
  filedata = json.load(open(jfile))
  jdata.extend(filedata)

print json.dumps(jdata, indent=2)
