import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd


# Load CSV and select only required columns
df = pd.read_csv('/Users/zuhayrshaikh/Documents/GitHub/EV-placement/model/401_Data.csv',
                 encoding='ISO-8859-1')[['Location Description', 'Latitude', 'Longitude']]


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
    global clicked_points_df, marker_colors  # Include marker_colors in global

    if clickData:
        point_index = clickData['points'][0]['pointIndex']

        # Update the color list
        marker_colors[point_index] = 'green'

        # Update the figure with the new color list
        fig['data'][0]['marker']['color'] = marker_colors

        # Get the data of the clicked point
        clicked_point = {
            'Location Description': df.iloc[point_index]['Location Description'],
            'lat': clickData['points'][0]['lat'],
            'lon': clickData['points'][0]['lon']
        }

        # Add the clicked point to the DataFrame
        clicked_points_df = clicked_points_df.append(
            clicked_point, ignore_index=True)

    return fig


@app.callback(
    Output('clicked-data', 'children'),
    [Input('ontario-map', 'clickData')]
)
def display_click_data(clickData):
    if clickData:
        # Extract the data for the clicked point
        point_index = clickData['points'][0]['pointIndex']
        location = df.iloc[point_index]['Location Description']
        lat = clickData['points'][0]['lat']
        lon = clickData['points'][0]['lon']

        # Display the clicked location's information
        return f"Clicked Location: {location}, Coordinates: ({lat}, {lon})"


if __name__ == '__main__':
    app.run_server(debug=True)
