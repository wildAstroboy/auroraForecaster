#Fetches data from the NOAA website: https://services.swpc.noaa.gov/
import requests
import pandas as pd
from scipy.ndimage import gaussian_filter
from datetime import datetime, timedelta
from dateutil.tz import UTC
from scipy.signal import filter_design

# Historical Data
KP_FORECAST_URL = 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json'
SEVENDAY_XRAY_FLARES = 'https://services.swpc.noaa.gov/json/goes/primary/xray-flares-7-day.json'

# Current & Future Data and Predictions
KP_INDEX_URL = 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json'
PRIMARY_XRAY_FLARES = 'https://services.swpc.noaa.gov/json/goes/primary/xrays-7-day.json'
SECONDARY_XRAY_FLARES = 'https://services.swpc.noaa.gov/json/goes/secondary/xrays-7-day.json'

# Latitude, Longitude, and percent chance of Aurora
AURORA_DATA = 'https://services.swpc.noaa.gov/json/ovation_aurora_latest.json'

# Alerts
ALERTS_URL = 'https://services.swpc.noaa.gov/products/alerts.json'

class NoaaData:
    # Fetch JSON Data
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

    # Get the Kp Forecast
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

        df['time'] = pd.to_datetime(df['time'], errors='coerce')

        # 2. Convert it to a string format that Plotly's layout engine can reliably project onto a 2D axis
        df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')

        #print(df)
        return df

    # Get Space Weather Alerts
    def get_alerts(self):
        alerts_data = self._fetch_json(ALERTS_URL)
        if alerts_data is None:
            return None
        return alerts_data[0]

    def get_xray_data(self):
        primary_data = self._fetch_json(PRIMARY_XRAY_FLARES)
        secondary_data = self._fetch_json(SECONDARY_XRAY_FLARES)
        if primary_data is None or secondary_data is None:
            return None

        df1 = pd.DataFrame(primary_data)
        dfs_by_energy = {energy: group for energy, group in df1.groupby('energy')}
        p_short_energy_df = dfs_by_energy['0.05-0.4nm']
        p_long_energy_df = dfs_by_energy['0.1-0.8nm']

        df2 = pd.DataFrame(secondary_data)
        dfs_by_energy = {energy: group for energy, group in df2.groupby('energy')}
        s_short_energy_df = dfs_by_energy['0.05-0.4nm']
        s_long_energy_df = dfs_by_energy['0.1-0.8nm']

        # Convert to pandas Datetime objects
        p_short_energy_df['time_tag'] = pd.to_datetime(p_short_energy_df['time_tag'])

        # Find the earliest and latest overall dates to anchor the time selectors
        min_date = p_short_energy_df['time_tag'].min()
        max_date = p_short_energy_df['time_tag'].max()

        # Format them as ISO strings which Plotly axes require
        xray_timeline_range = [min_date.strftime("%Y-%m-%d %H:%M:%S"), max_date.strftime("%Y-%m-%d %H:%M:%S")]

        #print(xray_timeline_range)
        return p_short_energy_df, p_long_energy_df, s_short_energy_df, s_long_energy_df, xray_timeline_range

    """
    Planned for future use.
    
    def get_kp_index(self):
        return self._fetch_json(KP_INDEX_URL)

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

if __name__ == '__main__':
    noaa_data.get_kp_forecast()
