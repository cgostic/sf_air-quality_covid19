import geopandas as gpd
import pandas as pd
import altair as alt
from shapely import wkt
import time
import ipywidgets as widgets
from ipywidgets import interact
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_gif_component as Gif
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], assets_folder = "assets")
app.config['suppress_callback_exceptions'] = True

server = app.server

app.title = 'Air Quality'

###################################################################################################
# Load the data
####################################################################################################
pollutants = ['NOX', 'BC', 'OZONE', 'PM25HR']

# Load geojson to dataframe object
shape_gdf = gpd.read_file('data/raw/Bay_Area_Counties.geojson')

# Load sites data
sites = pd.read_csv('data/wrangled/sites_data.csv')
sites_gdf = gpd.GeoDataFrame(sites, geometry=gpd.points_from_xy(sites.longitude,
                                                                sites.latitude))

# Load line chart data
lc_OZONE = pd.read_csv('data/wrangled/OZONE_line_plot.csv')
lc_BC = pd.read_csv('data/wrangled/BC_line_plot.csv')
lc_NOX = pd.read_csv('data/wrangled/NOX_line_plot.csv')
lc_PM25HR = pd.read_csv('data/wrangled/PM25HR_line_plot.csv')

lc_dict = {'OZONE': lc_OZONE, 
           'NOX': lc_NOX, 
           'BC': lc_BC, 
           'PM25HR': lc_PM25HR}
param_title = {'OZONE': 'Ozone', 
               'NOX': 'NOx', 
               'PM25HR': 'PM 2.5', 
               'BC': 'Black Carbon'}
units_dict = {'OZONE': 'ppm', 
              'NOX': 'ppm', 
              'PM25HR': 'µg/m3', 
              'BC': 'µg/m3'}

# Create base-map
base_map = (alt.Chart(shape_gdf).mark_geoshape(
                stroke='black',
                fill = None
                ).encode())

print(lc_OZONE['date'])


#####################################################################################################
# Make the plots
#####################################################################################################

def plot_sensors():
    """
    Returns Altair plot of point locations in gdf overlayed
    on base map.
    """
    sites_map = (alt.Chart(sites_gdf)
             .mark_geoshape(color = 'red', 
                            size = .25)
             .encode(tooltip = ['name']))
    return (base_map + sites_map).properties(title = "Sensor Locations",
                                             height = 450,
                                             width = 500)

def plot_line(param='NOX'):
    lp = (alt.Chart(lc_dict[param]).mark_line(size=1)
                .encode(
                    x=alt.X('date:T', title='Date'),
                    y=alt.Y(param, 
                            title = param_title[param]),
                    color=alt.Color('name:N', 
                                    title = 'Station'),
                    tooltip=['name:N'])
                .properties(height = 300, 
                            width = 1400, 
                            title = 'Daily average per Station'))
    pre_line = (alt.Chart(lc_dict[param])
        .mark_line(size=3, color='black')
        .encode(x='date',y='Pre-Shelter in place mean:Q'))
    post_line = (alt.Chart(lc_dict[param])
        .mark_line(size=3, color='black')
        .encode(x='date',y='Post-Shelter in place mean:Q'))
    return lp + pre_line + post_line
