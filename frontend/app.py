import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Initialize Dash app
app = dash.Dash(__name__)

# Map configuration
# Get a token from Mapbox
mapbox_access_token = 'pk.eyJ1IjoienVoYXlyODMiLCJhIjoiY2xrbHc0emVwMHE2NjNsbXZ3cTh2MHNleCJ9.CMVZ7OC27bxxARKMRTttfQ'
ontario_location = {'lat': 44.0, 'lon': -79.0}  # Approximate center of Ontario

app.layout = html.Div(
    style={'height': '100vh', 'width': '100vw', 'margin': '0px'},  # This Div takes up the full height and width
    children=[
        dcc.Graph(
            id='ontario-map',
            style={'height': '100%', 'width': '100%'},  # Graph takes up all the space in the Div
            figure={
                'data': [go.Scattermapbox(
                    lat=[ontario_location['lat']],
                    lon=[ontario_location['lon']],
                    mode='markers'
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
        )
    ]
)

@app.callback(
    Output('clicked-points', 'children'),
    [Input('ontario-map', 'clickData')]
)
def display_click_data(clickData):
    if clickData:
        coords = clickData['points'][0]['lat'], clickData['points'][0]['lon']
        return str(coords)

if __name__ == '__main__':
    app.run_server(debug=True)
