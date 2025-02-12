import os
import dash
from dash import dash_table, Input, Output, State, html, dcc, callback
import plotly.graph_objs as go
import dash_daq as daq
import pandas as pd

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TextClassificationPipeline,
)

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Clickbait o seguimiento de noticias cebo"
server = app.server
app.config["suppress_callback_exceptions"] = True

AGG_FILE_PATH=os.getenv("AGG_FILE_PATH")
LAST30_FILE_PATH=os.getenv("LAST30_FILE_PATH")
df = pd.read_csv(LAST30_FILE_PATH)
fuentes=df.fuente.unique()
df_agg=pd.read_csv(AGG_FILE_PATH)
tokenizerDOS = AutoTokenizer.from_pretrained("model/clickbait_es") #"taniwasl/clickbait_es")
modelDOS = AutoModelForSequenceClassification.from_pretrained("model/clickbait_es") #("taniwasl/clickbait_es")
nlp = TextClassificationPipeline(task = "text-classification",
                model = modelDOS,
                tokenizer = tokenizerDOS,
                max_length = 25,
                truncation=True,
                add_special_tokens=True
                )

# params = list(df)
max_length = len(df)

suffix_row = "_row"
suffix_button_id = "_button"
suffix_sparkline_graph = "_sparkline_graph"
suffix_count = "_count"
suffix_ooc_n = "_OOC_number"
suffix_ooc_g = "_OOC_graph"
suffix_indicator = "_indicator"


def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("DETECTOR DE CLICKBAITS"),
                    html.H6("Seguimiento de noticias cebo en los principales medios de comunicación españoles"),
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.Button(
                        id="learn-more-button", children="QUIERO SABER MÁS", n_clicks=0
                    ),
                    html.A(
                        html.Img(id="logo", src=app.get_asset_url("logo_taniwa_250.png")),
                        href="https://taniwa.es",
                    ),
                ],
            ),
        ],
    )


def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab2",
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="Specs-tab",
                        label="Titulares",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Control-chart-tab",
                        label="Gráficos de Evolución",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                ],
            )
        ],
    )


# def init_df():
#     ret = {}
#     for col in list(df[1:]):
#         data = df[col]
#         stats = data.describe()

#         std = stats["std"].tolist()
#         ucl = (stats["mean"] + 3 * stats["std"]).tolist()
#         lcl = (stats["mean"] - 3 * stats["std"]).tolist()
#         usl = (stats["mean"] + stats["std"]).tolist()
#         lsl = (stats["mean"] - stats["std"]).tolist()

#         ret.update(
#             {
#                 col: {
#                     "count": stats["count"].tolist(),
#                     "data": data,
#                     "mean": stats["mean"].tolist(),
#                     "std": std,
#                     "ucl": round(ucl, 3),
#                     "lcl": round(lcl, 3),
#                     "usl": round(usl, 3),
#                     "lsl": round(lsl, 3),
#                     "min": stats["min"].tolist(),
#                     "max": stats["max"].tolist(),
#                     "ooc": populate_ooc(data, ucl, lcl),
#                 }
#             }
#         )

#     return ret


# def populate_ooc(data, ucl, lcl):
#     ooc_count = 0
#     ret = []
#     for i in range(len(data)):
#         if data[i] >= ucl or data[i] <= lcl:
#             ooc_count += 1
#             ret.append(ooc_count / (i + 1))
#         else:
#             ret.append(ooc_count / (i + 1))
#     return ret


# state_dict = init_df()


# def init_value_setter_store():
#     # Initialize store data
#     state_dict = init_df()
#     return state_dict


def build_tab_1():
    return [
        # Manually select metrics
        html.Div(
            id="fuente-intro-container",
            children=html.P(
                "Selecciona la fuente de noticias para ver los titulares y su clasificación"
            ),
        ),
        html.Div(
            id="fuente-menu",
            children=[
                html.Div(
                    id="fuente-select-menu",
                    children=[
                        html.Label(id="fuente-select-title", children="Fuente de noticias"),
                        html.Br(),
                        dcc.Dropdown(
                            options=fuentes, 
                            value=fuentes[0],
                            id="fuente-select-dropdown",
                            multi=False,
                            searchable=True,
                        ),
                    ],
                ),
                html.Div(
                    id="value-setter-menu",
                    children=[
                        html.Div(id="value-setter-panel"),
                        html.Br(),
                html.Div(
                    id="value-setter-view-output", className="output-datatable",
                    children=[
                    dash_table.DataTable(
                            id='noticias-table',
                            columns=[{"name": i, "id": i} for i in df.columns],
                            data=df[df['fuente']==fuentes[0]].to_dict('records'),
                            page_size=25,

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
                        )  
                    ]
                ),
            ]),
            ],
        ),
    ]


