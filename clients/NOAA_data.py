#Fetches data from the NOAA website: https://services.swpc.noaa.gov/
import requests
import pandas as pd


# Historical Data
KP_FORECAST_URL = 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json'
SEVENDAY_XRAY_FLARES = 'https://services.swpc.noaa.gov/json/goes/primary/xray-flares-7-day.json'

# Current & Future Data and Predictions
KP_INDEX_URL = 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json'
LASTEST_XRAY_FLARE = 'https://services.swpc.noaa.gov/json/goes/primary/xray-flares-latest.json'

# Latitude, Longitude, and percent chance of Aurora
AURORA_DATA = 'https://services.swpc.noaa.gov/json/ovation_aurora_latest.json'


def get_kp_forecast():
    response = requests.get(KP_FORECAST_URL)
    response.raise_for_status()
    forcast_data = response.json()

    # Extract all the observations that are predicted.
    predicted = [forcast for forcast in forcast_data if forcast.get('observed') == 'predicted']
#   print(predicted)
    return predicted

def get_kp_index():
    response = requests.get(KP_INDEX_URL)
    response.raise_for_status()
    index_data = response.json()
#   print(index_data)
    return index_data

def get_lastest_xray():
    response = requests.get(LASTEST_XRAY_FLARE)
    response.raise_for_status()
    xray_data = response.json()
#   print(xray_data)
    return xray_data

def get_sevenday_xray():
    response = requests.get(SEVENDAY_XRAY_FLARES)
    response.raise_for_status()
    xray_data = response.json()
#   print(xray_data)
    return xray_data

# Fetch our Aurora geo locations and percent chance
def get_aurora_data():
    try:
        response = requests.get(AURORA_DATA)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f'Error fetching data: {e}')
        return

    forecast_time = data.get('Forecast Time')
    raw_data = data.get('coordinates', [])

    filtered_data = [[lon, lat, percent] for lon, lat, percent in raw_data if percent > 0]

    # Put our fetched data in to a dataframe
    df = pd.DataFrame(filtered_data, columns=['lon', 'lat', 'percent'])
    columns_data = ['lat', 'lon', 'percent']
    df = df.reindex(columns=columns_data)

    # Longitudinal data arrives in a range from 0 to 360, shifting to -180 to 180 for plotly
    df.loc[df['lon'] > 180, 'lon'] -= 360

    df['forecast'] = forecast_time

    #max_group = df.loc[df['percent'].idxmax()]
    #print(df)
    #print(max_group)
    return df
