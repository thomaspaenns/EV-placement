import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/about')

layout = html.Div([
    html.Div([
        html.Br(),
        html.H3('Purpose of Voltpath', style={"font-weight": "bold"}),
        html.Div('Despite significant advancements, Ontario faces a critical challenge in scaling its EV charging infrastructure to match the rapid growth in EV adoption. The Ministry of Transportation emphasizes the need for Ontario-specific strategies to enhance the network of public chargers, supporting not just urban areas but also ensuring inclusivity for municipalities, Indigenous communities, and businesses. Our project seeks to bridge this gap, offering a data-driven approach to optimize charging station placement.'),
        html.Br(),
        html.H3('Solution Development', style={"font-weight": "bold"}),
        html.Div(
            style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
            children=html.Div(
                style={'background-color': 'white', 'padding': '1rem 2rem', 'border-radius': '10px', 'width': '590px', 'min-height': '150px', 'text-align': 'center', 'margin-right': '20px'},
                children=[
                    html.H2('M/M/C Queueing Model', style={'color': '#4C4C4C'}),
                        html.P('To simulate the arrival and departure of cars at our charging stations, we incorporated the M/M/C queuing model into our simulation framework.' 
                               'Critical parameters include car interarrival times (based on demand data), charging stall service time, balking probability due to long queues, and maximum queue size before additional balking.'
                               'SimPy execution in Python allowed us to estimate these parameters to formulate our model', style={'color': '#4C4C4C'})
                  ]
            )
        ),
        html.Br(),
        html.Div(
            style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
            children=html.Div(
                style={'background-color': 'white', 'padding': '1rem 2rem', 'border-radius': '10px', 'width': '590px', 'min-height': '150px', 'text-align': 'center', 'margin-right': '20px'},
                children=[
                    html.H2('Modeling of the Problem', style={'color': '#4C4C4C'}),
                        html.P('By integrating an original Integer programming model, we can mathematically identify the coverage of our charging stations. We utilized this model to define a neighborhood around each potential charging station location, considering areas within a certain distance along the shortest path as covered. Our objective was to minimize costs while achieving a predefined coverage level.', style={'color': '#4C4C4C'})
                    ]
            )
        ),
        html.Br(),
        html.Div(
            style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
            children=html.Div(
                style={'background-color': 'white', 'padding': '1rem 2rem', 'border-radius': '10px', 'width': '590px', 'min-height': '150px', 'text-align': 'center', 'margin-right': '20px'},
                children=[
                    html.H2('Data Collection', style={'color': '#4C4C4C'}),
                        html.P('Our data collection process involved gathering traffic volume data from Ontario\'s Ministry of Transportation, analyzing charging station utilization across the province, and referencing successful charging network projects in the United States, such as the West Coast Pacific Highway initiative. By synthesizing insights from these diverse sources, we gained valuable information to inform our strategic planning efforts for optimizing EV charging infrastructure in Ontario.', style={'color': '#4C4C4C'})
                  ]
            )
        ),
        
        html.H4('System Flow Diagram', style={'font-weight': 'bold', 'display': 'flex'}),
        html.Div('Text about system flow of events'),
        html.Div(
            style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
            children=html.Img(src='assets/final_system.png', style={'align-items': 'center'}),
        ),
        html.Br(),
        html.Br(),

    ], style={'backgroundColor': '#f8f9fa',
              'marginLeft': '20px', 'marginRight': '20px'}),
    
    # FAQ Section
    html.Div([
        html.Br(),
        html.H3('Frequently Asked Questions', style={"font-weight": "bold"}),
        html.Div([
            html.H5('1. What is Integer Programming (IP)?'),
            html.P('IP is a mathematical optimization technique where decision variables are restricted to be integers. Link to our IP problem can be found here:'),
            html.Div(
            [
                html.A("Link to our IP problem", href="https://uofwaterloo.sharepoint.com/:b:/s/tm-arts-23-24mgtecapstone-Team10/EWrFsD7LvMlDmAouvAOTAO0BRn96RlvSks6X56_Q0UrURQ?e=5U9hnl")
            ]),
            html.H5('2. What is MMC model in queuing theory?'),
            html.P('Yes, Voltpath allows users to customize various constraints such as budget, must-have stations, and existing station consideration. Users can also adjust optimization parameters to tailor the results to their specific needs.'),
            
            html.H5('3. How often is the traffic data updated in Voltpath?'),
            html.P('The traffic data used in Voltpath is updated periodically, typically in accordance with updates to the Government of Ontario Linear Highway Referencing System. Users can expect reasonably up-to-date data for their simulations.'),
            
            html.H5('4. Is Voltpath suitable for large-scale deployment planning?'),
            html.P('Yes, Voltpath is designed to handle large-scale deployment planning for EV charging stations. Its optimization and simulation capabilities make it suitable for strategic planning at the regional or city level.'),
        ]),
    ], style={'backgroundColor': '#f8f9fa',
              'marginLeft': '20px', 'marginRight': '120px'})
], style={'backgroundColor': '#f8f9fa', 'padding': '0 25px',})

