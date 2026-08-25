import geocoder
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Create the interactive map
def create_map(coords, kp_forecast):

    #Get local lat and lon, if not found, use [0,0]
    my_loc = geocoder.ip('me')

    if my_loc and my_loc.latlng and len(my_loc.latlng) >= 2:
        my_lat = my_loc.latlng[0]
        my_lon = my_loc.latlng[1]
    else:
        my_lat = 0
        my_lon = 0

    aurora_df = coords

    # Convert forecast time to local time.
    utc_dt = datetime.fromisoformat(aurora_df.iloc[0]['forecast'])
    local_dt = utc_dt.astimezone().replace(tzinfo=None)

    # Data colors
    aurora_color_ramp = [
        (0.00, '#000000'),
        (0.25, '#00FF00'),
        (0.50, '#00FF00'),
        (0.75, '#9933FF'),
        (1.00, '#FF0000')
    ]

    # Create Subplots
    fig = make_subplots(
        rows = 2,
        cols = 2,
        vertical_spacing = 0.1,
        row_heights = [0.75, 0.25],
        specs = [
            [{'type': 'mapbox', 'colspan': 2}, None],
            [{'type': 'xy', 'colspan': 2}, None]
        ]
    )

    # Initialize density map and add to subplot
    contour_trace = go.Densitymapbox(
        lat = aurora_df['lat'],
        lon = aurora_df['lon'],
        z = aurora_df['percent'],
        coloraxis = "coloraxis",
        radius = 30,  # Matches the downsampled grid spacing for smooth integration
        hoverinfo = "z",
        hovertemplate = "Aurora Chance: %{z:.1f}%<extra></extra>"
    )
    fig.add_trace(contour_trace, row=1, col=1)

    # Place user waypoint locator pin
    fig.add_trace(
        go.Scattermapbox(
            lat = [my_lat], lon=[my_lon],
            mode = 'markers+text',
            marker = dict(size=14, color='#00FFFF', opacity=0.9, symbol='circle'),
            text = ["You Are Here"], textposition="top right",
            name = "My Location", hoverinfo="text"
        ),
        row = 1, col = 1
    )

    # Create bar chart and add to subplot
    kp_data = kp_forecast

    # Defined values
    def get_bar_color(row):
        # Prediction color
        if row['observed'] == 'predicted':
            return '#9933FF'
        elif row['observed'] == 'estimated':
            return 'blue'

        # Otherwise (observed or estimated), color-code dynamically by the Kp value
        val = row['kp']
        if val >= 9: return '#8B0000'  # Dark Red
        if val >= 8: return '#FF0000'  # Red
        if val >= 7: return '#FF8C00'  # Orange
        if val >= 6: return '#FFA500'  # Light Orange
        if val >= 5: return '#FFFF00'  # Yellow
        return '#5CED73'  # Normal/Low Kp (Cyan background)

    # Map the function to create a custom color column
    kp_data['bar_color'] = kp_data.apply(get_bar_color, axis=1)

    # Row-by-row color mapping
    fig.add_trace(
        go.Bar(
            x = kp_data['time'],
            y = kp_data['kp'],
            marker = dict(
                color = kp_data['bar_color'],
                line = dict(width=0)
            ),
            customdata = kp_data['observed'],
            hovertemplate = (
                "Time: %{x}<br>"
                "Kp Index: %{y}<br>"
                "Status: %{customdata}<extra></extra>"
            ),
        ),
        row = 2, col = 1
    )

    fig.update_yaxes(title_text="Kp Index",
                     row = 2, col = 1,
                     range = [0,9],
                     dtick = 1,
                     fixedrange = True,
                     )

    fig.update_xaxes(title_text="Time", row=2, col=1, fixedrange = True)

    # Map layout configs
    fig.update_layout(
        dragmode = 'pan',
        title_text = 'Map of Aurora Chances',
        title_font_size = 32,
        title_font_weight = 'bold',
        title_x = 0.5,
        title_xref = 'container',
        title_subtitle_text = f'Forecast Time: {local_dt}',
        showlegend = False,
        mapbox = dict(
            style = "carto-darkmatter",
            zoom = 2,
            center = {"lat": my_lat, "lon": 0},
            bounds=dict(
                west=-180,
                south=-90,
                east=180,
                north=90
            )
        ),
    )

    # Color bar configs
    fig.update_coloraxes(
        colorscale = aurora_color_ramp,
        cmin = 0,
        cmax = 100,
        colorbar = dict(
            orientation = 'h',
            y = 0.32,
            yanchor = 'top',
            x = 0.5,
            xanchor = 'center',
            len = 0.6,
            thickness = 15
        ),
        colorbar_title_text = '% Aurora Chance',
        colorbar_outlinewidth = 2,
        colorbar_title_font_size = 16,
        colorbar_title_side = 'top',
    )


    # Write the map to an HTML file
    fig.write_html('map/aurora_location.html', config ={'scrollZoom': True})
