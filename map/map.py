import geocoder
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Create the interactive map
def create_map(coords):

    #Get local lat and lon, if not found, use [0,0]
    my_loc = geocoder.ip('me')

    if my_loc.latlng[0] and my_loc.latlng[1]:
        my_lat = my_loc.latlng[0]
        my_lon = my_loc.latlng[1]
    else:
        my_lat = 0
        my_lon = 0

    df = coords

    # Convert forecast time to local time.
    utc_dt = datetime.fromisoformat(df.iloc[0]['forecast'])
    local_dt = utc_dt.astimezone().replace(tzinfo=None)

    # Data colors
    aurora_color_ramp = [
        (0.00, '#000000'),  # Keep 0% completely transparent/black if desired
        (0.25, '#00FF00'),  # 10% probability turns bright green
        (0.50, '#00FF00'),  # Stays green through 40% probability
        (0.75, '#9933FF'),  # Transitions to intense purple at 70% probability
        (1.00, '#FF0000')  # ONLY turns deep red when hitting 100% probability
    ]

    # Initialize map
    fig = px.density_map(
        df,
        lat='lat',
        lon='lon',
        z='percent',
        range_color=[0, 100],
        color_continuous_scale=aurora_color_ramp,
        map_style="carto-darkmatter",

        # Zoom and size blending
        radius=7,  # LOWER RADIUS: Keeps compressed global points from blowing up to red
        zoom=1.5,  # INITIAL ZOOM: Loads the entire flat world overview instantly
        center={"lat": 20, "lon": 0}
    )

    # Place marker at your location on map
    fig.add_trace(
        go.Scattermap(
            lat=[my_lat],
            lon=[my_lon],
            mode='markers+text',
            marker=dict(
                size=14,
                color='#00FFFF',  # Cyan contrast pin to cut through green aurora
                opacity=0.9,
                symbol='circle'  # Renders a sleek modern waypoint dot
            ),
            text=["You Are Here"],
            textposition="top right",
            name="My Location",
            hoverinfo="text"
        )
    )

    # Map layout configs
    fig.update_layout(
        title_text = 'Map of Aurora Chances',
        title_font_size = 32,
        title_font_weight = 'bold',
        title_x=0.5,
        title_xref='container',
        title_subtitle_text = f'Forecast Time: {local_dt}',
        margin = dict(
            t = 100,
        ),
        showlegend = False
    )

    # Color bar configs
    fig.update_coloraxes(
        colorbar_title_text = '% Aurora Chance',
        colorbar_outlinewidth = 2,
        colorbar_title_font_size = 16,
        colorbar_title_side = 'top',
        colorbar_x = 1,
    )

    # Write the map to an HTML file
    fig.write_html('map/aurora_location.html')