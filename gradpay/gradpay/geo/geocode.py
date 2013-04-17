# Imports
import time
from pygeocoder import Geocoder, GeocoderError

# Project imports
import fips

f = fips.Fips()

def geocode_institution(name, city, state):
    
    query = ', '.join([name, city, state])

    try:
        geo = Geocoder.geocode(query)
        time.sleep(2.5)
    except GeocoderError as e:
        return '', ''

    for result in geo.data:
        for comp in result['address_components']:
            if 'administrative_area_level_2' in comp['types']:
                county = comp['long_name']
                break
    
    if 'county' not in locals():
        return '', ''
    
    code = f.count_to_code(
        ('%s, %s' % (state, county)).lower()
    )

    return county, code
