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
                    html.Li(html.A('Simulation Flow', href='#simulation-flow')),
                    html.Li(html.A('System Flow Diagram', href='#system-flow')),
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
                            html.P('Our team leveraged public traffic volume and road data from Ontario\'s Ministry of Transportation, along with publicly available US government data on existing charging infrastructure in North America. All data sources were validated by the Ontario Ministry of Transportation. By synthesizing insights from these diverse sources, we were able to define the parameters of our Model and our Simulation.', style={'color': '#4C4C4C'})
                        ]
                    )
                ),
                html.Br(),
                html.Div(
                    style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
                    children=html.Div(
                        style={'background-color': 'white', 'padding': '1rem 2rem', 'border-radius': '10px', 'width': '590px', 'min-height': '150px', 'text-align': 'center', 'margin-right': '20px'},
                        children=[
                            html.H2('Optimization Problem', style={'color': '#19264f'}),
                            html.P('By integrating an original Integer Programming Model, we determine the optimal locations of charging stations. The objective of the model is to maximize the coverage of segments (defined as fraction of demand met in that segment) while adhering to a budget constraint', style={'color': '#4C4C4C'})
                        ]
                    )
                ),
                html.Div(
                    style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
                    children=html.Div(
                        style={'background-color': 'white', 'padding': '1rem 2rem', 'border-radius': '10px', 'width': '590px', 'min-height': '150px', 'text-align': 'center', 'margin-right': '20px'},
                        children=[
                            html.H2('Simulation Problem', style={'color': '#19264f'}),
                            html.P('To simulate traffic throughout the network, we built a simulation around an M/M/C queuing model for each station, with arrivals based on the demand in nearby segments.' 
                                   ' Critical parameters include car interarrival times (based on demand data), charging stall service time, balking probability due to long queues, and the speeds at which cars drive along the highway.')
                        ]
                    )
                ),
                html.Br(),
                html.Br(),
                html.H3('Simulation Flow Chart', id='simulation-flow', style={'font-weight': 'bold'}),
                html.Div('The flow chart below, illustrates the process of any one given vehicle in the simulation. While the simulation is being run, this process occurs thousands of times, across the road network. '),
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
                html.Div('The following diagram illustrates the relationship between the components of our tool, and how you as a user might iteratively interact with them. The FAQ section below could address some of the questions you might have. '),
                html.Div(
                    style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
                    children=html.Img(src='assets/final_system.png', style={'align-items': 'center'}),
                ),
                html.Br(),
                html.Br(),
                html.H3('Frequently Asked Questions', id='faq', style={'font-weight': 'bold'}),
                html.Div([
                    html.H5('1. What is an Integer Programming Model?'),
                    html.P('An integer programming model allows us to define locations of stations as integer decision variables, and define constraints and parameters such that a solver can then find the optimal solution to the defined problem'),
                    html.Div(
                        [
                            html.A("Link to our IP problem", href="https://uofwaterloo.sharepoint.com/:b:/s/tm-arts-23-24mgtecapstone-Team10/EWrFsD7LvMlDmAouvAOTAO0BRn96RlvSks6X56_Q0UrURQ?e=5U9hnl")
                        ]),
                    html.Br(),


                    html.H5('3. What do the numbers of charging ports represent?'),
                    html.P('The program allows both the user and/or the optimization model to select either 2, 4, or 8 charging ports for any given charging station. This refers to the number of physical connectors or outlets available for vehicles to plug into and charge simultaneously at a charging station.'),

                    html.H5('4. Is Voltpath suitable for large-scale deployment planning?'),
                    html.P('Yes, Voltpath is designed to handle large-scale deployment planning for EV charging stations. Its optimization and simulation capabilities make it suitable for strategic planning at the regional or provincial level.'),
                ]),
                html.Br(),
            ]),
            width=8
        ),

    ], style={'backgroundColor': '#f8f9fa', 'padding': '0 25px'}),
], style={'backgroundColor': '#f8f9fa', 'padding': '10px 25px'})