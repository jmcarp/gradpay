
# 
import json
import pandas as pd

datadir = '/Users/jmcarp/Dropbox/projects/gradpay/gradpay/data'
uniname = '%s/raw/cc2010_classification_data_file_11.07.2012.xls' % (datadir)

CATEGORIES = (
  'Research Universities',
  'Master\'s'
)

def read_uni(uni):
  """
  Read universities from .xls file to DataFrame
  """
  
  excel = pd.ExcelFile(uni)

  labels = excel.parse('Labels')

  # 
  for rowidx in range(len(labels)):
    value = labels['Variable'][rowidx]
    if hasattr(value, 'startswith') and value.startswith('ipug2010'):
      break
  
  # 
  labels = labels.ix[:rowidx-1]
  
  incidx = pd.Series([False] * labels.shape[0])
  for cat in CATEGORIES:
    incidx = incidx | (labels['Label'].str.contains(cat) == True)

  ccbasic = labels['Value'][incidx]

  # 
  data = excel.parse('Data')

  data = data.ix[pd.lib.ismember(data['CCBASIC'], set(ccbasic))]

  data = pd.merge(data, labels, left_on='CCBASIC', right_on='Value')

  return data

uni_map = {
  'NAME' : 'name',
  'CITY' : 'city',
  'STABBR' : 'state',
  'Label' : 'category',
}

def uni_to_json(uni, model, outname):
  """
  Write universities to JSON
  """
  
  # Initialize JSON
  rowdicts = []

  # Cast DataFrame rows to JSON
  for rowidx in range(len(uni)):
    row = uni.ix[rowidx]
    rowdict = {}
    rowdict['model'] = model
    rowdict['pk'] = rowidx + 1
    rowdict['fields'] = dict([(uni_map[key], row[key]) for key in uni_map])
    rowdicts.append(rowdict)

  # Open output file
  out = open(outname, 'w')

  # Write JSON to file
  json.dump(rowdicts, out, indent=2)

  # Close output file
  out.close()

if __name__ == '__main__':
  uni = read_uni(uniname)
  uni_to_json(uni, 'gradpay.institution', '%s/json/initial_institution.json' % (datadir))
