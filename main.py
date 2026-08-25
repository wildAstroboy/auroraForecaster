import os
import webbrowser

from clients.NOAA_data import get_kp_forecast, get_kp_index, get_lastest_xray, get_sevenday_xray, get_aurora_data
from map.map import create_map

def open_html():
    file_path = os.path.abspath('map/aurora_location.html')
    webbrowser.open(f'file://{file_path}')

if __name__ == '__main__':
    #get_aurora_data()

    create_map(get_aurora_data())
    open_html()

