import geopandas as gpd
import pandas as pd
import altair as alt
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
pollutants = ['NOX', 'BC', 'OZONE', 'PM25HR', 'NO2']

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
lc_NO2 = pd.read_csv('data/wrangled/NO2_line_plot.csv')

lc_dict = {'OZONE': lc_OZONE, 
           'NOX': lc_NOX, 
           'BC': lc_BC, 
           'PM25HR': lc_PM25HR,
           'NO2': lc_NO2}
param_title = {'OZONE': 'Ozone', 
               'NOX': 'NOx', 
               'PM25HR': 'PM 2.5', 
               'BC': 'Black Carbon',
               'NO2': 'NO2'}
units_dict = {'OZONE': 'ppm', 
              'NOX': 'ppm', 
              'PM25HR': 'µg/m3', 
              'BC': 'µg/m3',
              'NO2': 'ppm'}

# Create base-map
base_map = (alt.Chart(shape_gdf).mark_geoshape(
                stroke='black',
                fill = 'lightgray'
                ).encode())



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
    return ((base_map + sites_map).properties(title = "Sensor Locations",
                                             height = 450,
                                             width = 500)
                                             .configure(background='#cae1ff')
                                             .configure_title(fontSize = 24))

def plot_line(param='NOX'):
    lp = (alt.Chart(lc_dict[param]).mark_line(size=1)
                .encode(
                    x=alt.X('date:T', title='',axis = alt.Axis(labelFontSize = 13)),
                    y=alt.Y(param, 
                            title = '{} ({})'.format(param_title[param],
                                                units_dict[param]),
                            axis = alt.Axis(labelFontSize = 16,
                            titleFontSize = 20)),
                    color=alt.Color('name:N', 
                                    title = 'Station'),
                    tooltip=['name:N'])
                .properties(height = 300, 
                            width = 1100, 
                            title = 'Daily average {} concentration per station'.format(param_title[param])))
    pre_line = (alt.Chart(lc_dict[param])
        .mark_line(size=3, color='black')
        .encode(x='date:T',y='Pre-Shelter in place mean:Q'))
    post_line = (alt.Chart(lc_dict[param])
        .mark_line(size=3, color='black')
        .encode(x='date:T',y='Post-Shelter in place mean:Q'))
    text = alt.Chart().mark_text(dx=340,
                                dy=-130,
                                size=18,
                                text='Black = Mean value Pre- and Post- Shelter in Place').encode()
    return ((lp + pre_line + post_line + text)
                .configure_title(fontSize = 24)
                .configure_legend(titleFontSize=16))

def render_gif(param='NOX'):
    gp = Gif.GifPlayer(
            gif='assets/'+param+'.gif',
            still='assets/'+param+'_29.png'
                 )
    return gp


##########################################################################################
# APP LAYOUT
##########################################################################################

app.layout = html.Div([
    html.Div(className = "app-graphs",
            children = [
        # Row 1
        html.Div(className = "row",
            children = [
                # Writing!
                html.Div(className = 'writing',
                        children = [
                            html.Div(children=[
                                html.H2("How impactful is 'Shelter in Place' on Air Quality?"),
                                html.H2(""),
                                html.P(
                                    """On March 17th, San Francisco instituted a Shelter in Place
                                    ordinance in response to COVID-19. How will this drastic shift in
                                    human behavior impact the city's air quality? My guess is: for the
                                    better."""),
                                html.P(
                                    """Choose a Pollutant from the dropdown below! Options include Nitrogen Dioxide,
                                    Ozone, PM 2.5, NOx and Black Carbon, all of which human acitivities significantly 
                                    contribute to (mostly through automobiles)."""),
                                html.P(
                                    """The locations of air quality sensors and a time lapse of pollutant 
                                    levels from March 1st - present day are viewable by switching between 
                                    tabs to the right."""),
                                html.P(
                                    """The change in mean pollutant values from the month leading up 
                                    to the shelter in place ordinance (Feb 1st - March 16th) to the
                                    period after the shelter in place ordinance is displayed in the
                                    line-plot below.""")]),
                            html.Div(
                                className = "app-dd", 
                                children = [
                                    html.H3("Choose a Pollutant:"),
                                    dcc.Dropdown(
                                        id='dd-param',
                                        options=[
                                            {'label': 'Ozone', 'value': 'OZONE'},
                                            {'label': 'NOx', 'value': 'NOX'},
                                            {'label': 'PM 2.5', 'value': 'PM25HR'},
                                            {'label': 'Black Carbon', 'value': 'BC'},
                                            {'label': 'Nitrogen Dioxide', 'value': 'NO2'}
                                                ],
                                        value = 'NO2',
                                        clearable = False,
                                        style=dict(width='67%',
                                                    verticalAlign="middle",
                                                    fontSize = 18
                                                    )
                                    ),
                            ]),
                        dcc.Markdown(
                                """
                                ###### Already, we see a **decrease in mean pollutant levels** for everything but Ozone (which is highly
                                ###### influenced by weather conditions) as well as a **collapse of the weekly cycle** that coincides with high
                                ###### workday traffic.""")
                        ],
                    style={'width':'50%'}),
                # Tabs
                html.Div(
                    children=[
                        dcc.Tabs(
                                id='tabs',
                                value='main',
                                children=[
                                    dcc.Tab(
                                        label='Sensor Location',
                                        value='main',
                                        children=[
                                            html.Div(html.Iframe(
                                                sandbox='allow-scripts',
                                                id='sensor-plot',
                                                width='575',
                                                height='515',
                                                # Call plot function
                                                srcDoc = plot_sensors().to_html()
                                            ))
                                        ],
                                    ),
                                    dcc.Tab(
                                        label='Air Quality Time Series',
                                        value='gif',
                                        children=[
                                            html.Div(id='gif-player',
                                            children = [
                                                render_gif()
                                            ])
                                        ]
                                    )
                                ]
                            )
                        ],
                    style={'width':'35%'}
                    )
            ]
        ),
        # Line Plot           
        html.Div(className = "row",
                    children = [html.Iframe(
                        sandbox='allow-scripts',
                        id='line-plot',
                        height='400',
                        width='1425',
                        # Call plot function
                        srcDoc = plot_line().to_html()
                )]
        ),
        # Row 3
        html.Div(className='footer',
        children=[
            dcc.Markdown(
            """
            ###### Author: Cari Gostic" 
            ###### View the project Github Page [here]()
            ###### _Data is retrieved daily from the CA air resources board site (https://www.arb.ca.gov), and a linear interpolation is calculated over the region bounded by the air quality sensors to create the time lapse._
            ###### _View a vignette for PM 2.5 [here.](https://github.com/cgostic/sf_air-quality_covid19/blob/master/scripts/interpolate_pm25_vignette.ipynb)_
            # """)])
        ]
    )
])

@app.callback(
    dash.dependencies.Output('line-plot', 'srcDoc'),
              [dash.dependencies.Input('dd-param', 'value')])
def update_plot(param):
    '''
    Takes in a date and calls plot_line() to update our Altair figure
    '''
    updated_plot = plot_line(param).to_html()
    return updated_plot

@app.callback(
    dash.dependencies.Output('gif-player', 'children'),
              [dash.dependencies.Input('dd-param', 'value')])
def update_gif(param):
    '''
    Takes in a date and calls plot_line() to update our Altair figure
    '''
    updated_path = render_gif(param)
    return updated_path

if __name__ == '__main__':
    app.run_server(debug=True)