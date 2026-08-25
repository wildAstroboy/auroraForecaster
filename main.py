import os
import sys
import webbrowser

from clients.NOAA_data import get_kp_forecast, get_aurora_data
from map.map import create_map

def open_html():
    file_path = os.path.abspath('map/aurora_location.html')
    webbrowser.open(f'file://{file_path}')

if __name__ == '__main__':
    aurora_data = get_aurora_data()
    kp_forecast = get_kp_forecast()

    if aurora_data is None or kp_forecast is None:
        print('Could not fetch data from NOAA — check your network connection and try again.')
        sys.exit(1)

    create_map(aurora_data, kp_forecast)
    open_html()