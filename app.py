from model.model import Model
from simulation.simulation import Simulation

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import dash_bootstrap_components as dbc


# Load CSV and select only required columns
df = pd.read_csv('401_Data.csv', encoding='ISO-8859-1')

# Initialize a dictionary to track clicked LHRS
clicked_lhrs_dict = {lhrs: 0 for lhrs in df['LHRS']}

# Import model and simulation
# model = Model(df)
# sim = Simulation(df)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Map configuration
mapbox_access_token = 'pk.eyJ1IjoienVoYXlyODMiLCJhIjoiY2xrbHc0emVwMHE2NjNsbXZ3cTh2MHNleCJ9.CMVZ7OC27bxxARKMRTttfQ'
ontario_location = {'lat': 44.0, 'lon': -79.0}  # Approximate center of Ontario

# DataFrame to store clicked points
clicked_points_df = pd.DataFrame(
    columns=['Location Description', 'lat', 'lon'])
# List of 'grey' colors, one for each point
marker_colors = ['grey' for _ in range(len(df))]
app.layout = html.Div(
    style={'height': '100vh', 'width': '100vw', 'margin': '0px'},
    children=[
        dcc.Graph(
            id='ontario-map',
            style={'height': '100%', 'width': '100%'},
            figure={
                'data': [go.Scattermapbox(
                    lat=df['Latitude'],
                    lon=df['Longitude'],
                    mode='markers',
                    marker={'color': marker_colors, 'size': 10},
                    text=df['Location Description'],  # Display on hover
                    hoverinfo='text'
                )],
                'layout': go.Layout(
                    mapbox=dict(
                        accesstoken=mapbox_access_token,
                        center=ontario_location,
                        zoom=5
                    ),
                    margin={'l': 0, 'r': 0, 't': 0, 'b': 0}
                )
            }
        ),
        html.Pre(id='clicked-data'),
        dbc.Modal(
            [
                dbc.ModalHeader("Select Station Level"),
                dbc.ModalBody(
                    dbc.RadioItems(
                        options=[
                            {"label": "Level 1", "value": 1},
                            {"label": "Level 2", "value": 2},
                            {"label": "Level 3", "value": 3}
                        ],
                        id="station-level-radio",
                        inline=True
                    )
                ),
                dbc.ModalFooter(
                    dbc.Button("Confirm", id="modal-confirm", n_clicks=0)
                )
            ],
            id="modal",
            is_open=False,
        )
    ]
)

# Place this callback right after the app.layout definition


@app.callback(
    Output('modal', 'is_open'),
    Input('ontario-map', 'clickData'),
    State('modal', 'is_open')
)
def toggle_modal(clickData, is_open):
    if clickData:
        return not is_open
    return is_open


# Place this callback right after the first callback
@app.callback(
    Output('ontario-map', 'figure'),
    [Input('modal-confirm', 'n_clicks')],
    [State('station-level-radio', 'value'),
     State('ontario-map', 'clickData'),
     State('ontario-map', 'figure')]
)
def update_map_on_modal(n_clicks, selected_level, clickData, fig):
    global clicked_points_df, marker_colors, clicked_lhrs_dict

    if n_clicks > 0 and clickData:
        point_index = clickData['points'][0]['pointIndex']
        lhrs = df.iloc[point_index]['LHRS']

        # Update color and clicked_lhrs_dict based on selected level
        if selected_level:
            marker_colors[point_index] = 'green'
            clicked_lhrs_dict[lhrs] = selected_level
        else:
            marker_colors[point_index] = 'grey'
            clicked_lhrs_dict[lhrs] = 0

        # Update the marker colors in the figure
        fig['data'][0]['marker']['color'] = marker_colors

        # Return updated figure
        return fig

    # Return the figure unchanged if no level is selected
    return fig


@app.callback(
    Output('clicked-data', 'children'),
    [Input('ontario-map', 'clickData')]
)
def display_click_data(clickData):
    global clicked_points_df, marker_colors, clicked_lhrs_dict

    # Prepare a string to display the current state of clicked LHRs
    clicked_lhrs_status = '\n'.join([f'LHRS: {lhrs}, Status: {status}'
                                     for lhrs, status in clicked_lhrs_dict.items()])

    return clicked_lhrs_status


if __name__ == '__main__':
    app.run_server(debug=True)
