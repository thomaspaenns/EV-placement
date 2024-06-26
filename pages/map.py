from model.model import Model
from simulation.sim import Simulation

import dash
from dash import dcc, html, Dash, callback
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import dash_bootstrap_components as dbc
from dash import no_update
from geopy.distance import great_circle
from dash import callback_context as ctx

dash.register_page(__name__)

# Load CSV and select only required columns
df = pd.read_csv('data/401_Data.csv', encoding='ISO-8859-1')

# Load alt fuel stations data
alt_fuel_df = pd.read_csv(
    'data/alt_fuel_stations (Jan 23 2024).csv', encoding='utf8')

# Create a polyline from the latitude and longitude of the 401 data
polyline_401 = list(zip(df['Latitude'], df['Longitude']))

# Import model and simulation
model = Model(df)
sim = Simulation(df)

# Global variable to track if a budget is set
is_budget_set = False

# Global variable to track the current budget
current_budget = 0

# Map configuration
mapbox_access_token = 'pk.eyJ1IjoienVoYXlyODMiLCJhIjoiY2xrbHc0emVwMHE2NjNsbXZ3cTh2MHNleCJ9.CMVZ7OC27bxxARKMRTttfQ'
ontario_location = {'lat': 44.0, 'lon': -79.0}  # Approximate center of Ontario

# DataFrame to store clicked points
clicked_points_df = pd.DataFrame(
    columns=['Location Description', 'lat', 'lon'])
# List of 'grey' colors, one for each point
marker_colors = ['grey' for _ in range(len(df))]


layout = html.Div(
    style={'height': '100vh', 'width': '100vw',
           'backgroundColor': '#f8f9fa',
           'display': 'flex', 'flexDirection': 'column'},
    children=[
        dcc.Location(id='url', refresh='callback-nav'),
        html.Div(
            [
                dbc.Button("Toggle Existing Stations", id="toggle-stations",
                           n_clicks=0),
                dbc.Input(id="budget-input", type="number",
                          placeholder="Enter Budget", style={'width': '15%'}),
                # dbc.Button("Compute Optimal Solution",
                #            id="compute-optimal", n_clicks=0),
                dcc.Loading(id="loading-button", children=[
                    dbc.Button("Optimize & Simulate", id="compute-sim", n_clicks=0), # , href="/results"
                ]),
                html.Div(id='remaining-budget',
                         style={'fontSize': '16px'}),

                html.Div(
                    dcc.Slider(
                        id='selected-year-slider',
                        min=2024,
                        max=2049,
                        step=5,
                        value=2024,
                        marks={year: str(year)
                               for year in range(2024, 2050, 5)},
                        disabled=False,
                    ),
                    style={'width': '30%', 'marginRight': '20px',
                           'marginLeft': '20px'}
                ),

            ],
            style={
                'height': '12vh',
                'backgroundColor': '#f8f9fa',
                'display': 'flex',
                # 'justifyContent': 'flex-start',
                'alignItems': 'center',
                'gap': '10px',
                'marginRight': '10px',
                'marginLeft': '10px',
            }
        ),
        html.Div(
            style={'flexGrow': 1, 'marginRight':'20px', 'marginLeft':'10px',},
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
                                zoom=6.8,
                                uirevision=False  # Set a fixed uirevision
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
                            {"label": "2 Ports ($35k)", "value": 1},
                            {"label": "4 Ports ($56k)", "value": 2},
                            {"label": "8 Ports ($70k)", "value": 3}
                        ],
                        id="station-level-radio",
                        inline=True
                    )
                ),
                dbc.ModalFooter(
                    dbc.Button("Confirm", id="modal-confirm",
                               n_clicks=0, disabled=True)
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
                    dbc.Button("Confirm Removal",
                               id="modal-remove-confirm", n_clicks=0)
                )
            ],
            id="remove-modal",
            is_open=False,
        ),
        html.Pre(id='clicked-data', style={'whiteSpace': 'pre-wrap'}),
        html.Div(id='placeholder-output',
                 style={'padding': '20px', 'fontSize': '20px'}),
        html.Div(id='placeholder-output-two',
                 style={'padding': '20px', 'fontSize': '20px'}),
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

layout.children.append(remove_modal)


def is_within_radius(station_lat, station_lon, polyline, radius_km=0.5):
    for point in polyline:
        if great_circle((station_lat, station_lon), point).kilometers <= radius_km:
            return True
    return False


