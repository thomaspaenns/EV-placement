import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

app = Dash(__name__, use_pages=True,external_stylesheets=[dbc.themes.BOOTSTRAP])
image_path = 'assets/voltpath.png'


# Load CSV and select only required columns
df = pd.read_csv('data/401_Data.csv', encoding='ISO-8859-1')

# Initialize `store-clicked-lhrs` with all LHRS values set to 0
initial_clicked_lhrs_dict = {str(lhrs): 0 for lhrs in df['LHRS'].unique()}

# Initialize `store-clicked-lhrs` with all LHRS values set to -1
initial_coverage_dict = {str(lhrs): -1 for lhrs in df['LHRS'].unique()}


initial_util_dict = {str(lhrs): -1 for lhrs in df['LHRS'].unique()}


initial_wait_dict ={str(lhrs): -1 for lhrs in df['LHRS'].unique()} 


app.layout = html.Div([
    # Define your dcc.Store components here
    dcc.Store(id='store-clicked-lhrs', storage_type='memory', data=initial_clicked_lhrs_dict),
    dcc.Store(id='cumulative-cost-store', storage_type='memory', data={'cumulative_cost': 0}),
    dcc.Store(id='budget-store', storage_type='memory', data={'current_budget': 0}),
    dcc.Store(id='coverage', storage_type='memory', data=initial_coverage_dict),
    dcc.Store(id='wait_time', storage_type='memory', data=initial_wait_dict),
    dcc.Store(id='util', storage_type='memory', data=initial_util_dict),
    dcc.Store(id='year',storage_type='memory', data={'year':2024}),
    
    # Navbar
    html.Img(src=image_path, style={'display': 'inline-block', 'verticalAlign': 'top'}),
    html.Div([
        html.Div(
            dbc.Button(f"{page['name']}", href=page["relative_path"], color="secondary"),
            style={'display': 'inline-block', 'marginRight': '20px', 'marginTop': '10px', 'marginBottom': 'auto'}
        ) for page in dash.page_registry.values()
    ], style={'display': 'inline-block', 'marginRight': '10px'}),
    
    # Page container
    dash.page_container,

    #Footer
    html.Div([
        html.A('Contact Us', href='mailto:tenns@uwaterloo.ca?cc=z22shaikh@uwaterloo.ca&subject=Voltpath%20Contact'),
    ], style={'marginLeft': '20px',
              'marginRight': '20px',
              'marginTop': '10px',
              'marginBottom': '10px',
              'text-align': 'center'}),
])

if __name__ == '__main__':
    app.run(debug=True)