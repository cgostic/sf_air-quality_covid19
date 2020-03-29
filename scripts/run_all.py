"""
Author: Cari Gostic
Date: March 28, 2020

This script creates .csv files and .gifs to
support the air quality monitoring app hosted at


-----------------------------------------------------------------
The purpose of the app is to monitor changes in
air quality in the San Franciso Bay area over
the progression of the city's shelter in place ordinance
in repsonse to COVID-19.

The script retrives data from the CA air resources board
site (https://www.arb.ca.gov) for each of 4 pollutants: 
Black Carbon [BC], PM 2.5 [PM25HR], Ozone [OZONE] and NOx [NOX].

The script performs a linear interpolation over the region
bounded by the air quality sensors in the Bay Area.

The script exports a .png per day per pollutant and one .gif per
pollutant to the /assets folder, a sites_data.csv, *_interpolated.csv
per pollutant, and *_line.csv per pollutant to the 
data/wrangled folder.
"""

import geopandas as gpd
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import json
from shapely.geometry import Polygon, Point
from scipy.interpolate import griddata
import numpy as np
import requests
import io
import imageio
import os
from datetime import date

# Load site information
sites = pd.read_csv('../data/raw/PM25HR_SITELIST_2020-12-31.csv')
sites.astype({'site': 'str'})

# Load geojson (Bay Area County borders) to dataframe object
shape_gdf = gpd.read_file('../data/raw/Bay_Area_Counties.geojson')

# Create df of unique sensor locations
sites_wr = sites.groupby(['site', 'name']).aggregate({'latitude':'mean',
                                            'longitude':'mean'}).reset_index()
# Export for plotting
sites_wr.to_csv('../data/wrangled/sites_data.csv')
# Cast 'site' column as a string to match data df
sites_wr['site'] = sites_wr['site'].astype('int').astype('str')

# Units and pollutant mapping
param_title = {'OZONE': 'Ozone', 'NOX': 'NOx', 'PM25HR': 'PM 2.5', 'BC': 'Black Carbon'}
units_dict = {'OZONE': 'ppm', 'NOX': 'ppm', 'PM25HR': 'µg/m3', 'BC': 'µg/m3'}

# Today's date
today = date.today()

# Available pollutants
pollutants = ['PM25HR', 'OZONE', 'BC', 'NOX']

