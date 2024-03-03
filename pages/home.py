import dash
from dash import html

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H3('Welcome to Voltpath: a tool enabling optimal location of EV charging stations',style={"font-weight": "bold"}),
    html.Div('We employ a dual-model strategy combining integer programming and discrete event simulation, encapsulated within a user-friendly interface accessible to non-technical stakeholders. This innovative tool facilitates the strategic planning of EV charging station locations, balancing cost, coverage, and utilization to recommend the most effective locations for EV chargers. Our tool leverages traffic data pulled from the Government of Ontario Linear Highway Referencing System to accurately estimate demand.'),
], style={'marginTop': '30px', 'marginLeft': '30px', 'marginRight': '30px'})