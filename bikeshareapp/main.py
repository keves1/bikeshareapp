from bokeh.plotting import figure, curdoc
from bokeh.layouts import column
from bokeh.tile_providers import get_provider, Vendors
from bokeh.models import GeoJSONDataSource
from bokeh.models.tools import BoxZoomTool
import json
import math
import pybikes


def latlon_to_mercator(lat, lon):
    """
    Converts coordinates from latitude/longitude to web mercator coordinates
    Derived from the Java version shown here: http://wiki.openstreetmap.org/wiki/Mercator
    :param lat:
    :param lon:
    :return:
    """

    radius = 6378137.0
    x = math.radians(lon) * radius
    y = math.log(math.tan(math.radians(lat) / 2.0 + math.pi/4.0)) * radius

    return y, x


tile_provider = get_provider(Vendors.STAMEN_TERRAIN_RETINA)

# range bounds supplied in web mercator coordinates
p = figure(x_range=(-13650000.00, -13600000.00), y_range=(4549761.18, 4540000.00),
           x_axis_type="mercator", y_axis_type="mercator")
BoxZoomTool.match_aspect = True
p.add_tile(tile_provider)

# get data in GBSF format
bay_wheels = pybikes.get('bay-wheels')
bay_wheels.update()

# convert data to geojson format
geo_dict = {}
geo_dict['type'] = 'FeatureCollection'
geo_dict['features'] = []
for station in bay_wheels.stations:
    station_dict = {}
    station.latitude, station.longitude = latlon_to_mercator(station.latitude, station.longitude)
    station_dict['geometry'] = {'type': 'Point', 'coordinates': [station.longitude, station.latitude]}
    station_dict['type'] = 'Feature'
    station_dict['id'] = station.extra['uid']
    station_dict['properties'] = {'station name': station.name,
                                  'bikes': station.bikes,
                                  'free': station.free}
    geo_dict['features'].append(station_dict)

geo_source = GeoJSONDataSource(geojson=json.dumps(geo_dict))

p.circle(x='x', y='y', size=5, color='green', alpha=0.8, source=geo_source)

curdoc().add_root(column(p))
