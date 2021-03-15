import json
import math
import pybikes

from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.plotting import figure
from bokeh.tile_providers import get_provider, Vendors
from bokeh.models import GeoJSONDataSource, ColorBar, LinearColorMapper, Label
from bokeh.palettes import viridis


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


def color(percent_full):
    idx = int(percent_full*255)
    colors = viridis(256)
    color = colors[idx]

    return color


def gbsf_to_geojson(stations):
    # convert data to geojson format
    geo_dict = {}
    geo_dict['type'] = 'FeatureCollection'
    geo_dict['features'] = []
    for station in stations:
        station_dict = {}
        station.latitude, station.longitude = latlon_to_mercator(station.latitude, station.longitude)
        if station.bikes == 0 and station.free == 0:
            percent_full = 0
        else:
            percent_full = float(station.bikes)/float(station.bikes + station.free)
        station_dict['geometry'] = {'type': 'Point', 'coordinates': [station.longitude, station.latitude]}
        station_dict['type'] = 'Feature'
        station_dict['id'] = station.extra['uid']
        station_dict['properties'] = {'station name': station.name,
                                      'bikes': station.bikes,
                                      'free': station.free,
                                      'color': color(percent_full),
                                      'size': (station.free + station.bikes)*0.5}
        geo_dict['features'].append(station_dict)
        geo_json = json.dumps(geo_dict)

    return geo_json


def get_data():
    # get data in GBSF format
    capital = pybikes.get('capital-bikeshare')
    capital.update()
    stations = capital.stations
    geo_data = gbsf_to_geojson(stations)

    return geo_data


def make_map(source):
    tile_provider = get_provider(Vendors.STAMEN_TERRAIN_RETINA)

    geo_data = source

    TOOLTIPS = [
        ('bikes available', '@bikes'),
    ]

    p = figure(x_range=(-8596413.91, -8558195.48), y_range=(4724114.13, 4696902.60),
               x_axis_type="mercator", y_axis_type="mercator", width=1200, height=700, tooltips=TOOLTIPS)
    p.add_tile(tile_provider)
    p.xaxis.visible = False
    p.yaxis.visible = False

    p.circle(x='x', y='y', size='size', color='color', alpha=0.7, source=geo_data)

    color_bar_palette = viridis(256)
    color_mapper = LinearColorMapper(palette=color_bar_palette, low=0, high=100)
    color_bar = ColorBar(color_mapper=color_mapper, background_fill_alpha=0.7, title='% Full',
                         title_text_align='left', title_standoff=10)
    p.add_layout(color_bar)

    label = Label(x=820, y=665, x_units='screen', y_units='screen',
                  text='Dot size represents total docks in station', render_mode='css',
                  border_line_color=None, background_fill_color='white', background_fill_alpha=0.7)
    p.add_layout(label)

    return p


def update():
    geo_json = get_data()
    source.update(geojson=geo_json)


source = get_data()
source = GeoJSONDataSource(geojson=source)
fig = make_map(source)
curdoc().add_root(column(fig))
curdoc().add_periodic_callback(update, 120000)