# Filter alt fuel stations that are within 5km of the 401 polyline
relevant_stations = alt_fuel_df[alt_fuel_df.apply(lambda x: is_within_radius(
    x['Latitude'], x['Longitude'], polyline_401), axis=1)]


def find_closest_lhrs_for_station(station_lat, station_lon, polyline_401):
    min_distance = float('inf')
    closest_lhrs = None
    for (lhrs_lat, lhrs_lon, lhrs) in polyline_401:
        distance = great_circle(
            (station_lat, station_lon), (lhrs_lat, lhrs_lon)).kilometers
        if distance < min_distance:
            min_distance = distance
            closest_lhrs = lhrs
    return closest_lhrs


# Assuming polyline_401 is a list of tuples: (Latitude, Longitude, LHRS)
# Update the polyline_401 data structure to include LHRS values
polyline_401_with_lhrs = [
    (row['Latitude'], row['Longitude'], row['LHRS']) for index, row in df.iterrows()]

# Create a dictionary to store the closest LHRS value for each relevant station
station_to_lhrs = {}
for index, station in relevant_stations.iterrows():
    closest_lhrs = find_closest_lhrs_for_station(
        station['Latitude'], station['Longitude'], polyline_401_with_lhrs)
    station_to_lhrs[station['Station Name']] = closest_lhrs
    # Print the station name and its closest LHRS to the terminal
    # print(
    #     f"{station['Station Name']} assigned to closest LHRS: {closest_lhrs}")


# Initialize a dictionary to sum EV DC Fast Counts for each LHRS
lhrs_ev_dc_fast_count_sum = {}

# Fill in the EV DC Fast Count for each station, summing by LHRS
for index, station in relevant_stations.iterrows():
    # Access the dictionary using station names
    lhrs = station_to_lhrs[station['Station Name']]
    ev_dc_fast_count = station['EV DC Fast Count'] if pd.notnull(
        station['EV DC Fast Count']) else 0

    # Sum the EV DC Fast Counts for each LHRS
    if lhrs in lhrs_ev_dc_fast_count_sum:
        lhrs_ev_dc_fast_count_sum[lhrs] += ev_dc_fast_count
    else:
        lhrs_ev_dc_fast_count_sum[lhrs] = ev_dc_fast_count


@callback(
    [Output('placeholder-output-two', 'children'),
     Output('coverage', 'data'),
     Output('wait_time', 'data'),
     Output('util', 'data'),
     Output('optimal', 'data'),
     Output('url', 'pathname'),
     Output('compute-sim', 'disabled')],
    [Input('compute-sim', 'n_clicks')],
    [State('budget-store', 'data'),
     State('store-clicked-lhrs', 'data'),
     State('toggle-stations', 'n_clicks'),
     State('year', 'data')]
)
def compute_optimal_solution_and_run_simulation(n_clicks, budget_data, stored_clicked_lhrs, toggle_clicks, selected_year):
    if n_clicks > 0:
        budget = budget_data.get('current_budget') if budget_data else None
        if budget is not None:
            try:
                selected_year = int(selected_year.get('year'))
            except (ValueError, TypeError):
                return "Error: Invalid year format.", ''

            # Compute the optimal solution based on the budget and clicked LHRS
            # This step remains unchanged
            if toggle_clicks % 2 == 1:
                optimal_solution = model.get_optimal(
                    budget, stored_clicked_lhrs,
                    lhrs_ev_dc_fast_count_sum, year=selected_year)
                station_ranges = model.get_ranges()
            else:
                optimal_solution = model.get_optimal(
                    budget, stored_clicked_lhrs, year=selected_year)
                station_ranges = model.get_ranges()
            # Run the simulation with the optimal solution
            sim.simulate(optimal_solution, station_ranges, year=selected_year)

            # Gather results from the simulation
            coverage = sim.get_coverage()
            util = sim.get_util()
            wait_time = sim.get_wait_times()

            # Format the optimal solution and simulation results for display
            solution_summary = "Optimal Solution:\n" + \
                ", ".join(f"LHRS {lhrs}: Level {value}" for lhrs,
                          value in optimal_solution.items())
            simulation_summary = "\n\nSimulation Results:\n" + \
                f"Coverage: {coverage}\nUtilization: {util}\nWait Times: {wait_time}"

            # Combine summaries
            results_summary = solution_summary + simulation_summary
            # print(results_summary)
            # return results_summary, coverage, wait_time, util, optimal_solution
            return dash.no_update, coverage, wait_time, util, optimal_solution, "/results", True
        else:
            return "Please enter a valid budget.", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, False
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, False


