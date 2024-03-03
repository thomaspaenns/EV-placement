# archive.py
import dash
from dash import dcc, html, callback, Input, Output
import plotly.graph_objs as go
import pandas as pd

# Load your data
df = pd.read_csv('data/401_Data.csv', encoding='ISO-8859-1')

# Register the page in your Dash app
dash.register_page(__name__)

# Mapbox Access Token
mapbox_access_token = 'pk.eyJ1IjoienVoYXlyODMiLCJhIjoiY2xrbHc0emVwMHE2NjNsbXZ3cTh2MHNleCJ9.CMVZ7OC27bxxARKMRTttfQ'

layout = html.Div([
    html.H1('Coverage Map'),
    dcc.Graph(id='coverage-map')
])


@callback(
    Output('coverage-map', 'figure'),
    [Input('coverage', 'data'), Input(
        'util', 'data'), Input('wait_time', 'data')]
)
def update_coverage_map(coverage_data, util_data, wait_time):
    fig = go.Figure()

    # Apply the Mapbox access token
    fig.update_layout(mapbox=dict(
        accesstoken=mapbox_access_token,
        style='light',  # or 'dark', 'satellite', 'streets', etc.
        center=dict(lat=44.0, lon=-79.0),  # Center on Ontario
        zoom=5
    ))

    # Draw coverage lines
    if coverage_data:
        fig = draw_coverage_lines(coverage_data, fig)

    # Add points for selected stations
    if util_data:
        for index, row in df.iterrows():
            lhrs_str = str(row['LHRS'])
            if float(util_data.get(lhrs_str, -1)) >= 0:  # Station is selected
                fig.add_trace(go.Scattermapbox(
                    lat=[row['Latitude']],
                    lon=[row['Longitude']],
                    mode='markers',
                    marker=dict(color='purple', size=10),
                    text=row['Location Description'],
                    hoverinfo='text'
                ))

    # Set up map layout
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        showlegend=False,
        mapbox=dict(
            center=dict(lat=44.0, lon=-79.0),  # Center on Ontario
            zoom=5
        )
    )

    return fig


def draw_coverage_lines(coverage_dict, fig):
    sorted_lhrs = sorted([int(k) for k in coverage_dict.keys()])
    segments_to_color = {"green": [], "yellow": [], "red": [], "gray": []}

    i = 0
    while i < len(sorted_lhrs):
        segment_group = sorted_lhrs[i:i+4]
        i = i + 3
        covered_count = 0
        for j in segment_group:
            covered_count += float(coverage_dict.get(str(j), 0))
        color = "gray"
        if covered_count > 3:
            color = "green"
        elif covered_count > 1 and covered_count <= 3:
            color = "orange"
        elif covered_count <= 1 and covered_count >= 0:
            color = "red"
        else:
            color = "gray"
        group_lat = []
        group_lon = []
        for lhrs in segment_group:
            lat, lon = df[df['LHRS'] == lhrs][[
                'Latitude', 'Longitude']].iloc[0]
            group_lat.append(lat)
            group_lon.append(lon)
        # lat1, lon1 = df[df['LHRS'] == segment_group[0]
        #                 ][['Latitude', 'Longitude']].iloc[0]
        # lat2, lon2 = df[df['LHRS'] == segment_group[-1]
        #                 ][['Latitude', 'Longitude']].iloc[0]
        # latitudes = [lat1, lat2]
        # longitudes = [lon1, lon2]
        fig.add_trace(go.Scattermapbox(
            lat=group_lat,
            lon=group_lon,
            mode='lines',
            line=dict(width=4, color=color),
            hoverinfo='none'
        ))

        # for lhrs in segment_group:
        #     lat, lon = df[df['LHRS'] == lhrs][['Latitude', 'Longitude']].iloc[0]
        #     segments_to_color[color].append((lat, lon))

    # for color, coordinates in segments_to_color.items():
    #     if coordinates:
    #         latitudes, longitudes = zip(*coordinates)
    #         fig.add_trace(go.Scattermapbox(
    #             lat=latitudes,
    #             lon=longitudes,
    #             mode='lines',
    #             line=dict(width=4, color=color),
    #             hoverinfo='none'
    #         ))

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
