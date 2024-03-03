import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

app = Dash(__name__, use_pages=True,external_stylesheets=[dbc.themes.BOOTSTRAP])
image_path = 'assets/voltpath.png'

app.layout = html.Div([
    # html.H1('Multi-page app with Dash Pages'),
    html.Img(src=image_path, style={'display': 'inline-block', 'verticalAlign': 'top'}),
    html.Div([
        html.Div(
            dbc.Button(f"{page['name']}", href=page["relative_path"], color="secondary"),
            style={'display': 'inline-block', 'marginRight': '20px', 'marginTop': '10px', 'marginBottom': 'auto'}
            # dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"]),
            # style = {'display': 'inline-block', 'marginRight': '10px'}
        ) for page in dash.page_registry.values()
    ], style = {'display': 'inline-block', 'marginRight': '10px'}),
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=True)