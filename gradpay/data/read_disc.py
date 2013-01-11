
import json
import xlrd

def read_disc(discname):
  
  book = xlrd.open_workbook(discname)
  sheet = book.sheet_by_index(0)
  
  discs = []

  for rowidx in range(2, sheet.nrows - 1):
    
    values = sheet.row_values(rowidx)
    next_values = sheet.row_values(rowidx + 1)

    if not any(next_values):
      rowidx += 2
      continue

    if values[0]:
      discs.append(values[0].strip())

  return discs

def disc_to_json(discs, model, outname):
  
  discdicts = []

  for discidx in range(len(discs)):
    
    discdict = {}

    discdict['pk'] = discidx + 1
    discdict['model'] = model
    discdict['fields'] = {
      'name' : discs[discidx]
    }

    discdicts.append(discdict)
  
  out = open(outname, 'w')
  json.dump(discdicts, out, indent=2)
  out.close()
