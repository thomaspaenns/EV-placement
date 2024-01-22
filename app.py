from model.model import Model
from simulation.simulation import Simulation

import dash
from dash import dcc, html, Dash
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import dash_bootstrap_components as dbc
from dash import no_update
from geopy.distance import great_circle


# Load CSV and select only required columns
df = pd.read_csv('401_Data.csv', encoding='ISO-8859-1')

# Load alt fuel stations data
alt_fuel_df = pd.read_csv(
    'alt_fuel_stations (Jan 19 2024).csv', encoding='utf8')

# Create a polyline from the latitude and longitude of the 401 data
polyline_401 = list(zip(df['Latitude'], df['Longitude']))


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
    style={'height': '100vh', 'width': '100vw', 'display': 'flex', 'flexDirection': 'column'},
    children=[
        html.Div(
            [
                dbc.Button("Toggle Stations", id="toggle-stations", n_clicks=0, style={'marginRight': '20px'}),
                html.Div(
                    dcc.Slider(
                        id='selected-year-slider',
                        min=2024,
                        max=2049,
                        step=5,
                        value=2024,
                        marks={year: str(year) for year in range(2024, 2050, 5)},
                        disabled=False,
                    ),
                    style={'width': '60%', 'marginRight': '20px', 'marginLeft': '20px'}
                ),
                dbc.Button("Confirm", id="confirm-year", n_clicks=0, style={'marginLeft': '10px'}),
                dbc.Button("Edit", id="edit-year", n_clicks=0, style={'marginLeft': '10px', 'display': 'none'}),
            ],
            style={
                'height': '10vh',
                'backgroundColor': '#f8f9fa',
                'display': 'flex',
                'justifyContent': 'flex-start',
                'alignItems': 'center',
                'padding': '10px'
            }
        ),
        html.Div(
            style={'flexGrow': 1},
            children=[
                dcc.Graph(
                    id='ontario-map',
                    style={'height': '100%', 'width': '100%'},
                    figure={
                        'data': [go.Scattermapbox(
                            lat=df['Latitude'],
                            lon=df['Longitude'],
                            mode='markers',
                            marker={'color': ['grey']*len(df), 'size': 10},
                            text=df['Location Description'],
                            hoverinfo='text'
                        )],
                        'layout': go.Layout(
                            mapbox=dict(
                                accesstoken=mapbox_access_token,
                                center=ontario_location,
                                zoom=6.8
                            ),
                            margin={'l': 0, 'r': 0, 't': 0, 'b': 0}
                        )
                    }
                )
            ]
        ),
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
                    dbc.Button("Confirm", id="modal-confirm", n_clicks=0, disabled=True)
                )
            ],
            id="modal",
            is_open=False,
        ),
        dbc.Modal(
            [
                dbc.ModalHeader("Remove Station"),
                dbc.ModalBody("Are you sure you want to remove this station?"),
                dbc.ModalFooter(
                    dbc.Button("Confirm Removal", id="modal-remove-confirm", n_clicks=0)
                )
            ],
            id="remove-modal",
            is_open=False,
        ),
        html.Pre(id='clicked-data', style={'whiteSpace': 'pre-wrap'}),
        html.Div(id='stored-year', style={'display': 'none'})  # For storing selected year after confirmation
    ]
)

# Additional modal for confirming the removal of a station
remove_modal = dbc.Modal(
    [
        dbc.ModalHeader("Remove Station"),
        dbc.ModalBody("Are you sure you want to remove this station?"),
        dbc.ModalFooter(
            dbc.Button("Confirm Removal",
                       id="modal-remove-confirm", n_clicks=0)
        )
    ],
    id="remove-modal",
    is_open=False,
)

app.layout.children.append(remove_modal)
# Store the selected year in a hidden div after confirmation
app.layout.children.append(html.Div(id='stored-year', style={'display': 'none'}))



def is_within_radius(station_lat, station_lon, polyline, radius_km=5):
    for point in polyline:
        if great_circle((station_lat, station_lon), point).kilometers <= radius_km:
            return True
    return False


# Filter alt fuel stations that are within 5km of the 401 polyline
relevant_stations = alt_fuel_df[alt_fuel_df.apply(lambda x: is_within_radius(
    x['Latitude'], x['Longitude'], polyline_401), axis=1)]


@app.callback(
    [Output('selected-year-slider', 'disabled'),
     Output('edit-year', 'style'),
     Output('confirm-year', 'style'),
     Output('stored-year', 'children')],
    [Input('confirm-year', 'n_clicks'),
     Input('edit-year', 'n_clicks')],
    [State('selected-year-slider', 'value'),
     State('selected-year-slider', 'disabled')]
)
def lock_unlock_slider(confirm_clicks, edit_clicks, year_value, is_disabled):
    ctx = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if ctx == 'confirm-year':
        return True, {}, {'display': 'none'}, year_value
    elif ctx == 'edit-year':
        return False, {'display': 'none'}, {}, no_update
    return is_disabled, {}, {'display': 'none'} if is_disabled else {}, no_update


# Assuming your app initialization and other setups are done above

@app.callback(
    Output('modal-confirm', 'disabled'),
    [Input('station-level-radio', 'value')]
)
def toggle_modal_confirm_button(level_selected):
    return level_selected is None  # Returns True to disable if no level is selected, False to enable if a level is selected


