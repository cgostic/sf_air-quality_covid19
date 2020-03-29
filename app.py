import geopandas as gpd
import pandas as pd
import altair as alt
from shapely import wkt
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], assets_folder = "assets")
app.config['suppress_callback_exceptions'] = True

server = app.server

app.title = 'Air Quality'

###################################################################################################
# Load the data
####################################################################################################
# Load geojson to dataframe object
shape_gdf = gpd.read_file('data/raw/Bay_Area_Counties.geojson')

# Load sites data
sites = pd.read_csv('data/wrangled/sites_data.csv')
sites_gdf = gpd.GeoDataFrame(sites, geometry = gpd.points_from_xy(sites.longitude, sites.latitude))

# Load interpolated PM 2.5 data
data = pd.read_csv('data/wrangled/pm25_interpolated.csv')
data['geometry'] = data['geometry'].apply(wkt.loads)
pm25_gdf = gpd.GeoDataFrame(data, geometry = 'geometry')

# Rename data columns to integers for callback
dat_cols = list(pm25_gdf['date'].unique())

# Create base-map
base_map = (alt.Chart(shape_gdf).mark_geoshape(
                stroke='black',
                fill = None
                ).encode())

# Plot dimensions
h_sites, w_sites = 500, 500
h_pm25, w_pm25 = 800, 800

#####################################################################################################
# Make the plots
#####################################################################################################
def make_plot(date = 0):
#     def plot_sensors(base_map):
#         """
#         Returns Altair plot of point locations in gdf overlayed
#         on base map.
#         """
#         sites_map = (alt.Chart(sites_gdf)
#                 .mark_geoshape(color = 'red', 
#                                 size = .25)
#                 .encode(tooltip = ['name']))
#         return (base_map + sites_map).properties(title = title,
#                                                 height = h_sites,
#                                                 width = w_sites)
    def plot_pm25(date):
        plot_df = (pm25_gdf.query('date_int =='+str(date))
            .reset_index(drop = True))
        interpolated_plot = (alt.Chart(plot_df)
                        .mark_geoshape()
                        .encode(fill = alt.Color('pm25', 
                                        scale = alt.Scale(domain = [0,16]),
                                        title = 'µg/m3'),
                                tooltip = [alt.Tooltip('pm25', 
                                                        title = 'PM 2.5 (µg/m3)', 
                                                        format = '0.5')]
                                ))
        return (interpolated_plot + base_map).properties(
            title = "Bay Area Avg. PM 2.5 (µg/m3): "+plot_df.loc[0,'date'],
            height = h_pm25,
            width = w_pm25)
    return plot_pm25(date)

app.layout = html.Div([
        # First column        
        html.Div(
            children=[
                html.Div(className = "app-logo", children = [
                    html.Img(src='https://i.ibb.co/F78bQB2/logo-2.png', width = 200)
                ]),
                html.Div(className = "app-side-panel-intro", children = [
                    html.H5('Guide your observance of the famous squirrels of Central Park, NY')
                ]),
                dcc.Markdown(className = "app-panel-list", children = [
                    """
                    - Hover over any chart value to see details
                    - Click a region on any chart to highlight across all charts
                    - Shift + click to select multiple regions at once
                    """
                ]),
                html.Div(className = "app-behavior-intro", children = [
                    html.H5('Select a Behavior to'),
                    html.H5('Display:')
                    ]),
                html.Div(className = "app-behavior-dd", children = [
                    dcc.Dropdown(
                        id='dd-chart',
                        options=[
                            {'label': '2020-01-01', 'value': '2020-01-01'},
                            {'label': '2020-01-15', 'value': '2020-01-15'},
                            {'label': '2020-02-01', 'value': '2020-02-01'},
                            {'label': '2020-02-15', 'value': '2020-02-15'},
                            {'label': '2020-03-01', 'value': '2020-03-01'},
                                ],
                        value = '2020-01-01',
                        clearable = False,
                        style=dict(width='95%',
                                    verticalAlign="middle",
                                    fontSize = 18
                                    )
                            )
                    ]),
                html.Div(className = "app-behavior-arrow", children = [
                    html.Img(src="https://upload.wikimedia.org/wikipedia/commons/8/8e/Simpleicons_Interface_arrow-pointing-to-right.svg", width = 50)
                ])
        ], style={'width': '15%', 'display': 'inline-block', 'vertical-align': 'top'}),
        # 2nd column
        html.Div(className = 'app-graphs',
                children = [
                    html.Iframe(
                        sandbox='allow-scripts',
                        id='plot',
                        height='955',
                        width='1400',
                        style={'border-width': '0px'},
                        # Call plot function
                        srcDoc = make_plot().to_html()
                        ),
                    html.Div([
                        dcc.Slider(
                        id='year-slider',
                        marks = {i: dat_cols[i] for i in range(0,len(dat_cols), 5)},
                        min=0,
                        max=len(dat_cols),
                        step=1,
                        value=0,
                        updatemode='drag',
                    ),
                ], style={'width':'80%'})

                        ], style={'width': '84%', 'display': 'inline-block'}),                 
        dcc.Markdown(className = "app-footer", children = [
                    """
                    #### Visit the [Github Repository](https://github.com/cgostic/squirrel_app_CG)  
                    #### Sources: 
                    - [The Central Park Squirrel Census](https://www.thesquirrelcensus.com/)
                    - [NYC OpenData](https://data.cityofnewyork.us/Environment/2018-Central-Park-Squirrel-Census-Squirrel-Data/vfnx-vebw) 
                    - [Squirrel Image,](https://www.trzcacak.rs/myfile/full/50-509839_squirrel-black-and-white-free-squirrel-clipart-cartoon.png) [ Arrow Image](https://commons.wikimedia.org/wiki/File:Simpleicons_Interface_arrow-pointing-to-right.svg)
                    
                    #### Contributions:  
                    - The original version of this app was created with Roc Zhang and Lori Feng as a group project in UBC's Master of Data Science Program. The original app can be viewed [here](https://dsci-532-group203-milestone2.herokuapp.com/), and the original Github repository can be viewed [here](https://github.com/UBC-MDS/DSCI-532_group-203_Lab1-2).
                    """
                ])
    ])

@app.callback(
    dash.dependencies.Output('plot', 'srcDoc'),
              [dash.dependencies.Input('year-slider', 'value')])
def update_plot(date_int):
    '''
    Takes in a date and calls make_plot to update our Altair figure
    '''
    updated_plot = make_plot(date_int).to_html()
    return updated_plot



if __name__ == '__main__':
    app.run_server(debug=True)