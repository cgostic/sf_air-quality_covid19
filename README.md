# sf_air-quality_covid19

Monitoring air quality in the San Francisco Bay Area throughout the COVID-19 pandemic and shelter-in-place ordinance.

### View the [SF Bay Air Quality App]()

The purpose of the app is to monitor changes in air quality in the San Franciso Bay area over the progression of the city's 
shelter in place ordinance in repsonse to COVID-19.

The `scripts/runn_all.py` script retrives data from the CA air resources board site (https://www.arb.ca.gov) for each of 4 pollutants: 
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

### Vignette

In the `scripts` folder, there is also a [vignette]() that walks through the process of data wrangling and spatial interpolation
for a single pollutant (PM 2.5) that is executed to create the outputs seen on the app.