# Update this callback to remove dependencies on 'confirm-year' and 'edit-year' buttons
@callback(
    Output('year', 'data'),
    [Input('selected-year-slider', 'value')]
)
def update_year(value):
    # Simply return the slider value, which will be stored in 'stored-year'
    return {'year':int(value)}

@callback(
    Output('modal-confirm', 'disabled'),
    [Input('station-level-radio', 'value'),
     Input('ontario-map', 'clickData')],
    [State('budget-store', 'data'),  # Use budget from the budget-store
     State('cumulative-cost-store', 'data')]  # Existing state for cumulative cost
)
def toggle_modal_confirm_button(level_selected, clickData, budget_data, cumulative_cost_data):
    # Extract budget from budget_data
    budget = budget_data.get('current_budget') if budget_data else None
    is_budget_set = budget is not None and budget > 0

    if level_selected is None or not clickData or not is_budget_set:
        return True

    point_index = clickData['points'][0]['pointIndex']
    cost_column = f'cost {level_selected}'
    station_cost = df.iloc[point_index][cost_column]

    # Get the current cumulative cost from the store
    cumulative_cost = cumulative_cost_data.get(
        'cumulative_cost', 0)  # Default to 0 if key does not exist

    # Check if adding this station exceeds the budget
    if cumulative_cost + station_cost > budget:
        return True

    return False


def toggle_stations_on_map(fig, toggle_clicks, relevant_stations):
    show_stations = toggle_clicks % 2 == 1
    if show_stations:
        add_stations_to_map(fig, relevant_stations)
    else:
        remove_stations_from_map(fig)
    # Update the figure layout to hide the legend
    fig['layout']['showlegend'] = False


def add_stations_to_map(fig, relevant_stations):
    latitudes, longitudes, hover_texts = [], [], []
    for index, row in relevant_stations.iterrows():
        latitudes.append(row['Latitude'])
        longitudes.append(row['Longitude'])
        hover_texts.append(
            f"{row['Station Name']}: {get_station_level(row)}")

    fig['data'].append(go.Scattermapbox(
        lat=latitudes,
        lon=longitudes,
        mode='markers',
        marker={'color': 'blue', 'size': 8},
        text=hover_texts,
        hoverinfo='text'
    ))


def remove_stations_from_map(fig):
    if len(fig['data']) > 1:
        fig['data'].pop()


def get_station_level(row):
    if pd.notna(row['EV DC Fast Count']):
        return 'Level 3'
    elif pd.notna(row['EV Level2 EVSE Num']):
        return 'Level 2'
    elif pd.notna(row['EV Level1 EVSE Num']):
        return 'Level 1'
    return 'Unknown'


@callback(
    Output('budget-store', 'data'),
    [Input('budget-input', 'value')]
)
def update_budget_store(value):
    # Check if the budget input is not None and is a positive number
    if value is not None and value > 0:
        return {'current_budget': value}
    return {}  # Return an empty dictionary if the input is invalid


@callback(
    Output('remaining-budget', 'children'),
    [Input('modal-confirm', 'n_clicks'),
     Input('modal-remove-confirm', 'n_clicks'),
     Input('budget-input', 'value'),  # React to budget input changes directly
     Input('cumulative-cost-store', 'data')],  # Listen to cumulative cost updates
    [State('budget-store', 'data')]
)
def update_remaining_budget(n_clicks_confirm, n_clicks_remove, budget_input, cumulative_cost_data, budget_store_data):
    # If budget_input is not None, update the budget store
    # Default to 0 if key does not exist
    budget = budget_store_data.get('current_budget', 0)

    # Calculate the remaining budget
    # Default to 0 if key does not exist # Assuming cumulative_cost_data is always a dict
    cumulative_cost = cumulative_cost_data.get('cumulative_cost', 0)
    remaining_budget = budget - cumulative_cost

    return f"Remaining Budget: ${remaining_budget}"


