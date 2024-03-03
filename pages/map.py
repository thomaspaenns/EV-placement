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


# Initialize `store-clicked-lhrs` with all LHRS values set to 0
initial_clicked_lhrs_dict = {str(lhrs): 0 for lhrs in df['LHRS'].unique()}

# Initialize `store-clicked-lhrs` with all LHRS values set to -1
initial_coverage_dict = {str(lhrs): -1 for lhrs in df['LHRS'].unique()}


initial_util_dict = {str(lhrs): -1 for lhrs in df['LHRS'].unique()}


initial_wait_dict ={str(lhrs): -1 for lhrs in df['LHRS'].unique()} 

# Import model and simulation
model = Model(df)
sim = Simulation(df)

# # Initialize Dash app
# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

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
           'display': 'flex', 'flexDirection': 'column'},
    children=[
        # Adding dcc.Store at the top for better organization
        dcc.Store(id='store-clicked-lhrs', storage_type='memory',
                  data=initial_clicked_lhrs_dict),
        dcc.Store(id='cumulative-cost-store', storage_type='memory',
                  data={'cumulative_cost': 0}),
        dcc.Store(id='budget-store', storage_type='memory',
                  data={'current_budget': 0}),
        dcc.Store(id='coverage', storage_type='memory',
                  data=initial_coverage_dict),
        dcc.Store(id='wait_time', storage_type='memory',
                  data=initial_wait_dict),
        dcc.Store(id='util', storage_type='memory',
                  data=initial_util_dict),
        html.Div(
            [
                dbc.Button("Toggle Stations", id="toggle-stations",
                           n_clicks=0),
                # html.Div([
                dbc.Input(id="budget-input", type="number",
                            placeholder="Enter Budget", style={'width': '15%'}),
                dbc.Button("Compute Optimal Solution",
                            id="compute-optimal", n_clicks=0),
                dbc.Button("Run Simulation", id="compute-sim", n_clicks=0),
                # ], style={'display': 'flex', 'gap': '10px', 'marginTop': '10px','marginBottom': '10px'}),

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
            'gap': '10px'
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
                            {"label": "2 Ports", "value": 1},
                            {"label": "4 Ports", "value": 2},
                            {"label": "8 Ports", "value": 3}
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
        # For storing selected year after confirmation
        html.Div(id='stored-year', style={'display': 'none'})
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
# Store the selected year in a hidden div after confirmation
layout.children.append(
    html.Div(id='stored-year', style={'display': 'none'}))


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

# Print the sums for validation
# print(lhrs_ev_dc_fast_count_sum)
# print(len(lhrs_ev_dc_fast_count_sum))
# for lhrs, total_count in lhrs_ev_dc_fast_count_sum.items():
#     print(f"LHRS {lhrs} has a total EV DC Fast Count of {total_count}")


@callback(
    Output('placeholder-output', 'children'),
    [Input('compute-optimal', 'n_clicks')],
    [State('budget-store', 'data'),  # Use the budget from the budget-store
     State('store-clicked-lhrs', 'data'),
     State('toggle-stations', 'n_clicks'),
     State('stored-year', 'children')]
)
def compute_optimal_solution(n_clicks, budget_data, stored_clicked_lhrs, toggle_clicks, selected_year_str):
    if n_clicks > 0:
        # Extract budget from budget_data
        budget = budget_data.get('current_budget') if budget_data else None

        if budget is not None:
            # Convert the year from string to integer
            try:
                selected_year = int(selected_year_str)
            except (ValueError, TypeError):
                print("Invalid year format:", selected_year_str)
                return "Error: Invalid year format"

            # Use stored_clicked_lhrs instead of clicked_lhrs_dict
            if stored_clicked_lhrs is None:
                stored_clicked_lhrs = {}

            # Check if stations are being shown or not
            if toggle_clicks % 2 == 1:
                # Stations are shown, pass in both dictionaries
                optimal_solution = model.get_optimal(
                    budget, stored_clicked_lhrs, lhrs_ev_dc_fast_count_sum)
            else:
                # Stations are not shown, pass in only stored_clicked_lhrs
                optimal_solution = model.get_optimal(
                    budget, stored_clicked_lhrs)

            # Format the optimal solution for display
            solution_str = ", ".join(
                f"LHRS {key}: Level {value}" for key, value in optimal_solution.items())
            return f"Optimal solution computed: {solution_str}"
        else:
            return "Please enter a valid budget."
    return no_update


@callback(
    [Output('placeholder-output-two', 'children'),
    Output('coverage', 'data'),
    Output('wait_time', 'data'),
    Output('util', 'data')],
    [Input('compute-sim', 'n_clicks')],
    [State('budget-store', 'data'),
     State('store-clicked-lhrs', 'data'),
     State('toggle-stations', 'n_clicks'),
     State('stored-year', 'children')]
)
def compute_optimal_solution_and_run_simulation(n_clicks, budget_data, stored_clicked_lhrs, toggle_clicks, selected_year_str):
    if n_clicks > 0:
        budget = budget_data.get('current_budget') if budget_data else None
        if budget is not None:
            try:
                selected_year = int(selected_year_str)
            except (ValueError, TypeError):
                return "Error: Invalid year format.", ''

            # Compute the optimal solution based on the budget and clicked LHRS
            # This step remains unchanged
            if toggle_clicks % 2 == 1:
                optimal_solution = model.get_optimal(
                    budget, stored_clicked_lhrs, lhrs_ev_dc_fast_count_sum)
                station_ranges = model.get_ranges()
            else:
                optimal_solution = model.get_optimal(
                    budget, stored_clicked_lhrs)
                station_ranges = model.get_ranges()
            # print(optimal_solution, station_ranges)
            # Run the simulation with the optimal solution
            # Run the simulation
            sim.simulate(optimal_solution, station_ranges)

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
            print(results_summary)
            return results_summary, coverage, util, wait_time
        else:
            return "Please enter a valid budget.", dash.no_update, dash.no_update, dash.no_update
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update


# Update this callback to remove dependencies on 'confirm-year' and 'edit-year' buttons
@callback(
    Output('stored-year', 'children'),
    [Input('selected-year-slider', 'value')]
)
def update_year(value):
    # Simply return the slider value, which will be stored in 'stored-year'
    return value

# Assuming your app initialization and other setups are done above


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


# @app.callback(
#     Output('error-message', 'children'),
#     Output('error-message', 'style'),
#     [Input('modal-confirm', 'n_clicks')],
#     [State('station-level-radio', 'value'),
#      State('ontario-map', 'clickData'),
#      State('budget-input', 'value')]
# )
# def display_error_message(n_clicks, selected_level, clickData, budget):
#     if n_clicks and clickData and selected_level:
#         point_index = clickData['points'][0]['pointIndex']
#         cost_column = f'cost {selected_level}'
#         station_cost = df.iloc[point_index][cost_column]
#         if cumulative_cost + station_cost > budget:
#             return "Error: Selection exceeds budget.", {'color': 'red', 'display': 'block'}
#     return "", {'display': 'none'}


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
     Input('toggle-stations', 'n_clicks')],
    [State('station-level-radio', 'value'),
     State('ontario-map', 'clickData'),
     State('ontario-map', 'figure'),
     State('budget-input', 'value'),  # Using 'budget-input' value directly
     State('store-clicked-lhrs', 'data'),
     State('cumulative-cost-store', 'data')]
)
def update_map_and_stored_lhrs_data(confirm_clicks, remove_confirm_clicks, toggle_clicks, selected_level, clickData, fig, budget, stored_clicked_lhrs, cumulative_cost_data):
    cumulative_cost = cumulative_cost_data.get('cumulative_cost', 0)
    ctx = dash.callback_context
    if not ctx.triggered:
        trigger_id = 'No clicks yet'
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # if sim_clicks % 2 == 1:
    #     # Color lines based on coverage
    #     fig = draw_coverage_lines(coverage_dict, fig)

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

    # Ensure to return the updated figure, cumulative cost, and store data
    return fig, {'cumulative_cost': cumulative_cost}, stored_clicked_lhrs


def draw_coverage_lines(coverage_dict, fig):
    # Convert coverage_dict keys to integers for sorting and comparison
    sorted_lhrs = sorted([int(k) for k in coverage_dict.keys()])
    segments_to_color = {"green": [], "yellow": [], "red": [], "gray": []}

    # for i in range(len(sorted_lhrs) - 3):
    #     # Extract four consecutive segments
    #     segment_group = sorted_lhrs[i:i+4]
    #     covered_count = sum(1 for lhrs in segment_group if coverage_dict[str(lhrs)] >= 1.0)
    #     print(covered_count)
    print(coverage_dict)
    i = 0
    while i < len(sorted_lhrs):
        segment_group = sorted_lhrs[i:i+4]
        i = i + 3
        covered_count = 0
        for j in segment_group:
            covered_count += coverage_dict[str(j)]
        # Determine color based on coverage
        if covered_count > 3:
            color = "green"
        elif covered_count > 1 and covered_count <= 3:
            color = "yellow"
        elif covered_count <= 1 and covered_count >= 0:
            color = "red"
        else:
            color = "gray"

        # Add coordinates for these segments to the corresponding color group
        for lhrs in segment_group:
            lat, lon = df[df['LHRS'] == int(
                lhrs)][['Latitude', 'Longitude']].values[0]
            segments_to_color[color].append((lat, lon))

    # Draw lines for each color group
    for color, coordinates in segments_to_color.items():
        if coordinates:
            latitudes, longitudes = zip(*coordinates)
            fig['data'].append(go.Scattermapbox(
                lat=latitudes,
                lon=longitudes,
                mode='lines',
                line=dict(width=4, color=color),
                hoverinfo='none'
            ))

    return fig


# @callback(
#     [Output('clicked-data', 'children')],
#     [Input('store-clicked-lhrs', 'data')]  # Listening to updates in the store
# )
# def display_click_data(stored_clicked_lhrs):
#     # This function now purely displays data based on the store's state
#     changed_lhrs_statuses = "\n".join(
#         f"LHRS: {lhrs}, Status: {status}" for lhrs, status in stored_clicked_lhrs.items())
#     # print(f"Changed LHRS Status:\n{changed_lhrs_statuses}")
#     return [f"Changed LHRS Status:\n{changed_lhrs_statuses}"]


if __name__ == '__main__':
    app.run_server(debug=True)
