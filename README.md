# sf_air-quality_covid19

### Monitoring air quality in the San Francisco Bay Area throughout the COVID-19 pandemic and shelter-in-place ordinance.

### View the [SF Bay Air Quality App](https://sf-aq-covid19.herokuapp.com/)

### Read the [Analysis Report](https://github.com/cgostic/sf_air-quality_covid19/blob/master/docs/NO2_analysis_2020_04_05.md)

On March 17th, San Francisco instituted a Shelter in Place ordinance in response to COVID-19. How will this drastic shift in
human behavior impact the city's air quality? My guess is: for the better.

The app created through this repository displays a time lapse of concentrations of common pollutants that human activities contribute to through automobiles and industrial processes. These include Nitrogen Dioxide, Ozone, PM 2.5, NOx and Black Carbon.
                            

## Usage

#### To run the app locally:

- Download/clone this repository
- Navigate to this repository via the command line
- Run the following in the command line:

```
python app.py
```

**app.py Dependencies:**

- dash==1.4.1
- pandas==1.0.1
- altair==4.0.1
- numpy==1.18.1
- vega_datasets==0.7.0
- geopandas==0.6.1
- gunicorn==20.0.0
- dash-bootstrap-components==0.7.2
- dash-gif-component==1.0.2
- dash-html-components==1.0.1
- dash-core-components==1.3.1

#### To create/update the .gif's locally:

- Download/clone this repository
- Navigate to the **scripts folder** of this repository via the command line
- Run the following in the command line:

```
python run_all.py
```

**run_all.py Dependencies:**

- geopandas==0.6.1
- pandas==1.0.1
- numpy==1.18.1
- altair==4.0.1
- Shapely==1.6.4.post2
- scipy==1.4.1
- requests==2.22.0
- imageio==2.6.1

The `scripts/run_all.py` script retrives data from the CA air resources board site (https://www.arb.ca.gov) for each of 4 pollutants: 
NO2 [NO2], Black Carbon [BC], PM 2.5 [PM25HR], Ozone [OZONE] and NOx [NOX]. The script performs a linear interpolation over the region
bounded by the air quality sensors in the Bay Area.

Inputs:

- `data/raw/PM25HR_SITELIST_2020-12-31.csv` ; sensor location data
- `data/raw/Bay_Area_Counties.geojson` ; a base map of county boundaries for the San Francisco Bay area.

Outputs:

- `assets/*.gif` ; a time lapse of air quality from March 1, 2020 - present day for each pollutant `*`.
  - `assets/img/*_<int>.png` ; images of each pollutant `*` for each date `<int>`.
- `data/wrangled/*_line_plot.csv` ; a data file for each pollutant `*` to create the app's line plot
- `data/wrangled/sites_data.csv`; a data file with geographical information on sites



## Vignette

In the `scripts` folder, there is also a [vignette](https://github.com/cgostic/sf_air-quality_covid19/blob/master/docs/interpolate_pm25_vignette.ipynb) that walks through the process of data wrangling and spatial interpolation
for a single pollutant (PM 2.5) that is executed to create the outputs seen on the app.


#### Data Sources

- [CA Air Resources Board hourly data](https://www.arb.ca.gov/aqmis2/aqdselect.php?tab=hourly)
- [Data SF Bay area counties shapefile](https://data.sfgov.org/Geographic-Locations-and-Boundaries/Bay-Area-Counties/s9wg-vcph)

#### Coding Resources

- [geologyandpython.com (geographic interpolation method)](http://geologyandpython.com/ml-interpolation-method.html)
- [GIS Stack Exchange: creating square buffers around points using shapely](https://gis.stackexchange.com/questions/314949/creating-square-buffers-around-points-using-shapely)

