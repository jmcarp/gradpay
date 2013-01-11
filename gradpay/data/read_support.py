# Imports
import json

def support_to_json(supportname, model, outname):
  
  supports = open(supportname, 'r').readlines()
  
  supportdicts = []

  for supportidx in range(len(supports)):

    supportdict = {}
    supportdict['pk'] = supportidx + 1
    supportdict['model'] = model
    supportdict['fields'] = {
      'name' : supports[supportidx].strip(),
    }

    supportdicts.append(supportdict)

  out = open(outname, 'w')
  json.dump(supportdicts, out, indent=2)
  out.close()
