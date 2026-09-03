import os
import sys
import webbrowser
from dotenv import load_dotenv

load_dotenv()

carto_api_key = os.getenv('CARTO_API_KEY')

from clients.NOAA_data import noaa_data
from map.map import create_map

# Open saved HTML file function
def open_html():
    file_path = os.path.abspath('map/aurora_location.html')
    webbrowser.open(f'file://{file_path}')

if __name__ == '__main__':
    #Load data and check to see if any return None
    aurora_data = noaa_data.get_aurora_data()
    kp_forecast = noaa_data.get_kp_forecast()
    alerts_data = noaa_data.get_alerts()
    xray_data = noaa_data.get_xray_data()

    if aurora_data is None or kp_forecast is None or xray_data is None:
        print('Could not fetch data from NOAA — check your network connection and try again.')
        sys.exit(1)

    # Create and save Plotly dash and open the HTML file
    create_map(aurora_data, kp_forecast, alerts_data, *xray_data, carto_api_key)
    open_html()