for param in pollutants:
    # Set parameters
    first_date = '2020-2-15' # yyyy-m-d 
    units = {'OZONE': '007', 'BC': '001', 'NOX': '007', 'PM25HR': '001'}
    year = '2020'
    mon = str(today.month)
    day = str(today.day)
    basin = 'SFB-San+Francisco+Bay'
    rows = {'OZONE': '20', 'BC': '6', 'NOX': '18', 'PM25HR': '17'}
    fname = param+'_'+year+'-'+mon+'-'+day

    url = 'https://www.arb.ca.gov/aqmis2/display.php?sitelist=All&\
filefmt=csv&fname='+fname+'&datafmt=web&download=y&\
first_date='+first_date+'&param='+param+'&\
units='+units[param]+'&year='+year+'&report=PICKDATA\
&mon='+mon+'&day='+day+'&o3area=&o3pa8=&\
county_name=--COUNTY--&latitude=--PART+OF+STATE--&\
basin='+basin+'&order=basin%2Ccounty_name%2Cs.name&\
ptype=aqd&o3switch=new&hours=all&\
statistic=&qselect=Screened&start_mon=2&\
start_day=1&submit=All+Sites&\
rows='+rows[param]

    print("Creating content for "+param)

    # Download data from CA air resources board
    # https://www.arb.ca.gov
    r = requests.post(url)
    if r.ok:
        data = r.content.decode('utf8')
        aq_data = pd.read_csv(io.StringIO(data))    

    # Remove observations marked "invalid"
    aq_data = aq_data.dropna()

    # Map latitude, longitude values to new columns in data df based 
    # on site id
    lat_dict = dict(zip(sites_wr['site'], sites_wr['latitude']))
    long_dict = dict(zip(sites_wr['site'], sites_wr['longitude']))
    aq_data['lat'] = aq_data['site'].map(lat_dict)
    aq_data['long'] = aq_data['site'].map(long_dict)

    # Cast sites as geodataframe
    gdf_sites = gpd.GeoDataFrame(
        sites_wr, geometry=gpd.points_from_xy(sites_wr.longitude, 
                                            sites_wr.latitude))

    # Reshape df, column per date
    aq_da = aq_data[['site', 
                    'date', 
                    'value']].groupby(['site',
                                        'date']).mean().reset_index()
    aq_da = aq_da.pivot(index = 'site', 
                        values = 'value', 
                        columns = 'date').reset_index()
    # Merge spatial data with aq data
    aq_gdf = pd.merge(gdf_sites, aq_da, how = 'inner', on = 'site')

    # Interpolate AQ values across a grid bounded by sensor locations

    # Define size of pixels in grid (units of lat/long degrees)
    pixel = .05
    # Determine extent of observations and create pixel_size-spaced arrays
    # in the N and S direction
    x_range = np.arange(aq_gdf.longitude.min()-aq_gdf.longitude.min()%pixel,
                        aq_gdf.longitude.max(), pixel)
    y_range = np.arange(aq_gdf.latitude.min()-aq_gdf.latitude.min()%pixel,
                        aq_gdf.latitude.max(), pixel)[::-1]
    shape = (len(y_range), len(x_range))
    xmin, xmax = x_range.min(), x_range.max()
    ymin, ymax = y_range.min(), y_range.max()
    extent = (xmin, xmax, ymin, ymax)
    # Create grid
    x_mesh, y_mesh = np.meshgrid(x_range, y_range)

    # Store interpolated points in new dataframe
    interp_df = pd.DataFrame({'lat':y_mesh.flatten(), 
                            'long': x_mesh.flatten()})
    date_cols = aq_gdf.columns[5:]
    print('    Interpolating across all dates')
    for date in date_cols[15:]:
        # Linear interpolation across grid
        pm_interp = griddata((aq_gdf['longitude'], 
                            aq_gdf['latitude']), 
                            aq_gdf[date], 
                            (x_mesh, y_mesh), 
                            method = 'linear')
        interp_df[date] = pm_interp.flatten()

    # Cast to geodataframe
    interp_gdf = gpd.GeoDataFrame(
        interp_df, geometry=gpd.points_from_xy(interp_df.long, 
                                            interp_df.lat))

    # Buffer each grid point to a larger pixel
    interp_buffer = interp_gdf.copy()
    buffer = interp_buffer.buffer(0.04)
    envelope = buffer.envelope
    interp_buffer['geometry'] = envelope

    # Write csv with interpolated values
    interp_buffer = interp_buffer.melt(id_vars = ['geometry','lat','long'], 
                                    var_name = 'date', 
                                    value_name = param)
    interp_buffer['date_int'] = (interp_buffer['date']
                                    .map(dict(zip(date_cols, 
                                            range(len(date_cols))))))
    interp_buffer.to_csv('../data/wrangled/'+param+'_interpolated.csv')

    # Write csv to plot avg daily AQ values per station
    cols = ['name']+list(date_cols)
    line_df = aq_gdf[cols].melt(id_vars='name', 
        var_name = 'date', 
        value_name = param).dropna()
    line_df['Pre-Shelter in place mean']=np.where(line_df['date']<='2020-03-16', 
                    np.mean(line_df.query('date <= "2020-03-16"')[param]), np.nan)
    line_df['Post-Shelter in place mean']=np.where(line_df['date']>'2020-03-16', 
                    np.mean(line_df.query('date > "2020-03-16"')[param]), np.nan)
    line_df.to_csv('../data/wrangled/'+param+'_line_plot.csv')

    # CREATE GIFS of AQ values across bay area
    #print(interp_buffer.loc[15,['date','date_int']])

    # create basemap
    base_map = (alt.Chart(shape_gdf).mark_geoshape(
        stroke='black',
        fill = None
        ).encode())

    def plot_aq(date = 0):
        """
        Returns map of interpolated AQ values for single date
        """
        plot_df = interp_buffer.query('date_int =='+str(date)).reset_index(drop=True)
        interpolated_plot = (alt.Chart(plot_df)
            .mark_geoshape()
            .encode(fill = alt.Color(param,
                        scale = alt.Scale(
                            domain=[min(interp_buffer[param].dropna()),
                                max(interp_buffer[param].dropna())],
                            type = 'linear',
                            scheme = 'yelloworangebrown'),
                        title = units_dict[param]),
                    tooltip = [alt.Tooltip(param, 
                                title = param_title[param]+" \
                                    "+units_dict[param], 
                                format = '0.5')]
                            ))
        if date < 31:
            return ((interpolated_plot + base_map)
                .properties(
                    title = "Bay Area Avg.{} ({}): {}".format(
                        param_title[param],
                        units_dict[param],
                        plot_df.loc[0,'date']),
                    height = 450,
                    width = 500)
                .configure_title(fontSize = 20)
                .configure_legend(titleFontSize=16, labelFontSize=14))
        else:
            annotation = alt.Chart(plot_df).mark_text(
                align='left',
                baseline='middle',
                fontSize = 16,
                dx = 65,
                dy = -210,
                text = 'Shelter-in-place enforced',
                color = 'red'
                ).encode()
            return ((interpolated_plot + base_map + annotation)
                .properties(title = "Bay Area Avg.{} ({}): {}".format(
                                            param_title[param],
                                            units_dict[param],
                                            plot_df.loc[0,'date']),
                            height = 450,
                            width = 500)
                .configure_title(fontSize = 20)
                .configure_legend(titleFontSize=16, labelFontSize=14))

    # Save image of plot for each date
    filenames = []
    # Create gif starting at march 1st
    print('    Creating images')
    for i in range(15, max(interp_buffer['date_int'])+1):
        filename = '../assets/'+param+'_'+str(i)+'.png'
        filenames.append(filename)
        plot_aq(i).save(filename)
    # Merge images into gif
    print('    Creating gif')
    with imageio.get_writer('../assets/'+param+'.gif', 
                            mode='I', 
                            duration = .6, 
                            loop = 1) as writer:
        for filename in filenames:
            image = imageio.imread(filename)
            writer.append_data(image)
print('All finished!!!')