# ud_usl_input = daq.NumericInput(
#     id="ud_usl_input", className="setting-input", size=200, max=9999999
# )
# ud_lsl_input = daq.NumericInput(
#     id="ud_lsl_input", className="setting-input", size=200, max=9999999
# )
# ud_ucl_input = daq.NumericInput(
#     id="ud_ucl_input", className="setting-input", size=200, max=9999999
# )
# ud_lcl_input = daq.NumericInput(
#     id="ud_lcl_input", className="setting-input", size=200, max=9999999
# )

def generate_modal():
    return html.Div(
        id="markdown",
        className="modal",
        children=(
            html.Div(
                id="markdown-container",
                className="markdown-container",
                children=[
                    html.Div(
                        className="close-container",
                        children=html.Button(
                            "Close",
                            id="markdown_close",
                            n_clicks=0,
                            className="closeButton",
                        ),
                    ),
                    html.Div(
                        className="markdown-text",
                        children=dcc.Markdown(
                            children=(
                                """
                        ###### ¿De qué va este panel?

                        Éste es un Dashboard que monitoriza diariamente los principales medios de comunicación españoles.
                        Todos los días se recogen los titulares y se clasifican en dos categorías: Clickbait o No Clickbait.
                        Una noticia es clickbait o cebo cuando trata de atraer la atención del lector con un titular y no es clickbait cuando el titular es descriptivo del contenido de la noticia.

                        ###### ¿Qué información se muestra en este panel?
                        
                        En este panel se muestran las diferentes fuentes de noticias y los titulares recogidos en el día.
                        
                        También mostramos la evolución del porcentaje de noticias clickbait en cada fuente a lo largo del tiempo. Esto nos da una idea comparativa entre los diferentes medios y también nos permite ver si hay alguna tendencia en el tiempo, que puede correlacionar o no con eventos generales como unas elecciones.
                        
                        ###### ¿Cómo se clasifican las noticias y dónde encontrar el código fuente?
                        
                        Para saber cómo se clasifican las noticias puedes consultar los entresijos en este artículo del blog de taniwa: [Cómo construimos un modelo IA de clasificación de titulares (en una semana)](https://taniwa.es/blog/clickbait_es/)

                    """
                            )
                        ),
                    ),
                ],
            )
        ),
    )


def build_quick_stats_panel():
    return html.Div(
        id="quick-stats",
        className="row",
        children=[
            html.Div(
                id="card-1",
                children=[
                    html.P("Fuente"),
                    daq.LEDDisplay(
                        id="operator-led",
                        value=fuentes[0],
                        color="#92e0d3",
                        backgroundColor="#1e2130",
                        size=50,
                    ),
                ],
            ),
            html.Div(
                id="card-2",
                children=[
                    html.P("Porcentaje de noticias clickbait"),
                    daq.Gauge(
                        id="progress-gauge",
                        max=100,
                        min=0,
                        value=0,
                        showCurrentValue=True,  # default size 200 pixel
                    ),
                ],
            ),
        ],
    )
def generate_piechart():
    return dcc.Graph(
        id="piechart",
        figure={
            "data": [
                {
                    "labels": [],
                    "values": [],
                    "type": "pie",
                    "marker": {"line": {"color": "white", "width": 1}},
                    "hoverinfo": "label",
                    "textinfo": "label",
                }
            ],
            "layout": {
                "margin": dict(l=20, r=20, t=20, b=20),
                "showlegend": True,
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"color": "white"},
                "autosize": True,
            },
        },
    )

# Para mostrar un porcentaje
    # {"id": ooc_percentage_id, "children": "0.00%"},
    # {
    #     "id": ooc_graph_id + "_container",
    #     "children": daq.GraduatedBar(
    #         id=ooc_graph_id,
    #         color={
    #             "ranges": {
    #                 "#92e0d3": [0, 3],
    #                 "#f4d44d ": [3, 7],
    #                 "#f45060": [7, 15],
    #             }
    #         },
    #         showCurrentValue=False,
    #         max=15,
    #         value=0,
    #     ),
    # },

