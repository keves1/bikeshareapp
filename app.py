from bokeh.plotting import figure, curdoc
from bokeh.layouts import column
from bokeh.tile_providers import get_provider, Vendors
import pybikes

tile_provider = get_provider(Vendors.CARTODBPOSITRON)

# range bounds supplied in web mercator coordinates
p = figure(x_range=(-13651271.00, -13610224.41), y_range=(4549761.18, 4529887.56),
           x_axis_type="mercator", y_axis_type="mercator")
p.add_tile(tile_provider)

# get data in gbsf format
bay_wheels = pybikes.get('bay-wheels')
bay_wheels.update()

# convert data to geojson format


curdoc().add_root(column(p))
