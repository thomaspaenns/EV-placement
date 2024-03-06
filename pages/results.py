import base64
import dash
import dash_bootstrap_components as dbc
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
    html.Div([
        html.Div([
            html.H3('Coverage Map',
                    style={"font-weight": "bold", 'display': 'inline-block'}),
            # html.A(id='download-link', children="Export Data", href="#", 
            #         style={'display': 'inline-block', 'margin-top':'5px'},
            #         title="Export data to CSV (will not export if model has not been run)"),
            dbc.Button("Export Data", id='download-link', 
                    style={'display': 'inline-block', 'margin-top':'5px'},
                    title="Export data to CSV (will not export if model has not been run)"),
        ], style={'display': 'flex', 'justify-content': 'space-between'}),
        html.Div(id='overall-stats', style={"font-weight": "bold"}),
        dcc.Graph(id='coverage-map')
    ], style={'marginLeft': '20px', 'marginRight': '20px'})
], style={'marginTop': '10px','backgroundColor': '#f8f9fa',})


@callback(
    [Output('overall-stats', 'children'),
     Output('download-link', 'href')],
    [Input('coverage', 'data'), Input(
        'util', 'data'), Input('wait_time', 'data')]
)
def update_overall_stats(coverage_data, util_data, wait_time):
    seg_count = 0
    tot_coverage = 0.0
    for k, v in coverage_data.items():
        seg_count += 1
        tot_coverage += v
    avg_coverage = round(tot_coverage/seg_count,2)
    station_count = 0
    tot_util = 0.0
    for k, v in util_data.items():
        station_count += 1
        tot_util += v
    avg_util = round(tot_util/station_count,2)
    tot_wait = 0.0
    for k, v in wait_time.items():
        tot_wait += v
    avg_wait = round(tot_wait/station_count,2)
    stat_str = ''
    download_link = None
    if avg_wait < 0 or avg_coverage < 0 or avg_util < 0:
        stat_str = 'Run the model to see your results'
    else:
        stat_str = f"Average Coverage: {round(avg_coverage*100,1)}%. Average Utilization: {round(avg_util*100,1)}%. Average Wait Time: {avg_wait} min."
        coverage_df = pd.DataFrame.from_dict(coverage_data, orient='index', columns=['Coverage'])
        util_df = pd.DataFrame.from_dict(util_data, orient='index', columns=['Util'])
        wait_df = pd.DataFrame.from_dict(wait_time, orient='index', columns=['Wait (minutes)'])
        export_df = util_df.join(wait_df).join(coverage_df, how='right')
        csv_string = export_df.to_csv(index_label='LHRS_num')
        csv_base64 = base64.b64encode(csv_string.encode()).decode()
        download_link = "data:text/csv;charset=utf-8;base64," + csv_base64
    return stat_str, download_link


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
                    text=f"Util: {round(util_data[lhrs_str]*100,1)}% | Avg wait: {wait_time[lhrs_str]} min | {row['Location Description']}",
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
        fig.add_trace(go.Scattermapbox(
            lat=group_lat,
            lon=group_lon,
            mode='lines',
            line=dict(width=4, color=color),
            text = f"Coverage: {round(100*covered_count/4,1)}%",
            hoverinfo='text' if covered_count >= 0 else 'none'
        ))
    return fig

# @callback(
#     Output('export-csv-button', 'n_clicks'),
#     [Input('export-csv-button', 'n_clicks'),
#      Input('coverage', 'data'), 
#      Input('util', 'data'),
#      Input('wait_time', 'data')]
# )
# def export_to_csv(n_clicks, coverage_data, util_data, wait_time):
#     if n_clicks > 0:
#         if coverage_data:
#             csv_string = pd.DataFrame.from_dict(coverage_data, orient='index', columns=['Coverage']).to_csv(index_label='Segment')
#             csv_string = "data:text/csv;charset=utf-8," + base64.b64encode(csv_string.encode()).decode()
#             return csv_string
#     return ""

if __name__ == '__main__':
    app.run_server(debug=True)
