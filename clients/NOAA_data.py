#Fetches data from the NOAA website: https://services.swpc.noaa.gov/
import requests
import pandas as pd
from scipy.ndimage import gaussian_filter
from datetime import datetime, timedelta
from dateutil.tz import UTC


# Historical Data
KP_FORECAST_URL = 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json'
SEVENDAY_XRAY_FLARES = 'https://services.swpc.noaa.gov/json/goes/primary/xray-flares-7-day.json'

# Current & Future Data and Predictions
KP_INDEX_URL = 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json'
LASTEST_XRAY_FLARE = 'https://services.swpc.noaa.gov/json/goes/primary/xray-flares-latest.json'

# Latitude, Longitude, and percent chance of Aurora
AURORA_DATA = 'https://services.swpc.noaa.gov/json/ovation_aurora_latest.json'

class NoaaData:

    @staticmethod
    def _fetch_json(url) -> dict | None:
        # Fetch NOAA endpoint
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f'Error fetching {url}: {e}')
            return None

    def get_kp_forecast(self):
        forcast_data = self._fetch_json(KP_FORECAST_URL)
        if forcast_data is None:
            return None

        cutoff_time = datetime.now(UTC) - timedelta(days=1)
        future_cutoff_time = datetime.now(UTC) + timedelta(days=1)
        filtered_data = [[item['time_tag'], item['kp'], item['observed']]
                         for item in forcast_data
                         if cutoff_time <= datetime.fromisoformat(item['time_tag']).replace(
                tzinfo=UTC) <= future_cutoff_time]

        df = pd.DataFrame(filtered_data, columns=['time', 'kp', 'observed'])

        # print(df)
        return df
    """
    Planned for future use.
    
    def get_kp_index(self):
        return self._fetch_json(KP_INDEX_URL)

    def get_lastest_xray(self):
        return self._fetch_json(LASTEST_XRAY_FLARE)

    def get_sevenday_xray(self):
        return self._fetch_json(SEVENDAY_XRAY_FLARES)
    """

    # Fetch our Aurora geo locations and percent chance
    def get_aurora_data(self):
        data = self._fetch_json(AURORA_DATA)
        if data is None:
            return None

        forecast_time = data.get('Forecast Time')
        raw_data = data.get('coordinates', [])

        df = pd.DataFrame(raw_data, columns=['lon', 'lat', 'percent'])

        num_lon, num_lat = 360, 181

        # Extract the raw 1D array into an active 2D grid matrix
        grid_z = df['percent'].to_numpy().reshape(num_lat, num_lon, order='F')

        # Make pixels into smooth contour
        smoothed_grid = gaussian_filter(grid_z.astype(float), sigma=5.0)

        df['percent'] = smoothed_grid.flatten(order='F')

        # Coordinate transformations
        df.loc[df['lon'] > 180, 'lon'] -= 360
        df = df.reindex(columns=['lat', 'lon', 'percent'])

        df = df.sort_values(by=['lat', 'lon']).reset_index(drop=True)

        # Downsample and drop 0 values
        df = df.iloc[::4]
        df = df[df['percent'] >= 1.0]

        df['forecast'] = forecast_time
        return df

noaa_data = NoaaData()