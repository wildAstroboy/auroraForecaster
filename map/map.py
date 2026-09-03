import textwrap
import geocoder
from datetime import datetime, UTC, timedelta
import plotly.graph_objects as go


# Create the interactive map
def create_map(aurora_coords, kp_forecast, alerts, p_short_energy, p_long_energy, s_short_energy, s_long_energy, timeline_range, carto_api_key):

    # Get local lat and lon, if not found, use [0,0]
    my_loc = geocoder.ip('me')

    if my_loc and my_loc.latlng and len(my_loc.latlng) >= 2:
        my_lat = my_loc.latlng[0]
        my_lon = my_loc.latlng[1]
    else:
        my_lat = 0
        my_lon = 0

    # Aurora Data
    aurora_df = aurora_coords

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

    # Init Plotly
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

    # Alerts Trace
    raw_alerts_message = alerts.get('message')
    wrapped_text = textwrap.wrap(raw_alerts_message, width=108)
    formatted_alerts_message = '<br>'.join(wrapped_text)

    fig.add_annotation(
        text = f'<u><b>LATEST ALERT</b></u>: {formatted_alerts_message}',
        xref = 'paper', yref = 'paper',
        x = 0.6, y = 1.14,
        xanchor = 'center',
        yanchor = 'middle',
        showarrow = False,
        align = 'center',
        font = dict(size=14, color='#AAAAAA')
    )

    # Kp Index Data
    kp_data = kp_forecast

    # Bar colors
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
        name = 'KP Index',
        x = kp_data['time'],
        y = kp_data['kp'],

        xaxis = 'x',
        yaxis = 'y',

        customdata = [list(x) for x in zip(kp_data['kp'], kp_data['observed'])],
        textposition = 'outside',
        texttemplate = '%{customdata[0]:.1f}<br>(%{customdata[1]})',

        marker = dict(
            color = kp_data['bar_color'],
            line = dict(width=0)
        ),
        hoverinfo = 'all',
        hovertemplate = (
            'Time: %{x}<br>'
            'Kp Index: %{customdata[0]:.1f}<br>'
            'Status: %{customdata[1]}<extra></extra>'
        ),
        visible = False
    )
    fig.add_trace(bar_trace)

    # X-ray Data
    p_short_df = p_short_energy
    p_long_df = p_long_energy
    s_short_df = s_short_energy
    s_long_df = s_long_energy

    # Add line trace
    # Primary Short
    line_trace_p_short = go.Scatter(
        name = 'GOES-18 Short',
        x = p_short_df['time_tag'],
        y = p_short_df['flux'],
        xaxis = 'x2',
        yaxis = 'y2',
        visible = 'legendonly',
    )

    fig.add_trace(line_trace_p_short)

    # Primary Long
    line_trace_p_long = go.Scatter(
        name = 'GOES-18 Long',
        x = p_long_df['time_tag'],
        y = p_long_df['flux'],
        xaxis = 'x2',
        yaxis = 'y2',
        visible = 'legendonly',
    )

    fig.add_trace(line_trace_p_long)

    # Secondary Short
    line_trace_s_short = go.Scatter(
        name = 'GOES-19 Short',
        x = s_short_df['time_tag'],
        y = s_short_df['flux'],
        xaxis = 'x2',
        yaxis = 'y2',
        visible = 'legendonly',
    )

    fig.add_trace(line_trace_s_short)

    # Secondary Long
    line_trace_s_long = go.Scatter(
        name = 'GOES-19 Long',
        x = s_long_df['time_tag'],
        y = s_long_df['flux'],
        xaxis = 'x2',
        yaxis = 'y2',
        visible = 'legendonly',
    )

    fig.add_trace(line_trace_s_long)

    # Empty mapbox style schema
    empty_mapbox_style = {'version': 8, 'sources': {}, 'layers': []}

    # Base Layout Configurations
    fig.update_layout(
        template = 'plotly_dark',
        title_text = 'Aurora Chance',
        title_font_size = 32,
        title_font_weight = 'bold',
        title_x = 0.03,
        title_y = 0.95,
        title_xref = 'container',
        title_subtitle_text = f'Forecast Time: {local_dt}',
        showlegend = False,
        plot_bgcolor = '#111111',
        paper_bgcolor = '#111111',
        margin = dict(t=200, b=50, l=50, r=50),

        xaxis = dict(visible = False, domain = [0, 1], fixedrange = True),
        yaxis = dict(visible = False, domain = [0, 1], range = [0, 9], fixedrange = True),
        xaxis2 = dict(visible = False, domain = [0, 1], overlaying = 'x', fixedrange = True),
        yaxis2 = dict(visible = False, domain = [0, 1], overlaying = 'y', range = [-9, -2], type = 'log', fixedrange = True),

        mapbox = dict(
            layers = [
                dict(
                    sourcetype = "raster",
                    source = [
                        f"https://basemaps.cartocdn.com/rastertiles/dark_all/{{z}}/{{x}}/{{y}}.png?key={carto_api_key}"
                    ],
                    below = "traces",
                    sourceattribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attributions">CARTO</a>'
                )
            ],
            style = 'carto-darkmatter',
            zoom = 2,
            center = {'lat': my_lat, 'lon': 0},
            bounds = dict(west=-180, south=-90, east=180, north=90)
        ),
        # Create tabs for each chart
        updatemenus = [
            dict(
                type = 'buttons',
                direction = 'right',
                x = 0.18,
                y = 1.06,
                showactive = True,
                font = dict(color='black'),
                buttons = [
                    # Aurora Map Tab
                    dict(
                        label = 'Aurora Chance',
                        method = 'update',
                        args = [
                            {'visible': [True, True, False, False, False, False, False]},
                            {
                                'title.text': 'Map of Aurora Chance',
                                'title.x': 0.03,
                                'title.y': 0.95,
                                'title.subtitle.text': f'Forecast Time: {local_dt}',
                                'coloraxis.colorbar.visible': True,

                                'xaxis.visible': False, 'yaxis.visible': False,
                                'xaxis2.visible': False, 'yaxis2.visible': False,

                                'xaxis2.rangeslider.visible': False,
                                'xaxis2.rangeselector.visible': False,

                                'mapbox.visible': True,
                                'mapbox.domain': dict(x=[0, 1], y=[0, 1]),
                                'mapbox.style': 'carto-darkmatter',
                                'mapbox.layers': [
                                    dict(
                                        sourcetype = "raster",
                                        source = [
                                            f"https://basemaps.cartocdn.com/rastertiles/dark_all/{{z}}/{{x}}/{{y}}.png?key={carto_api_key}"
                                        ],
                                        below = "traces",
                                        sourceattribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attributions">CARTO</a>'
                                    )
                                ],
                                'dragmode': 'pan',
                                'margin.t': 200,
                                'margin.b': 50,
                                'margin.l': 50,
                                'margin.r': 50,
                                'showlegend': False,
                                'hovermode': 'closest',
                                'updatemenus[1].visible': False
                            }
                        ],
                    ),
                    # Kp Index Tab
                    dict(
                        label = 'KP Index',
                        method = 'update',
                        args = [
                            {'visible': [False, False, True, False, False, False, False]},
                            {
                                'title.text': 'KP Index Forecast',
                                'title.x': 0.03,
                                'title.y': 0.93,
                                'title.subtitle.text': None,
                                'coloraxis.colorbar.visible': False,

                                'xaxis.visible': True, 'yaxis.visible': True,
                                'xaxis2.visible': False, 'yaxis2.visible': False,

                                'xaxis2.rangeslider.visible': False,
                                'xaxis2.rangeselector.visible': False,

                                'yaxis.type': 'linear',
                                'yaxis.range': [0,9],
                                'xaxis.title.text': 'Time',
                                'yaxis.title.text': 'Kp Index',

                                'mapbox.visible': False,
                                'mapbox.domain': dict(x=[0, 0.01], y=[0, 0.01]),
                                'mapbox.style': empty_mapbox_style,
                                'dragmode': 'zoom',
                                'margin.t': 200,
                                'margin.b': 50,
                                'margin.l': 50,
                                'margin.r': 50,
                                'showlegend': False,
                                'hovermode': 'x',
                                'updatemenus[1].visible': False
                            }
                        ],
                    ),
                    # X-Ray Flux Tab
                    dict(
                        label = 'X-Ray Flux',
                        method = 'update',
                        args = [
                            {'visible': [False, False, False, True, True, True, True]},
                            {
                                'title.text': 'X-Ray Flux',
                                'title.x': 0.03,
                                'title.y': 0.93,
                                'title.subtitle.text': None,
                                'coloraxis.colorbar.visible': False,

                                'xaxis.visible': False, 'yaxis.visible': False,
                                'xaxis2.visible': True, 'yaxis2.visible': True,
                                'xaxis2.title.text': 'Time Tag',
                                'xaxis2.type': 'date',

                                'yaxis2.title.text': 'Flux Watts / m²',
                                'yaxis2.type': 'log',
                                'yaxis2.range': [-10, -2],
                                'yaxis2.dtick': None,

                                'mapbox.visible': False,
                                'mapbox.domain': dict(x=[0, 0.01], y=[0, 0.01]),
                                'mapbox.style': empty_mapbox_style,
                                'dragmode': 'zoom',
                                'margin.t': 200,
                                'margin.b': 50,
                                'margin.l': 50,
                                'margin.r': 50,
                                'showlegend': True,
                                'hovermode': 'x',
                                'updatemenus[1].visible': True,
                                'legend': dict(
                                    yanchor = "top",
                                    y = 0.95,
                                    xanchor = "right",
                                    x = 0.98,
                                    bgcolor = "rgba(17, 17, 17, 0.6)",
                                    font = dict(color="#FFFFFF")
                                )
                            }
                        ]
                    ),
                ],
            ),

            # Time Range Buttons for X-Ray Flux
            dict(
                type = 'buttons',
                direction = 'right',
                x = 0.52,
                y = 1.06,
                active = 0,
                visible = False,
                font = dict(color='black'),
                buttons = [
                    dict(
                        label = "Full View",
                        method = "relayout",
                        args = [{"xaxis2.range": timeline_range}]
                    ),
                    dict(
                        label = "Last 3 Days",
                        method = "relayout",
                        args = [{"xaxis2.range": [
                            (datetime.now(UTC) - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
                            datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
                        ]}]
                    ),
                    dict(
                        label = "Last 24 Hours",
                        method = "relayout",
                        args = [{"xaxis2.range": [
                            (datetime.now(UTC) - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                            datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
                        ]}]
                    ),
                    dict(
                        label = "Last 6 Hours",
                        method = "relayout",
                        args = [{"xaxis2.range": [
                            (datetime.now(UTC) - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S'),
                            datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
                        ]}]
                    )
                ]
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
    fig.write_html('map/aurora_location.html', config = {'scrollZoom': True})