def build_chart_panel():
    return html.Div(
        id="control-chart-container",
        className="twelve columns",
        children=[
            html.Div(className="section-banner", children="Evolución de noticias clickbait"),
            dcc.Graph(
                id="control-chart-live",
                figure=go.Figure(
                    {
                        "data": [
                            {
                                "x": [],
                                "y": [],
                                "mode": "lines+markers",
                                "name": params[1],
                            }
                        ],
                        "layout": {
                            "paper_bgcolor": "rgba(0,0,0,0)",
                            "plot_bgcolor": "rgba(0,0,0,0)",
                            "xaxis": dict(
                                showline=False, showgrid=False, zeroline=False
                            ),
                            "yaxis": dict(
                                showgrid=False, showline=False, zeroline=False
                            ),
                            "autosize": True,
                        },
                    }
                ),
            ),
        ],
    )


def generate_graph(interval, specs_dict, col):
    stats = state_dict[col]
    col_data = stats["data"]
    mean = stats["mean"]
    ucl = specs_dict[col]["ucl"]
    lcl = specs_dict[col]["lcl"]
    usl = specs_dict[col]["usl"]
    lsl = specs_dict[col]["lsl"]

    x_array = state_dict["Batch"]["data"].tolist()
    y_array = col_data.tolist()

    total_count = 0

    if interval > max_length:
        total_count = max_length - 1
    elif interval > 0:
        total_count = interval

    ooc_trace = {
        "x": [],
        "y": [],
        "name": "Out of Control",
        "mode": "markers",
        "marker": dict(color="rgba(210, 77, 87, 0.7)", symbol="square", size=11),
    }

    for index, data in enumerate(y_array[:total_count]):
        if data >= ucl or data <= lcl:
            ooc_trace["x"].append(index + 1)
            ooc_trace["y"].append(data)

    histo_trace = {
        "x": x_array[:total_count],
        "y": y_array[:total_count],
        "type": "histogram",
        "orientation": "h",
        "name": "Distribution",
        "xaxis": "x2",
        "yaxis": "y2",
        "marker": {"color": "#f4d44d"},
    }

    fig = {
        "data": [
            {
                "x": x_array[:total_count],
                "y": y_array[:total_count],
                "mode": "lines+markers",
                "name": col,
                "line": {"color": "#f4d44d"},
            },
            ooc_trace,
            histo_trace,
        ]
    }

    len_figure = len(fig["data"][0]["x"])

    fig["layout"] = dict(
        margin=dict(t=40),
        hovermode="closest",
        uirevision=col,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend={"font": {"color": "darkgray"}, "orientation": "h", "x": 0, "y": 1.1},
        font={"color": "darkgray"},
        showlegend=True,
        xaxis={
            "zeroline": False,
            "showgrid": False,
            "title": "Batch Number",
            "showline": False,
            "domain": [0, 0.8],
            "titlefont": {"color": "darkgray"},
        },
        yaxis={
            "title": col,
            "showgrid": False,
            "showline": False,
            "zeroline": False,
            "autorange": True,
            "titlefont": {"color": "darkgray"},
        },
    )

    return fig


def update_sparkline(interval, param):
    x_array = state_dict["Batch"]["data"].tolist()
    y_array = state_dict[param]["data"].tolist()

    if interval == 0:
        x_new = y_new = None

    else:
        if interval >= max_length:
            total_count = max_length
        else:
            total_count = interval
        x_new = x_array[:total_count][-1]
        y_new = y_array[:total_count][-1]

    return dict(x=[[x_new]], y=[[y_new]]), [0]


def update_count(interval, col, data):
    if interval == 0:
        return "0", "0.00%", 0.00001, "#92e0d3"

    if interval > 0:

        if interval >= max_length:
            total_count = max_length - 1
        else:
            total_count = interval - 1

        ooc_percentage_f = data[col]["ooc"][total_count] * 100
        ooc_percentage_str = "%.2f" % ooc_percentage_f + "%"

        # Set maximum ooc to 15 for better grad bar display
        if ooc_percentage_f > 15:
            ooc_percentage_f = 15

        if ooc_percentage_f == 0.0:
            ooc_grad_val = 0.00001
        else:
            ooc_grad_val = float(ooc_percentage_f)

        # Set indicator theme according to threshold 5%
        if 0 <= ooc_grad_val <= 5:
            color = "#92e0d3"
        elif 5 < ooc_grad_val < 7:
            color = "#f4d44d"
        else:
            color = "#FF0000"

    return str(total_count + 1), ooc_percentage_str, ooc_grad_val, color


