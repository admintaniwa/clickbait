from dash import Dash, html, dcc, Input, Output, dash_table, callback
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go

import collections
import pandas as pd


app = Dash(__name__)

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')


app.layout = html.Div([
    dcc.Store(id='memory-output'),
    dcc.Dropdown(df.country.unique(),
                 ['Canada', 'United States'],
                 id='memory-countries',
                 multi=True),
    dcc.Dropdown({'lifeExp': 'Life expectancy', 'gdpPercap': 'GDP per capita'},
                 'lifeExp',
                 id='memory-field'),
    html.Div(className="twelve columns",children=[
        html.Div(className="section-banner", children="Evolución de noticias clickbait"),
        dcc.Graph(id='memory-graph',
                figure=go.Figure(
                    {
                        "layout": {
                            "paper_bgcolor": "rgba(100,100,100,0)",
                            "plot_bgcolor": "rgba(0,0,0,0)",
                            "xaxis": dict(
                                showline=False, showgrid=False, zeroline=False
                            ),
                            "yaxis": dict(
                                showgrid=False, showline=False, zeroline=False
                            ),
                            "autosize": True,
                            "margin": dict(l=20, r=20, t=20, b=20),
                            "showlegend": True,
                            "font": {"color": "white"},
                            "legend": {"font": {"color": "white"}, "orientation": "h"},
                        },
                    }
                ),

        ),
        dash_table.DataTable(
            id='memory-table',
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_header={"fontWeight": "bold", "color": "inherit"},
            style_as_list_view=True,
            fill_width=True,
            style_cell_conditional=[
                {"if": {"column_id": "score"}, "textAlign": "left"}
            ],
            style_cell={
                "backgroundColor": "#1e2130",
                "fontFamily": "Open Sans",
                "padding": "0 2rem",
                "color": "darkgray",
                "border": "none",
            },
            css=[
                {"selector": "tr:hover td", "rule": "color: #91dfd2 !important;"},
                {"selector": "td", "rule": "border: none !important;"},
                {
                    "selector": ".dash-cell.focused",
                    "rule": "background-color: #1e2130 !important;",
                },
                {"selector": "table", "rule": "--accent: #1e2130;"},
                {"selector": "tr", "rule": "background-color: transparent"},
            ],
        ),
    ])
])


@callback(Output('memory-output', 'data'),
              Input('memory-countries', 'value'))
def filter_countries(countries_selected):
    if not countries_selected:
        # Return all the rows on initial load/no country selected.
        return df.to_dict('records')

    filtered = df.query('country in @countries_selected')

    return filtered.to_dict('records')


@callback(Output('memory-table', 'data'),
              Input('memory-output', 'data'))
def on_data_set_table(data):
    if data is None:
        raise PreventUpdate

    return data


@callback(Output('memory-graph', 'figure'),
              Input('memory-output', 'data'),
              Input('memory-field', 'value'))
def on_data_set_graph(data, field):
    if data is None:
        raise PreventUpdate

    aggregation = collections.defaultdict(
        lambda: collections.defaultdict(list)
    )

    for row in data:

        a = aggregation[row['country']]

        a['name'] = row['country']
        a['mode'] = 'lines+markers'

        a['y'].append(row[field])
        a['x'].append(row['year'])

    return go.Figure( 
        {
        'data': [x for x in aggregation.values()],
        "layout": {
                            "paper_bgcolor": "rgba(200,200,200,2)",
                            "plot_bgcolor": "rgba(0,0,0,3)",
                            "xaxis": dict(
                                showline=False, showgrid=False, zeroline=False
                            ),
                            "yaxis": dict(
                                showgrid=False, showline=False, zeroline=False
                            ),
                            "autosize": True,
                        },
        })


if __name__ == '__main__':
    app.run( threaded=True, port=10450)
