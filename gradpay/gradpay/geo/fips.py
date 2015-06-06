import os
import json

# Data from http://coastwatch.pfeg.noaa.gov/erddap/convert/fipscounty.json

path, _ = os.path.split(os.path.realpath(__file__))
filename = '%s/fips.json' % (path)

class Fips(object):

    def __init__(self, filename=filename):

        # Load JSON data
        with open(filename) as fh:
            self.data = json.load(fh)

        # Initialize maps
        self.map = {}
        self.map['state_to_code'] = {}
        self.map['code_to_state'] = {}
        self.map['count_to_code'] = {}
        self.map['code_to_count'] = {}

        cols = self.data['table']['columnNames']

        # Build maps
        for row in self.data['table']['rows']:
            vals = dict(zip(cols, row))
            name = vals['Name'].lower()
            code = vals['FIPS'].lower()
            if code.endswith('000'):
                code = code[:2]
                self.map['state_to_code'][name] = code
                self.map['code_to_state'][code] = name
            else:
                self.map['count_to_code'][name] = code
                self.map['code_to_count'][code] = name

    # Lookup functions

    def state_to_code(self, state):
        return self.map['state_to_code'].get(state.lower(), None)

    def count_to_code(self, count):
        return self.map['count_to_code'].get(count.lower(), None)

    def code_to_state(self, code):
        return self.map['code_to_state'].get(code, None)

    def code_to_count(self, code):
        return self.map['code_to_count'].get(code, None)
