import geocoder
from datetime import datetime
import plotly.graph_objects as go


# Create the interactive map
def create_map(coords, kp_forecast):

    # Get local lat and lon, if not found, use [0,0]
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

    fig = go.Figure()

    # Density Map Trace
    contour_trace = go.Densitymapbox(
        name = 'Aurora Chance',
        lat = aurora_df['lat'],
        lon = aurora_df['lon'],
        z = aurora_df['percent'],
        coloraxis = 'coloraxis',
        radius = 30,
        hoverinfo = 'z',
        hovertemplate = 'Aurora Chance: %{z:.1f}%<extra></extra>',
        visible = True
    )
    fig.add_trace(contour_trace)

    # User Location Pin Trace
    location_trace = go.Scattermapbox(
        lat = [my_lat], lon=[my_lon],
        mode = 'markers+text',
        marker = dict(size=14, color='#00FFFF', opacity=0.9, symbol='circle'),
        text = ['You Are Here'], textposition='top right',
        name = 'My Location', hoverinfo='text',
        visible = True
    )
    fig.add_trace(location_trace)

    # Process Kp Data
    kp_data = kp_forecast

    def get_bar_color(row):
        if row['observed'] == 'predicted':
            return '#9933FF'
        elif row['observed'] == 'estimated':
            return 'blue'
        val = row['kp']
        if val >= 9: return '#8B0000'
        if val >= 8: return '#FF0000'
        if val >= 7: return '#FF8C00'
        if val >= 6: return '#FFA500'
        if val >= 5: return '#FFFF00'
        return '#5CED73'

    kp_data['bar_color'] = kp_data.apply(get_bar_color, axis=1)

    # Bar Chart Trace
    bar_trace = go.Bar(
        name='KP Index',
        x=kp_data['time'],
        y=kp_data['kp'],

        customdata=list(zip(kp_data['kp'], kp_data['observed'])),
        textposition='outside',
        texttemplate='%{customdata[0]:.1f}<br>(%{customdata[1]})',

        marker=dict(
            color=kp_data['bar_color'],
            line=dict(width=0)
        ),

        hovertemplate=(
            'Time: %{x}<br>'
            'Kp Index: %{customdata[0]:.1f}<br>'
            'Status: %{customdata[1]}<extra></extra>'
        ),
        visible=False  # Hidden on initial load
    )
    fig.add_trace(bar_trace)

    # Configure Axes
    fig.update_yaxes(title_text='Kp Index', range=[0,9], dtick=1, fixedrange=True, visible=False)
    fig.update_xaxes(title_text='Time', fixedrange=True, visible=False)

    # Empty mapbox style schema
    empty_mapbox_style = {"version": 8, "sources": {}, "layers": []}

    # Base Layout Configurations
    fig.update_layout(
        template = "plotly_dark",
        title_text = 'Map of Aurora Chance',
        title_font_size = 32,
        title_font_weight = 'bold',
        title_x = 0.5,
        title_xref = 'container',
        title_subtitle_text = f'Forecast Time: {local_dt}',
        showlegend = False,
        plot_bgcolor = '#111111',
        paper_bgcolor = '#111111',
        mapbox = dict(
            style = 'carto-darkmatter',
            zoom = 2,
            center = {'lat': my_lat, 'lon': 0},
            bounds=dict(west=-180, south=-90, east=180, north=90)
        ),
        # Create tabs for each chart
        updatemenus=[
            dict(
                type='buttons',
                direction='right',
                x=0.1,
                y=1.15,
                showactive=True,
                font=dict(color='black'),
                buttons=[
                    dict(
                        label='Aurora Chance',
                        method='update',
                        args=[
                            {'visible': [True, True, False]},
                            {
                                'title.text': 'Map of Aurora Chance',
                                'title.subtitle.text': f'Forecast Time: {local_dt}',
                                'coloraxis.colorbar.visible': True,
                                'xaxis.visible': False,
                                'yaxis.visible': False,
                                'mapbox.style': 'carto-darkmatter',
                                'dragmode': 'pan',
                            }
                        ],
                    ),
                    dict(
                        label='KP Index',
                        method='update',
                        args=[
                            {'visible': [False, False, True]},
                            {
                                'title.text': 'KP Index Forecast',
                                'title.subtitle.text': None,
                                'coloraxis.colorbar.visible': False,
                                'xaxis.visible': True,
                                'yaxis.visible': True,
                                'mapbox.style': empty_mapbox_style,
                                'dragmode': 'zoom',
                            }
                        ],
                    ),
                ],
            )
        ]
    )

    # Color bar configs
    fig.update_coloraxes(
        colorscale = aurora_color_ramp,
        cmin = 0,
        cmax = 100,
        colorbar = dict(
            orientation = 'h',
            y = -0.1,
            yanchor = 'bottom',
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