@callback(
    [Output('modal', 'is_open'),
     Output('remove-modal', 'is_open')],
    [Input('ontario-map', 'clickData'),
     Input('modal-confirm', 'n_clicks'),
     Input('modal-remove-confirm', 'n_clicks')],
    [State('modal', 'is_open'),
     State('remove-modal', 'is_open'),
     State('store-clicked-lhrs', 'data')]
)
def handle_modal_and_map_clicks(clickData, confirm_clicks, remove_confirm_clicks, is_add_modal_open, is_remove_modal_open, stored_clicked_lhrs):
    ctx = dash.callback_context

    # Check what triggered the callback
    if not ctx.triggered:
        trigger_id = 'No clicks yet'
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Default modal states
    open_add_modal = is_add_modal_open
    open_remove_modal = is_remove_modal_open

    if trigger_id == 'ontario-map' and clickData:
        point_index = clickData['points'][0]['pointIndex']
        lhrs = str(df.iloc[point_index]['LHRS'])

        # Determine if this LHRS has been clicked/selected before
        if stored_clicked_lhrs.get(lhrs, 0) > 0:
            # Already selected; initiate removal
            open_remove_modal = True
            open_add_modal = False  # Ensure add modal is closed
        else:
            # Not yet selected; initiate addition
            open_add_modal = True
            open_remove_modal = False  # Ensure remove modal is closed
    elif 'modal-confirm' in trigger_id or 'modal-remove-confirm' in trigger_id:
        # Close both modals on confirm button click
        open_add_modal = False
        open_remove_modal = False

    return open_add_modal, open_remove_modal


@callback(
    [Output('ontario-map', 'figure'),
     Output('cumulative-cost-store', 'data'),
     Output('store-clicked-lhrs', 'data')],
    [Input('modal-confirm', 'n_clicks'),
     Input('modal-remove-confirm', 'n_clicks'),
     Input('toggle-stations', 'n_clicks'),
     Input('url', 'pathname')],
    [State('station-level-radio', 'value'),
     State('ontario-map', 'clickData'),
     State('ontario-map', 'figure'),
     State('budget-input', 'value'),  # Using 'budget-input' value directly
     State('store-clicked-lhrs', 'data'),
     State('cumulative-cost-store', 'data')]
)
def update_map_and_stored_lhrs_data(confirm_clicks, remove_confirm_clicks, toggle_clicks, pathname, selected_level, clickData, fig, budget, stored_clicked_lhrs, cumulative_cost_data):
    cumulative_cost = cumulative_cost_data.get('cumulative_cost', 0)
    ctx = dash.callback_context
    if not ctx.triggered:
        trigger_id = 'No clicks yet'
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Handling adding or removing stations
    if trigger_id in ['modal-confirm', 'modal-remove-confirm'] and clickData:
        point_index = clickData['points'][0]['pointIndex']
        lhrs = str(df.iloc[point_index]['LHRS'])
        station_cost = df.iloc[point_index][f'cost {selected_level}'] if selected_level else 0
        cumulative_cost = cumulative_cost_data.get('cumulative_cost', 0)

        if 'modal-confirm' in trigger_id and budget - cumulative_cost >= station_cost:
            stored_clicked_lhrs[lhrs] = selected_level
            cumulative_cost += station_cost
        elif 'modal-remove-confirm' in trigger_id and lhrs in stored_clicked_lhrs:
            level_removed = stored_clicked_lhrs[lhrs]
            station_cost_removed = df.iloc[point_index][f'cost {level_removed}']
            cumulative_cost -= station_cost_removed
            # Setting back to 0 instead of removing, to signify station removal
            stored_clicked_lhrs[lhrs] = 0

    # Handling station visibility toggle
    if trigger_id == 'toggle-stations':
        toggle_stations_on_map(fig, toggle_clicks, relevant_stations)

    # Update the map's marker colors based on the stored_clicked_lhrs
    updated_colors = []
    for index, row in df.iterrows():
        lhrs_str = str(row['LHRS'])
        station_level = stored_clicked_lhrs.get(lhrs_str, 0)
        if station_level > 0:
            # Station added, represented by green
            updated_colors.append('green')
        else:
            # No station or removed, represented by grey
            updated_colors.append('grey')

    # Applying the color update to the figure
    fig['data'][0]['marker']['color'] = updated_colors

    # # Reset cost to zero if new navigation
    if trigger_id == 'url':
        cumulative_cost = 0
        for lhrs_id in stored_clicked_lhrs.keys():
            stored_clicked_lhrs[lhrs_id] = 0

    # Ensure to return the updated figure, cumulative cost, and store data
    return fig, {'cumulative_cost': cumulative_cost}, stored_clicked_lhrs
