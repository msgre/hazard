import urllib
from utils import simplejson, geocoder_factory

# https://developers.google.com/maps/documentation/geocoding/#ReverseGeocoding
def geocode(lat, lon):
    json = simplejson.load(urllib.urlopen(
        'http://maps.googleapis.com/maps/api/geocode/json?' + urllib.urlencode({
            'latlng': '%s,%s' % (lat, lon),
            'sensor': 'false',
            'language': 'cs'
        })
    ))
    return json

geocoder = geocoder_factory(geocode)
