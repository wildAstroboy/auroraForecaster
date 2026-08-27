import os
import sys
import webbrowser

from clients.NOAA_data import noaa_data
from map.map import create_map


def open_html():
    file_path = os.path.abspath('map/aurora_location.html')
    webbrowser.open(f'file://{file_path}')

if __name__ == '__main__':
    aurora_data = noaa_data.get_aurora_data()
    kp_forecast = noaa_data.get_kp_forecast()
    alerts_data = noaa_data.get_alerts()

    if aurora_data is None or kp_forecast is None:
        print('Could not fetch data from NOAA — check your network connection and try again.')
        sys.exit(1)

    create_map(aurora_data, kp_forecast, alerts_data)
    open_html()