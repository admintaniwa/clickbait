# import necessary modules 
import dash
from dash import dcc
from dash import html
import pandas as pd
from dash.dependencies import Output, Input

# Set up the App 
app = dash.Dash(__name__)

# Define CSS for dark theme
css_path = '/assets/styles/main.css'
external_css = [
    {'href': 'https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap'},
    {'href': css_path}
]

# Define the layout 
app.layout = html.Div([
    html.Link(href='https://codepen.io/shshaw/pen/MJRZNO?theme-id=dark', rel="stylesheet", type="text/css"),
    html.H1("Dash App with Dark Theme"),
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Option 1', 'value': '1'},
            {'label': 'Option 2', 'value': '2'}
        ],
        value='1'
    ),
    dcc.Graph(
        id='my-graph',
        figure={}
    )
])

# Define a callback for the dropdown
@app.callback(
    Output('my-graph', 'figure'),
    Input('my-dropdown', 'value'))
def update_graph(selected_value):
    # Create random data
    df = pd.DataFrame({
        'x': [1, 2, 3],
        'y': [4, 5, 6],
        'label': ['A', 'B', 'C']
    })

    # Update the graph with new data
    figure = {
        'data': [
            {'x': df['x'].tolist(), 'y': df['y'].tolist(), 'mode': 'markers', 'type': 'scatter', 'name': 'Scatter Plot'}
        ],
        'layout': {
            'showlegend': False,
            'xaxis': {'title': 'X Axis'},
            'yaxis': {'title': 'Y Axis'},
            'title': {
                'text': "Dash App with Dark Theme"
            }
        }
    }

    return figure

# Running the server
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
