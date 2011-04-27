import urllib
from utils import simplejson, geocoder_factory

# http://code.google.com/apis/maps/documentation/geocoding/index.html

def geocode(q, api_key):
    json = simplejson.load(urllib.urlopen(
        'http://maps.google.com/maps/geo?' + urllib.urlencode({
            'q': q.encode('utf-8'),
            'output': 'json',
            'oe': 'utf8',
            'sensor': 'false',
            'key': api_key,
            'hl': 'cs'
        })
    ))
    return json

geocoder = geocoder_factory(geocode)
