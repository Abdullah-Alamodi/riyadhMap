from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_leaflet as dl

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])

app.title = 'RiyadhGeoFind'

app.layout = html.Div(style={'position': 'relative', 'height': '100vh', 'overflow': 'hidden'}, children=[
    # Map
    dl.Map(id="map", style={'width': '100%', 'height': '100%'}, center=[24.7136, 46.6753], zoom=12, children=[
        dl.TileLayer(url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', noWrap=True),
        dl.LayerGroup(id="layer")
    ]),
    # Floating search bar
    html.Div([
        dbc.CardBody([
            dbc.Input(id="search-box", placeholder="Search for a place...", type="text", style={'width': '100%', 'border-radius': '20px', 'border': '1px solid #ccc', 'padding': '10px'}),
            dbc.Button(
                html.I(className="fa fa-search", style={'color': '#002030'}),
                id="search-icon", n_clicks=0,
                style={'position': 'absolute', 'right': '30px', 'top': '50%', 'transform': 'translateY(-50%)', 'background': 'none', 'border': 'none', 'padding': '0'}
            )
        ])
    ], style={'position': 'absolute', 'top': '20px', 'left': '50%', 'transform': 'translateX(-50%)', 'background': 'white', 'z-index': '1000', 'border-radius': '20px', 'width': '90%', 'max-width': '800px'}),

    # Hidden store to capture Enter key press
    dcc.Store(id='enter-press', data=False),

    # Floating LLM output text box
    html.Div([
        dbc.Textarea(id="llm-answer", placeholder="LLM Answer", style={'width': '100%', 'height': '100px', 'border-radius': '10px', 'padding': '10px', 'border': '1px solid #ccc', 'opacity': '0.5'})
    ], style={'position': 'absolute', 'bottom': '20px', 'left': '50%', 'transform': 'translateX(-50%)', 'z-index': '1000', 'background-color': 'white', 'box-shadow': '0px 4px 10px rgba(0, 0, 0, 0.2)', 'border-radius': '20px', 'padding': '10px', 'width': '90%', 'max-width': '800px'}),

    # Card for place details
    dbc.Card(id="place-details", style={'display': 'none', 'position': 'absolute', 'bottom': '160px', 'left': '50%', 'transform': 'translateX(-50%)', 'z-index': '1000', 'background-color': 'white', 'box-shadow': '0px 4px 10px rgba(0, 0, 0, 0.2)', 'border-radius': '20px'}, children=[
        dbc.CardBody([
            html.H4(id="place-name", children="Place Name", style={'margin': '0'}),
            html.P(id="place-description", children="Description", style={'margin': '5px 0'}),
            html.P(id="place-about", children="About", style={'margin': '5px 0'})
        ])
    ])
])

@app.callback(
    Output('enter-press', 'data'),
    [Input('search-box', 'n_submit')]
)
def update_enter_press(n_submit):
    return True

@app.callback(
    [Output("place-name", "children"),
     Output("place-description", "children"),
     Output("place-about", "children"),
     Output("llm-answer", "value"),
     Output("layer", "children"),
     Output("place-details", "style")],
     Output("map", "center"),
    [Input("search-icon", "n_clicks"),
     Input("enter-press", "data"),
     Input("layer", "click_feature")],
    [State("search-box", "value")]
)
def update_output(n_clicks, enter_press, click_feature, search_value):
    import dash
    ctx = dash.callback_context

    if not ctx.triggered:
        return "", "", "", "", [], {'display': 'none'}
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id in ["search-icon", "enter-press"] and search_value:
        # Dummy data for example purposes
        place_name = f"Name: {search_value}"
        places = [[24.92240594541537, 46.697644545161054], [24.830648890314453, 46.88040359101927], [24.7136, 46.6753], [24.728996675511027, 46.5803294259357], [24.728720030785063, 46.62307417597616]]
        import random
        random_place = random.choice(places)
        place_description = "Description: This is a description of the place."
        place_about = "About: This is some information about the place."
        llm_answer = "LLM Answer: This is the answer from the language model."
        marker = dl.Marker(position=random_place, children=[
            dl.Tooltip(search_value),
            dl.Popup([
                html.H4(place_name),
                html.P(place_description),
                html.P(place_about)
            ])
        ])
        return place_name, place_description, place_about, llm_answer, [marker], {'display': 'block'}, random_place
    
    if triggered_id == "layer" and click_feature:
        properties = click_feature['properties']
        place_name = properties.get('name', 'Place Name')
        place_description = properties.get('description', 'Description')
        place_about = properties.get('about', 'About')
        marker = dl.Marker(position=click_feature['geometry']['coordinates'][::-1], children=[
            dl.Tooltip(place_name),
            dl.Popup([
                html.H4(place_name),
                html.P(place_description),
                html.P(place_about)
            ])
        ])
        return place_name, place_description, place_about, "", [marker], {'display': 'block'}, click_feature['geometry']['coordinates'][::-1]
    
    return "", "", "", "", [], {'display': 'none'}, [24.7136, 46.6753]

if __name__ == '__main__':
    app.run_server(debug=True)