import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/about')

layout = html.Div([
    dbc.Row([
        dbc.Col(
            html.Div([
                html.Br(),
                html.H2('Guide', style={'font-weight': 'bold'}),
                html.Ul([
                    html.Li(html.A('Purpose of Voltpath', href='#purpose')),
                    html.Li(html.A('Solution Development', href='#solution')),
                    html.Li(html.A('System Flow Diagram', href='#system-flow')),
                    html.Li(html.A('Simulation Flow', href='#simulation-flow')),
                    html.Li(html.A('FAQ', href='#faq')),
                ]),
                html.Br(),
            ]),
            width=2
        ),
        dbc.Col(
            html.Div(style={'border-left': '1px solid #ccc', 'height': '100%'}),
            width=1
        ),
        dbc.Col(
            # Main Content
            html.Div([
                html.Br(),
                html.H2('Purpose of Voltpath', id='purpose', style={'font-weight': 'bold'}),
                html.Div('Despite significant advancements, Ontario faces a critical challenge in scaling its EV charging infrastructure to match the rapid growth in EV adoption. The Ministry of Transportation emphasizes the need for Ontario-specific strategies to enhance the network of public chargers, supporting not just urban areas but also ensuring inclusivity for municipalities, Indigenous communities, and businesses. Our project seeks to bridge this gap, offering a data-driven approach to optimize charging station placement.'),
                html.Br(),
                html.H3('Solution Development', style={"font-weight": "bold"}),
                html.H5('The goal is to build “An EVCS site selection tool to support MTO staff in identifying, evaluating and prioritizing appropriate locations for public EVCS, both on government lands and at third-party sites.” (HIIFP, 2023). In essence, since this problem combines many types of issues; it is at once a:', style={'color': '#141e3d', 'font-style': 'italic'}),
                html.Br(),
                html.Div(
                    style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
                    children=html.Div(
                        style={'background-color': 'white', 'padding': '1rem 2rem', 'border-radius': '10px', 'width': '590px', 'min-height': '150px', 'text-align': 'center', 'margin-right': '20px'},
                        children=[
                            html.H2('Data Engineering Problem', style={'color': '#19264f'}),
                            html.P('Our data collection process involved gathering traffic volume data from Ontario\'s Ministry of Transportation, analyzing charging station utilization across the province, and referencing successful charging network projects in the United States, such as the West Coast Pacific Highway initiative. By synthesizing insights from these diverse sources, we gained valuable information to inform our strategic planning efforts for optimizing EV charging infrastructure in Ontario.', style={'color': '#4C4C4C'})
                        ]
                    )
                ),
                html.Br(),
                html.Div(
                    style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
                    children=html.Div(
                        style={'background-color': 'white', 'padding': '1rem 2rem', 'border-radius': '10px', 'width': '590px', 'min-height': '150px', 'text-align': 'center', 'margin-right': '20px'},
                        children=[
                            html.H2('Linear Programming Problem (IP)', style={'color': '#19264f'}),
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
                            html.H2('M/M/C Queueing Problem', style={'color': '#19264f'}),
                            html.P('To simulate the arrival and departure of cars at our charging stations, we incorporated the M/M/C queuing model into our simulation framework.' 
                                   ' Critical parameters include car interarrival times (based on demand data), charging stall service time, balking probability due to long queues, and maximum queue size before additional balking.'
                                   ' SimPy execution in Python allowed us to estimate these parameters to formulate our model', style={'color': '#4C4C4C'})
                        ]
                    )
                ),
                html.H3('Event Simulation', id='simulation-flow', style={'font-weight': 'bold'}),
                html.Div('The simulation primarily tracks the series of events that will occur throughout the process of charging a vehicle. Critical parameters such as driving speed, balking probability due to long queues, and '
                         'duration of charging stall service time were assumed based on historical data. Future steps involve large-scale SimPy execution in Python'),
                html.Br(),
                html.Div(
                    style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
                    children=html.Img(
                        src='assets/simulation-flow_chart.png',
                        style={'max-height': '250px', 'align-items': 'center'}
                    )
                ),
                html.Br(),
                html.H3('System Flow Diagram', id='system-flow', style={'font-weight': 'bold'}),
                html.Div('The following diagram illustrates the relationship between the tools, and the FAQ section below could address some of the questions you might have. For each model, certain features will be necessary. For all features, if future projections cannot be obtained then they will have to be forecasted.'),
                html.Div(
                    style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
                    children=html.Img(src='assets/final_system.png', style={'align-items': 'center'}),
                ),
                html.Br(),
                html.Br(),
                html.H3('Frequently Asked Questions', id='faq', style={'font-weight': 'bold'}),
                html.Div([
                    html.H5('1. What is Integer Programming (IP)?'),
                    html.P('IP is a mathematical optimization technique where decision variables are restricted to be integers. Link to our IP problem can be found here:'),
                    html.Div(
                        [
                            html.A("Link to our IP problem", href="https://uofwaterloo.sharepoint.com/:b:/s/tm-arts-23-24mgtecapstone-Team10/EWrFsD7LvMlDmAouvAOTAO0BRn96RlvSks6X56_Q0UrURQ?e=5U9hnl")
                        ]),
                    html.Br(),

                    html.H5('2. What is M/M/C model in queuing theory?'),
                    html.P('An M/M/c model represents a queueing system that has exponential arrivals, c servers with exponential service time'),

                    html.H5('3. What do the charging ports mean?'),
                    html.P('The 2, 4, 8 charging ports in the simulation refers to the number of physical connectors or outlets available for vehicles to plug into and charge simultaneously at a charging station.'),

                    html.H5('4. Is Voltpath suitable for large-scale deployment planning?'),
                    html.P('Yes, Voltpath is designed to handle large-scale deployment planning for EV charging stations. Its optimization and simulation capabilities make it suitable for strategic planning at the regional or city level.'),
                ]),
                html.Br(),
            ]),
            width=8
        ),

    ], style={'backgroundColor': '#f8f9fa', 'padding': '0 25px'}),
], style={'backgroundColor': '#f8f9fa', 'padding': '10px 25px'})