app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        dcc.Interval(
            id="interval-component",
            interval=2 * 1000,  # in milliseconds
            n_intervals=50,  # start at batch 50
            disabled=True,
        ),
        html.Div(
            id="app-container",
            children=[
                build_tabs(),
                # Main app
                html.Div(id="app-content"),
            ],
        ),
        dcc.Store(id="value-setter-store", data=init_value_setter_store()),
        dcc.Store(id="n-interval-stage", data=50),
        generate_modal(),
    ],
)


@app.callback(
    [Output("app-content", "children"), Output("interval-component", "n_intervals")],
    [Input("app-tabs", "value")],
    [State("n-interval-stage", "data")],
)
def render_tab_content(tab_switch, stopped_interval):
    if tab_switch == "tab1":
        return build_tab_1(), stopped_interval
    return (
        html.Div(
            id="status-container",
            children=[
                build_quick_stats_panel(),
                html.Div(
                    id="graphs-container",
                    children=[build_chart_panel()],
                ),
            ],
        ),
        stopped_interval,
    )


# Update interval
@app.callback(
    Output("n-interval-stage", "data"),
    [Input("app-tabs", "value")],
    [
        State("interval-component", "n_intervals"),
        State("interval-component", "disabled"),
        State("n-interval-stage", "data"),
    ],
)
def update_interval_state(tab_switch, cur_interval, disabled, cur_stage):
    if disabled:
        return cur_interval

    if tab_switch == "tab1":
        return cur_interval
    return cur_stage


# ======= Callbacks for modal popup =======
@app.callback(
    Output("markdown", "style"),
    [Input("learn-more-button", "n_clicks"), Input("markdown_close", "n_clicks")],
)
def update_click_output(button_click, close_click):
    ctx = dash.callback_context

    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop_id == "learn-more-button":
            return {"display": "block"}

    return {"display": "none"}


# ======= update progress gauge =========
@app.callback(
    output=Output("progress-gauge", "value"),
    inputs=[Input("interval-component", "n_intervals")],
)
def update_gauge(interval):
    if interval < max_length:
        total_count = interval
    else:
        total_count = max_length

    return int(total_count)


# ===== Callbacks to update values based on store data and dropdown selection =====
@callback(
# @app.callback(
#     output=[
        Output("value-setter-panel", "children"),
        # Output("ud_usl_input", "value"),
        # Output("ud_lsl_input", "value"),
        # Output("ud_ucl_input", "value"),
        # Output("ud_lcl_input", "value"),
    # ],
    inputs=[Input("fuente-select-dropdown", "value")],
    state=[State("value-setter-store", "data")],
)


# ====== Callbacks to update stored data via click =====
@app.callback(
    output=Output("value-setter-store", "data"),
    inputs=[Input("value-setter-set-btn", "n_clicks")],
    state=[
        State("fuente-select-dropdown", "value"),
        State("value-setter-store", "data"),
        # State("ud_usl_input", "value"),
        # State("ud_lsl_input", "value"),
        # State("ud_ucl_input", "value"),
        # State("ud_lcl_input", "value"),
    ],
)
def set_value_setter_store(set_btn, param, data):
    usl = daq.NumericInput(
        id="ud_usl_input", className="setting-input", size=200, max=9999999
    )
    lsl = daq.NumericInput(
        id="ud_lsl_input", className="setting-input", size=200, max=9999999
    )
    ucl = daq.NumericInput(
        id="ud_ucl_input", className="setting-input", size=200, max=9999999
    )
    lcl = daq.NumericInput(
        id="ud_lcl_input", className="setting-input", size=200, max=9999999
    )
    if set_btn is None:
        return data
    else:
        data[param]["usl"] = usl
        data[param]["lsl"] = lsl
        data[param]["ucl"] = ucl
        data[param]["lcl"] = lcl

        # Recalculate ooc in case of param updates
        data[param]["ooc"] = populate_ooc(df[param], ucl, lcl)
        return data


