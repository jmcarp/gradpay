# Imports
import json

datadir = '/Users/jmcarp/Dropbox/projects/gradpay/gradpay/data'
supportname = '%s/raw/support.csv' % (datadir)

def support_to_json(supportname, model, outname):
  
  supports = open(supportname, 'r').readlines()
  
  supportdicts = []

  for supportidx in range(len(supports)):
    
    supportline = supports[supportidx]
    supportvals = supportline.split(';')

    supportdict = {}
    supportdict['pk'] = supportidx + 1
    supportdict['model'] = model
    supportdict['fields'] = {
      'name' : supportvals[0].strip(),
      'tooltip' : supportvals[1].strip(),
    }

    supportdicts.append(supportdict)

  out = open(outname, 'w')
  json.dump(supportdicts, out, indent=2)
  out.close()

if __name__ == '__main__':
  support_to_json(supportname, 'gradpay.support', '%s/initial_support.json' % (datadir))
