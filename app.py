import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_leaflet as dl

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = 'RiyadhGeoFind'

app.layout = html.Div(style={'position': 'relative', 'height': '100vh', 'overflow': 'hidden'}, children=[
    # Map
    dl.Map(id="map", style={'width': '100%', 'height': '100%'}, center=[24.7136, 46.6753], zoom=12, children=[
        dl.TileLayer(url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', noWrap=True),
        dl.LayerGroup(id="layer")
    ]),

    # Floating search bar
    html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Input(id="search-box", placeholder="Search for a place...", type="text", style={'width': '100%', 'border-radius': '20px', 'border': '1px solid #ccc', 'padding': '10px', 'opacity': '0.5'}),
            ], width=8),
            dbc.Col([
                dbc.Button("Search", id="search-button", n_clicks=0, style={'width': '100%', 'border-radius': '20px', 'background-color': '#4285F4', 'color': 'white', 'border': 'none', 'padding': '10px 20px'}),
            ], width=4)
        ], style={'margin-bottom': '10px'})
    ], style={'position': 'absolute', 'top': '20px', 'left': '50%', 'transform': 'translateX(-50%)', 'z-index': '1000', 'background-color': 'white', 'box-shadow': '0px 4px 10px rgba(0, 0, 0, 0.2)', 'border-radius': '10px', 'padding': '10px', 'width': '90%', 'max-width': '800px'}),

    # Floating LLM output text box
    html.Div([
        dbc.Textarea(id="llm-answer", placeholder="LLM Answer", style={'width': '100%', 'height': '100px', 'border-radius': '10px', 'padding': '10px', 'border': '1px solid #ccc', 'opacity': '0.5'})
    ], style={'position': 'absolute', 'bottom': '20px', 'left': '50%', 'transform': 'translateX(-50%)', 'z-index': '1000', 'background-color': 'white', 'box-shadow': '0px 4px 10px rgba(0, 0, 0, 0.2)', 'border-radius': '10px', 'padding': '10px', 'width': '90%', 'max-width': '800px'}),

    # Card for place details
    dbc.Card(id="place-details", style={'display': 'none', 'position': 'absolute', 'bottom': '160px', 'left': '50%', 'transform': 'translateX(-50%)', 'z-index': '1000', 'background-color': 'white', 'box-shadow': '0px 4px 10px rgba(0, 0, 0, 0.2)', 'border-radius': '10px', 'padding': '10px'}, children=[
        dbc.CardBody([
            html.H4(id="place-name", children="Place Name", style={'margin': '0'}),
            html.P(id="place-description", children="Description", style={'margin': '5px 0'}),
            html.P(id="place-about", children="About", style={'margin': '5px 0'})
        ])
    ])
])

@app.callback(
    [Output("place-name", "children"),
     Output("place-description", "children"),
     Output("place-about", "children"),
     Output("llm-answer", "value"),
     Output("layer", "children"),
     Output("place-details", "style")],
    [Input("search-button", "n_clicks"),
     Input("layer", "click_feature")],
    [State("search-box", "value")]
)
def update_output(n_clicks, click_feature, search_value):
    if n_clicks > 0 and search_value:
        # Dummy data for example purposes
        place_name = f"Name: {search_value}"
        place_description = "Description: This is a description of the place."
        place_about = "About: This is some information about the place."
        llm_answer = "LLM Answer: This is the answer from the language model."
        marker = dl.Marker(position=[24.7136, 46.6753], children=dl.Tooltip(search_value))
        return place_name, place_description, place_about, llm_answer, [marker], {'display': 'none'}
    
    if click_feature:
        properties = click_feature['properties']
        place_name = properties.get('name', 'Place Name')
        place_description = properties.get('description', 'Description')
        place_about = properties.get('about', 'About')
        return place_name, place_description, place_about, "", [], {'display': 'block'}
    
    return "", "", "", "", [], {'display': 'none'}

if __name__ == '__main__':
    app.run_server(debug=True)