@app.callback(
    output=Output("value-setter-view-output", "children"),
    inputs=[
        Input("value-setter-view-btn", "n_clicks"),
        Input("fuente-select-dropdown", "value"),
        Input("value-setter-store", "data"),
    ],
)
def show_current_specs(n_clicks, dd_select, store_data):
    if n_clicks > 0:
        curr_col_data = store_data[dd_select]
        new_df_dict = {
            "Specs": [
                "Upper Specification Limit",
                "Lower Specification Limit",
                "Upper Control Limit",
                "Lower Control Limit",
            ],
            "Current Setup": [
                curr_col_data["usl"],
                curr_col_data["lsl"],
                curr_col_data["ucl"],
                curr_col_data["lcl"],
            ],
        }
        new_df = pd.DataFrame.from_dict(new_df_dict)
        return dash_table.DataTable(
            style_header={"fontWeight": "bold", "color": "inherit"},
            style_as_list_view=True,
            fill_width=True,
            style_cell_conditional=[
                {"if": {"column_id": "Specs"}, "textAlign": "left"}
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
            data=new_df.to_dict(orient="records"),
            columns=[{"id": c, "name": c} for c in ["Specs", "Current Setup"]],
        )


# decorator for list of output
def create_callback(param):
    def callback(interval, stored_data):
        count, ooc_n, ooc_g_value, indicator = update_count(
            interval, param, stored_data
        )
        spark_line_data = update_sparkline(interval, param)
        return count, spark_line_data, ooc_n, ooc_g_value, indicator

    return callback


for param in params[1:]:
    update_param_row_function = create_callback(param)
    app.callback(
        output=[
            Output(param + suffix_count, "children"),
            Output(param + suffix_sparkline_graph, "extendData"),
            Output(param + suffix_ooc_n, "children"),
            Output(param + suffix_ooc_g, "value"),
            Output(param + suffix_indicator, "color"),
        ],
        inputs=[Input("interval-component", "n_intervals")],
        state=[State("value-setter-store", "data")],
    )(update_param_row_function)


#  ======= button to choose/update figure based on click ============
@app.callback(
    output=Output("control-chart-live", "figure"),
    inputs=[
        Input("interval-component", "n_intervals"),
        Input(params[1] + suffix_button_id, "n_clicks"),
        Input(params[2] + suffix_button_id, "n_clicks"),
        Input(params[3] + suffix_button_id, "n_clicks"),
        Input(params[4] + suffix_button_id, "n_clicks"),
        Input(params[5] + suffix_button_id, "n_clicks"),
        Input(params[6] + suffix_button_id, "n_clicks"),
        Input(params[7] + suffix_button_id, "n_clicks"),
    ],
    state=[State("value-setter-store", "data"), State("control-chart-live", "figure")],
)
def update_control_chart(interval, n1, n2, n3, n4, n5, n6, n7, data, cur_fig):
    # Find which one has been triggered
    ctx = dash.callback_context

    if not ctx.triggered:
        return generate_graph(interval, data, params[1])

    if ctx.triggered:
        # Get most recently triggered id and prop_type
        splitted = ctx.triggered[0]["prop_id"].split(".")
        prop_id = splitted[0]
        prop_type = splitted[1]

        if prop_type == "n_clicks":
            curr_id = cur_fig["data"][0]["name"]
            prop_id = prop_id[:-7]
            if curr_id == prop_id:
                return generate_graph(interval, data, curr_id)
            else:
                return generate_graph(interval, data, prop_id)

        if prop_type == "n_intervals" and cur_fig is not None:
            curr_id = cur_fig["data"][0]["name"]
            return generate_graph(interval, data, curr_id)


# Update piechart
@app.callback(
    output=Output("piechart", "figure"),
    inputs=[Input("interval-component", "n_intervals")],
    state=[State("value-setter-store", "data")],
)
def update_piechart(interval, stored_data):
    if interval == 0:
        return {
            "data": [],
            "layout": {
                "font": {"color": "white"},
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
            },
        }

    if interval >= max_length:
        total_count = max_length - 1
    else:
        total_count = interval - 1

    values = []
    colors = []
    for param in params[1:]:
        ooc_param = (stored_data[param]["ooc"][total_count] * 100) + 1
        values.append(ooc_param)
        if ooc_param > 6:
            colors.append("#f45060")
        else:
            colors.append("#91dfd2")

    new_figure = {
        "data": [
            {
                "labels": params[1:],
                "values": values,
                "type": "pie",
                "marker": {"colors": colors, "line": dict(color="white", width=2)},
                "hoverinfo": "label",
                "textinfo": "label",
            }
        ],
        "layout": {
            "margin": dict(t=20, b=50),
            "uirevision": True,
            "font": {"color": "white"},
            "showlegend": False,
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "autosize": True,
        },
    }
    return new_figure


# Running the server
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)