@app.callback(
    Output('ontario-map', 'figure'),
    [Input('modal-confirm', 'n_clicks'),
     Input('modal-remove-confirm', 'n_clicks'),
     Input('toggle-stations', 'n_clicks')],
    [State('station-level-radio', 'value'),
     State('ontario-map', 'clickData'),
     State('ontario-map', 'figure')]
)
def update_map_on_modal(station_confirm_clicks, remove_confirm_clicks, toggle_clicks, selected_level, clickData, fig):
    global clicked_points_df, marker_colors, clicked_lhrs_dict
    ctx = dash.callback_context

    input_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if clickData and (input_id == 'modal-confirm' or input_id == 'modal-remove-confirm'):
        point_index = clickData['points'][0]['pointIndex']
        lhrs = df.iloc[point_index]['LHRS']

        if input_id == 'modal-confirm' and station_confirm_clicks > 0:
            marker_colors[point_index] = 'green'
            clicked_lhrs_dict[lhrs] = selected_level
        elif input_id == 'modal-remove-confirm' and remove_confirm_clicks > 0:
            marker_colors[point_index] = 'grey'
            clicked_lhrs_dict[lhrs] = 0

        fig['data'][0]['marker']['color'] = marker_colors

    if input_id == 'toggle-stations':
        show_stations = toggle_clicks % 2 == 1

        if show_stations:
            stations_info = {}
            for index, row in relevant_stations.iterrows():
                unique_key = f"{row['Station Name']}_{row['Latitude']}_{row['Longitude']}"
                level = 'Level Unknown'
                if pd.notna(row['EV DC Fast Count']):
                    level = 'Level 3'
                elif pd.notna(row['EV Level2 EVSE Num']):
                    level = 'Level 2'
                elif pd.notna(row['EV Level1 EVSE Num']):
                    level = 'Level 1'
                
                stations_info[unique_key] = {
                    'name': row['Station Name'],
                    'level': level,
                    'latitude': row['Latitude'],
                    'longitude': row['Longitude']
                }

            # Print the stations_info dictionary to the terminal
            # print(stations_info)

            latitudes = [info['latitude'] for info in stations_info.values()]
            longitudes = [info['longitude'] for info in stations_info.values()]
            hover_texts = [f"{info['name']} - {info['level']}" for info in stations_info.values()]

            fig['data'].append(go.Scattermapbox(
                lat=latitudes,
                lon=longitudes,
                mode='markers',
                marker={'color': 'blue', 'size': 8},
                text=hover_texts,
                hoverinfo='text'
            ))
        else:
            if len(fig['data']) > 1:
                fig['data'].pop()

    fig['layout']['showlegend'] = False
    return fig


# Updated callback for handling modals
@app.callback(
    Output('modal', 'is_open'),
    Output('remove-modal', 'is_open'),
    [Input('ontario-map', 'clickData'),
     Input('modal-confirm', 'n_clicks'),
     Input('modal-remove-confirm', 'n_clicks')],
    [State('modal', 'is_open'),
     State('remove-modal', 'is_open')]
)
def handle_modal(clickData, confirm_clicks, remove_confirm_clicks, is_add_modal_open, is_remove_modal_open):
    ctx = dash.callback_context

    if not ctx.triggered:
        # No input has been triggered, return the current states
        return is_add_modal_open, is_remove_modal_open

    input_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if input_id == 'ontario-map' and clickData:
        point_index = clickData['points'][0]['pointIndex']
        if marker_colors[point_index] == 'green':
            # If the circle is green, open the remove modal
            return False, True
        else:
            # If the circle is grey, open the add modal
            return True, False
    elif input_id in ['modal-confirm', 'modal-remove-confirm']:
        # Close both modals on confirm button click
        return False, False

    # In all other cases, return the current states
    return is_add_modal_open, is_remove_modal_open


# Global variable to store the previous state of clicked_lhrs_dict
prev_clicked_lhrs_dict = clicked_lhrs_dict.copy()


@app.callback(
    [Output('clicked-data', 'children')],
    [Input('modal-confirm', 'n_clicks'),
     Input('modal-remove-confirm', 'n_clicks')],
    [State('ontario-map', 'clickData')]
)
def display_click_data(confirm_clicks, remove_confirm_clicks, clickData):
    global clicked_points_df, marker_colors, clicked_lhrs_dict, prev_clicked_lhrs_dict

    ctx = dash.callback_context

    if not ctx.triggered:
        return [no_update]  # No button click, no update

    # Compare the current state with the previous state
    changed_lhrs = {lhrs: status for lhrs, status in clicked_lhrs_dict.items(
    ) if clicked_lhrs_dict[lhrs] != prev_clicked_lhrs_dict[lhrs]}

    # Print only the changed key-value pairs
    if changed_lhrs:
        print("Changed LHRS Status:")
        for lhrs, status in changed_lhrs.items():
            print(f"LHRS: {lhrs}, Status: {status}")

    # Update the previous state for the next comparison
    prev_clicked_lhrs_dict = clicked_lhrs_dict.copy()

    return [no_update]


if __name__ == '__main__':
    app.run_server(debug=True)