from model.model import Model
from simulation.simulation import Simulation

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd


# Load CSV and select only required columns
df = pd.read_csv('401_Data.csv', encoding='ISO-8859-1')

# Initialize a dictionary to track clicked LHRS
clicked_lhrs_dict = {lhrs: 0 for lhrs in df['LHRS']}

# Import model and simulation
# model = Model(df)
# sim = Simulation()

# Initialize Dash app
app = dash.Dash(__name__)

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
        html.Pre(id='clicked-data')
    ]
)


@app.callback(
    Output('ontario-map', 'figure'),
    Input('ontario-map', 'clickData'),
    State('ontario-map', 'figure')
)
def update_map(clickData, fig):
    global clicked_points_df, marker_colors, clicked_lhrs_dict

    if clickData:
        point_index = clickData['points'][0]['pointIndex']

        # Toggle the color and update the clicked_lhrs_dict
        if marker_colors[point_index] == 'grey':
            marker_colors[point_index] = 'green'
            clicked_lhrs_dict[df.iloc[point_index]['LHRS']] = 1
        else:
            marker_colors[point_index] = 'grey'
            clicked_lhrs_dict[df.iloc[point_index]['LHRS']] = 0
        
        # Print the updated clicked_lhrs_dict for debugging
        print(f"Updated clicked_lhrs_dict: {clicked_lhrs_dict}")

        # Update the marker colors in the figure
        fig['data'][0]['marker']['color'] = marker_colors

        # Get the data of the clicked point
        clicked_point = {
            'Location Description': df.iloc[point_index]['Location Description'],
            'lat': clickData['points'][0]['lat'],
            'lon': clickData['points'][0]['lon']
        }

        # Check if this point is already in clicked_points_df
        if clicked_points_df[(clicked_points_df.lat == clicked_point['lat']) & 
                             (clicked_points_df.lon == clicked_point['lon'])].empty:
            # Add the clicked point to the DataFrame if not already present
            clicked_points_df = pd.concat(
                [clicked_points_df, pd.DataFrame([clicked_point])], ignore_index=True)
        else:
            # Remove the clicked point from the DataFrame if it is already present
            clicked_points_df = clicked_points_df.drop(
                clicked_points_df[(clicked_points_df.lat == clicked_point['lat']) & 
                                  (clicked_points_df.lon == clicked_point['lon'])].index
            )
        

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
