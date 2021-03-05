import json
import math
import pybikes

from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.plotting import figure
from bokeh.tile_providers import get_provider, Vendors
from bokeh.models import GeoJSONDataSource


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
    y = math.log(math.tan(math.radians(lat) / 2.0 + math.pi / 4.0)) * radius

    return y, x


def gbsf_to_geojson(stations):
    # convert data to geojson format
    geo_dict = {}
    geo_dict['type'] = 'FeatureCollection'
    geo_dict['features'] = []
    for station in stations:
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

    return geo_source


def get_data():
    # get data in GBSF format
    capital = pybikes.get('capital-bikeshare')
    capital.update()
    stations = capital.stations
    geo_data = gbsf_to_geojson(stations)

    return geo_data


def make_map():
    tile_provider = get_provider(Vendors.STAMEN_TERRAIN_RETINA)

    p = figure(x_range=(-8596413.91, -8558195.48), y_range=(4724114.13, 4696902.60),
               x_axis_type="mercator", y_axis_type="mercator")
    p.add_tile(tile_provider)

    geo_data = get_data()

    p.circle(x='x', y='y', size=5, color='green', alpha=0.8, source=geo_data)

    return p


fig = make_map()
curdoc().add_root(column(fig))
