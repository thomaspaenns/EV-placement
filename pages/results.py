import base64
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, dash_table, Input, Output
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
            dbc.Button("Export Data", id='download-link', 
                    style={'display': 'inline-block', 'margin-top':'5px'},
                    title="Export data to CSV (will not export if model has not been run)"),
        ], style={'display': 'flex', 'justify-content': 'space-between'}),
        html.Div(id='overall-stats', style={"font-weight": "bold"}),
        dbc.Spinner(fullscreen=False, children=[
            dcc.Graph(id='coverage-map'),
            html.Br(),
            html.H4("Insights", style={'font-weight': 'bold', 'text-align': 'center', 'margin-bottom':'10px'}),
            html.Div([
                dcc.Graph(id='time-coverage'),
            ], style={'width': '50%', 'align': 'left', 'display': 'inline-block'}),
            html.Div([
                dcc.Graph(id='budget-coverage'),
            ], style={'width': '50%', 'align': 'right', 'display': 'inline-block'}),
            html.Div(),
            html.Div([
                dcc.Graph(id='time-wait'),
            ], style={'width': '50%', 'align': 'left', 'display': 'inline-block'}),
            html.Div([
                dcc.Graph(id='budget-wait'),
            ], style={'width': '50%', 'align': 'right', 'display': 'inline-block'}),
            html.Br(),
            html.Div(id='export-table-container', style={'margin-top':'20px','margin-bottom': '20px'})
        ]),
    ], style={'marginLeft': '20px', 'marginRight': '20px'})
], style={'marginTop': '10px','backgroundColor': '#f8f9fa',})

def calculate_cost(row):
    if row['Charging Ports'] == 0:
        return "$0"
    elif row['Charging Ports'] == 2:
        return "$35,000"
    elif row['Charging Ports'] == 4:
        return "$56,000"
    elif row['Charging Ports'] == 8:
        return "$70,000"
    else:
        return 0 

@callback(
    [Output('overall-stats', 'children'),
     Output('download-link', 'href'),
     Output('export-table-container', 'children')],
    [Input('coverage', 'data'),
     Input('util', 'data'),
     Input('wait_time', 'data'),
     Input('optimal', 'data')],
)
def update_overall_stats(coverage_data, util_data, wait_time, optimal):
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
        export_table=None
    else:
        level_convert = {0:0, 1:2, 2:4, 3:8}
        stat_str = f"Average Coverage: {round(avg_coverage*100)}%. Average Utilization: {round(avg_util*100)}%. Average Wait Time: {avg_wait} min."
        coverage_df = pd.DataFrame.from_dict(coverage_data, orient='index', columns=['Coverage'])
        util_df = pd.DataFrame.from_dict(util_data, orient='index', columns=['Util'])
        wait_df = pd.DataFrame.from_dict(wait_time, orient='index', columns=['Wait (minutes)'])
        for i in optimal.keys():
            optimal[i] = level_convert[optimal[i]]
        port_df = pd.DataFrame.from_dict(optimal,orient='index', columns=['Charging Ports'])
        export_df = util_df.join(wait_df).join(coverage_df, how='right').join(port_df)
        csv_string = export_df.to_csv(index_label='LHRS_num')
        csv_base64 = base64.b64encode(csv_string.encode()).decode()
        download_link = "data:text/csv;charset=utf-8;base64," + csv_base64

        df.reset_index(drop=True, inplace=True)
        export_df.reset_index(drop=True, inplace=True)
        export_df = pd.concat([df, export_df], axis=1)[
            ['LHRS','Location Description','Util','Wait (minutes)', 'Charging Ports']]
        export_df = export_df[export_df['Util']>0]
        export_df['Util'] = round(export_df['Util']*100).astype(str) + "%"
        export_df['Cost'] = export_df.apply(calculate_cost, axis=1)
        export_table = html.Div([
            html.H4('Station Information', style={"font-weight": "bold", "text-align":"center"}),
            dash_table.DataTable(
            id='export-datatable',
            columns=[{"name": i, "id": i} for i in export_df.columns],
            data=export_df.to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_cell={
                'whiteSpace': 'normal',
                'textAlign': 'left',
                'minWidth': '80px',
                'maxWidth': '300px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
            })
        ])     
    return stat_str, download_link, export_table



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
        zoom=6
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
            zoom=6
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

@callback(
    [Output('budget-coverage', 'figure'),
     Output('time-coverage', 'figure'),
     Output('budget-wait', 'figure'),
     Output('time-wait', 'figure'),],
    Input('coverage', 'data')
)
def update_budget_coverage_plot(coverage_dict):
    # No Existing Infrastructure
    budget = [0.0,500000,1000000,1500000,2000000,3000000,4000000,5000000,6000000,7000000,8000000,9000000]
    coverage = [0.0, 0.27, 0.38, 0.41, 0.42, 0.48, 0.53, 0.58, 0.64, 0.75, 0.82, 1.0]
    util = [1.0, 0.71, 0.60, 0.41, 0.41, 0.34, 0.24, 0.23, 0.20, 0.18, 0.16, 0.15]
    wait = [None, 10.46, 5.18, 3.12, 2.73, 1.48, 0.86, 0.31, 0.19, 0.09, 0.03, 0.02]
    trace_coverage = go.Scatter(x=budget, y=coverage, mode='lines+markers', name='Coverage')
    trace_util = go.Scatter(x=budget, y=util, mode='lines+markers', name='Util')
    layout = go.Layout(
        title="<b>Utilization and Coverage by Budget</b> <br><sup>(Not including existing infrastructure)</sup>",
        xaxis=dict(title='Budget'),
        yaxis=dict(title='Percentage', tickformat=',.0%'))
    fig = go.Figure(data=[trace_coverage, trace_util], layout=layout)

    year = [2024, 2029, 2034, 2039, 2044, 2049]
    coverage_2 = [0.58, 0.33, 0.22, 0.16, 0.12,0.10]
    util_2 = [0.64, 0.90, 0.96, 0.99, 1.00, 1.00]
    wait_2 = [7.2, 13.3, 16.7, 18.1, 18.9, 19.3]
    trace_coverage_2 = go.Scatter(x=year, y=coverage_2, mode='lines+markers', name='Coverage')
    trace_util_2 = go.Scatter(x=year, y=util_2, mode='lines+markers', name='Util')
    layout_2 = go.Layout(
        title="<b>Utilization and Coverage by Year</b> <br><sup>(With existing infrastructure only)</sup>",
        xaxis=dict(title='Year'),
        yaxis=dict(title='Percentage', tickformat=',.0%'))
    fig_2 = go.Figure(data=[trace_coverage_2, trace_util_2], layout=layout_2)

    trace_wait_3 = go.Scatter(x=budget, y=wait, mode='lines+markers')
    layout_3 = go.Layout(
        title="<b>Wait Times by Budget</b> <br><sup>(Not including existing infrastructure)</sup>",
        xaxis=dict(title='Budget'),
        yaxis=dict(title='Minutes'))
    fig_3 = go.Figure(data=trace_wait_3, layout=layout_3)

    trace_wait_4 = go.Scatter(x=year, y=wait_2, mode='lines+markers')
    layout_4 = go.Layout(
        title="<b>Wait Times by Year</b> <br><sup>(With existing infrastructure only)</sup>",
        xaxis=dict(title='Year'),
        yaxis=dict(title='Minutes'))
    fig_4 = go.Figure(data=trace_wait_4, layout=layout_4)
    return fig, fig_2, fig_3, fig_4