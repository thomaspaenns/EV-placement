import dash
from dash import html
import dash_bootstrap_components as dbc


dash.register_page(__name__, path='/')

layout = html.Div([
    html.Div([
        html.Br(),
        html.H3('Welcome to Voltpath: a tool enabling optimal location of EV charging stations',style={"font-weight": "bold"}),
        html.Div('We employ a dual-model strategy combining integer programming and discrete event simulation, encapsulated within a user-friendly interface accessible to non-technical stakeholders. This innovative tool facilitates the strategic planning of EV charging station locations, balancing cost, coverage, and utilization to recommend the most effective locations for EV chargers. Our tool leverages traffic data pulled from the Government of Ontario Linear Highway Referencing System to accurately estimate demand.'),
        html.Br(),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.Img(src='assets/constraint.png', style={'width': '40%', 'height': 'auto'}),
                html.H5("Select Your Constraints", 
                         style={'font-weight': 'bold', 'marginTop': '15px'}),
                # <a href="https://www.flaticon.com/free-icons/constraint" title="constraint icons">Constraint icons created by noomtah - Flaticon</a>
                html.Div("Use the map page to set your budget and select any must-have stations along with the number of associated ports. Decide whether to take into account existing stations. Select the year for which you want to optimize/simulate."),
            ], style={'text-align': 'center'}),
            dbc.Col([
                html.Img(src='assets/two-cars-in-line.png', style={'width': '40%', 'height': 'auto'}),
                html.H5("Optimize and Simulate", 
                         style={'font-weight': 'bold', 'marginTop': '15px'}),
                # <a href="https://www.flaticon.com/free-icons/traffic" title="traffic icons">Traffic icons created by Freepik - Flaticon</a>
                html.Div("Run the optimization model and discrete event simulation to select remaining optimal locations and then simulate the effects on the road network. Interpret the outputs in the results page and download the results as a CSV file."),
            ], style={'text-align': 'center'}),
            dbc.Col([
                html.Img(src='assets/iterative.png', style={'width': '40%', 'height': 'auto'}),
                # <a href="https://www.flaticon.com/free-icons/iterative" title="iterative icons">Iterative icons created by JunGSa - Flaticon</a>
                html.H5("Iterate!", 
                         style={'font-weight': 'bold', 'marginTop': '15px'}),
                html.Div("Based on the outputs of the model and simulation, adjust your constraints/locations and try out new scenarios. Continue iterating until you have a solution that suits your specific requirements and priorities."),
            ], style={'text-align': 'center'}),
        ]),
        html.Br(),
        html.Br(),
        html.Div([
            dbc.Button('Get Started', href='/map', 
                       style={'font-size':'30', 'width':'40%', 'height':'auto'}),
            html.Br(),
            html.Br(),
            html.H4('System Flow Diagram', style={'font-weight': 'bold'}),
            html.Img(src='assets/final_system.png')
        ], style={'text-align': 'center'}),
    ], style={'backgroundColor': '#f8f9fa',
              'marginLeft': '20px', 'marginRight': '20px'})
], style={'backgroundColor': '#f8f9fa',})