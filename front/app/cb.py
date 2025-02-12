import os
import dash
from dash import dash_table, Input, Output, State, html, dcc, callback
import plotly.express as px

import dash_bootstrap_components as dbc
import dash_daq as daq
import pandas as pd
import dotenv

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TextClassificationPipeline,
)



app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "Clickbait en español", "content": "width=device-width, initial-scale=2"}],
)

app.title = "Clickbait o seguimiento de noticias cebo"
server = app.server
app.config["suppress_callback_exceptions"] = True
external_stylesheets = [dbc.themes.BOOTSTRAP]

dotenv.load_dotenv()
AGG_FILE_PATH=os.getenv("AGG_FILE_PATH")
LAST30_FILE_PATH=os.getenv("LAST30_FILE_PATH")

df = pd.read_csv(LAST30_FILE_PATH)
df_agg=pd.read_csv(AGG_FILE_PATH)
df_mean=df_agg.groupby([df_agg['fecha']],as_index=False)['clickbait_prc'].mean()
df_mean['fuente']='MEDIA DIARIA'
df_mean['num']=0
# df_agg=pd.concat([df_agg,df_mean], ignore_index=True)
fuentes=sorted(df_agg.fuente.unique())
## Seleccionados 2 fuentes a fuego.
# fuentes=['Antena 3 Noticias','RTVE']


prc_fuente = 5
tokenizerDOS = AutoTokenizer.from_pretrained("modelo/clickbait_es") #"taniwasl/clickbait_es")
modelDOS = AutoModelForSequenceClassification.from_pretrained("modelo/clickbait_es") #("taniwasl/clickbait_es")
nlp = TextClassificationPipeline(task = "text-classification",
                model = modelDOS,
                tokenizer = tokenizerDOS,
                max_length = 25,
                truncation=True,
                add_special_tokens=True
                )



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

def build_graph():
    return html.Div(
        id="graph",
        className="graph",
        # style={"height":"fit-content"  , "width": "80%", "margin": "10px",  "border": "1px solid #ccc", "border-radius": "5px",  "box-shadow": "0 2px 4px 0 rgba(0,0,0,0.1)", "transition": "0.3s"},
        style={"height":"fit-content"  , "width": "90%", "height": "fit-content","margin": "10px",  "transition": "0.3s"},
        children=[
            html.Div(         
                    dcc.Graph(
                        id='control-chart-live',
                        figure=px.line(
                            df_agg, x='fecha', y='clickbait_prc', color='fuente', symbol='fuente', 
                            markers=True, 
                            title='Evolución de porcentaje de noticias clickbait por medio de comunicación y Día',
                            labels={'fecha':'Fecha', 'clickbait_prc':'% Clickbait','fuente':'Medio'},
                            line_shape="spline", render_mode="auto",height=800,
                            color_discrete_sequence=px.colors.qualitative.Vivid_r ,# px.colors.qualitative.Alphabet_r,
                            template= 'simple_white', # 'plotly_dark' #                            # facet_row='fuente'
                        )
                    ),
                    # style={"height": "100%", "width": "100%"}, 
            ),
            html.Div(
                id="fin",
                children=[
                    html.Hr(),
                ],
            ),
            html.Div(         
                    dcc.Graph(
                        id='mean-chart-live',
                        figure=px.line(
                            df_mean, x='fecha', y='clickbait_prc', 
                            markers=True, 
                            title='Media de clickbaits',
                            labels={'fecha':'Fecha', 'clickbait_prc':'% Clickbait'},
                            line_shape="spline", render_mode="auto",height=200,
                            template= 'simple_white', # 'plotly_dark' #                            # facet_row='fuente'
                        )
                    ),
                    # style={"height": "100%", "width": "100%"}, 
            ),            
        ],
    )
    
def generate_modal():
    return html.Div(
        id="markdown",
        className="modal",
        children=[
            html.Div(
                id="markdown-container",
                className="markdown-container",
                children=[
                    html.Div(
                        className="close-container",
                        children=html.Button(
                            "CERRAR",
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
        ],
    )

def build_datos_por_fuente():
    return html.Div(
            id="data",
            className="data",
            style={"height":"fit-content"  , "width": "70%", "margin": "10px",  "border": "1px solid #ccc", "border-radius": "5px",  "box-shadow": "0 2px 4px 0 rgba(0,0,0,0.1)", "transition": "0.3s"},
            children=[
                html.Div(
                id="drop-down-container",
                style={"height":"fit-content"  , "width": "100%",  "padding": "10px", "align":"center", "justify":"center"},
                    children=[
                        dbc.Row([
                            dbc.Col(
                                html.Div(
                                    id="fuente-select-menu",
                                    children=[
                                        html.Label(id="fuente-select-title", children="Fuente de noticias"),
                                        dcc.Dropdown(
                                            options=[{"label": i, "value": i} for i in fuentes], 
                                            value=fuentes[0],
                                            id="fuente-select-dropdown",
                                            multi=False,
                                            searchable=True,
                                        ),
                                        html.Hr(), 
                                    ],
                                )
                                
                            ),
                            dbc.Col(
                                html.Div(
                                    id="fuente-prc",
                                    children=[
                                        html.Label(id="fuente-prc-title", children="% clickbait en últimas noticias"),
                                        daq.GraduatedBar(
                                            id="grad_bar",
                                            color={
                                                "gradient":True,
                                                "ranges": {
                                                    "#92e0d3": [0, 20],
                                                    "#f4d44d": [20, 50],
                                                    "#f45060": [50, 100],
                                                }
                                            },
                                            showCurrentValue=True,
                                            max=100,
                                            value=prc_fuente,
                                            step=5, 
                                        ),
                                    ], 
                                ),
                               
                            ), 
                        ], justify="center"),
                        dbc.Row([
                            html.Div(
                                id="noticias-view-output", className="noticias-datatable",
                                children=[
                                dash_table.DataTable(
                                        id='noticias-table',
                                        columns=[{"name": i, "id": i} for i in ['titulo','cb','score']],
                                        data=df[df['fuente']==fuentes[0]][['titulo','cb','score']].to_dict('records'),
                                        page_size=25,
                                        style_table={ 'overflowX': 'auto', 'overflowY': 'auto'},
                                        style_header={'backgroundColor': 'rgb(40, 40, 40)', 'color': 'white' , 'fontWeight': 'bold'},   
                                        style_data={
                                            'color': 'black',
                                            'backgroundColor': 'white',
                                            'whiteSpace': 'normal',
                                            'height': 'auto',
                                        },
                                        style_data_conditional=[
                                            {
                                                'if': {'row_index': 'odd'},
                                                "backgroundColor": "#f3f3f3",
                                            }
                                        ],
                                        style_as_list_view=True,
                                        fill_width=True,
                                        style_cell_conditional=[
                                            {"if": {"column_id": "score"}, "textAlign": "right"}
                                        ],
                                        style_cell={
                                            "fontFamily": "Open Sans",
                                            "padding": "0 2rem",
                                            "color": "black",
                                            "border": "none",
                                            'textAlign': 'left'
                                        },
                                    )  
                                ]
                            ), 
                        ]),
                    ],     
                ),
            ]
        )

def build_uso_clickbait(): 
    return html.Div(
            id="probando",
            style={"width": "80%", "margin": "10px",  "border": "1px solid #ccc", "border-radius": "5px",  "box-shadow": "0 2px 4px 0 rgba(0,0,0,0.1)", "transition": "0.3s"},
            children=[
            dbc.Row(
                id='input-noticia-container',
                children=[
                dbc.Col(
                    html.Div(
                        dcc.Input(id='input-noticia',
                            type='text',
                            placeholder='Introduce un titular',
                            autoComplete='off',
                            style={ 'color': 'black', 'borderRadius': '10px', 'padding': '10px', 'margin': '10px', 'width': '100%'},   
                        ),
                    # style={"width": "100%", "margin": "10px",  "border": "1px solid #ccc",},   
                    ),
                    width=10
                ),
                dbc.Col(
                    html.Button('Predecir', id='submit-button', n_clicks=0, 
                                style={ 'color': 'black', 'borderRadius': '10px', 'margin': '10px'}, #{'width': '20%', 'height': '50px', 'color': 'black', 'fontSize': '12px', 'borderRadius': '10px', }
                    ),
                    width=2
                ),
                ],
            ),
            dbc.Row(
            [
                dbc.Col(width=2),
                dbc.Col(
                [ 
                    html.Div(
                        daq.LEDDisplay(
                            label="NA",
                            labelPosition='top',
                            id='output-noticia',
                            value='0.00',
                            color="gray",
                            size=150,
                            style={'align':'center', 'margin':'20px', 'padding':'10px', 'border':'0px solid grey'}
                        )                        
                    ),
                ],
                    width=8, 

                ),
                dbc.Col(width=2)
            ]
            ),    
        ],
    )




# ======================================================================================================================================
# CALLBACKS
# ======================================================================================================================================
@app.callback(
    Output("markdown", "style"),
    [Input("learn-more-button", "n_clicks"), 
     Input("markdown_close", "n_clicks")],
)
def update_click_output(button_click, close_click):
    ctx = dash.callback_context

    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop_id == "learn-more-button":
            return {"display": "block"}

    return {"display": "none"}
# --------------------------------------------------------------------------------------------------------------------------------------
@callback(
    Output('grad_bar', 'value'),
    Output('noticias-table', 'data'),
    Input("fuente-select-dropdown", "value"),
)
def update_fuente(fuente):
    '''
    Actualiza el valor de la barra de progreso con el porcentaje de noticias clickbait de la fuente seleccionada y
    devuelve el valor para la barra de progreso.
    '''
    prc=0.0
    data=[]
    if fuente:
        prc = df_agg[df_agg['fuente']==fuente]['clickbait_prc'].mean()
        df = pd.read_csv(LAST30_FILE_PATH)
        data=df[df['fuente']==fuente][['titulo','cb','score']].to_dict('records')
    return prc, data
    
# --------------------------------------------------------------------------------------------------------------------------------------
@callback(
    Output('output-noticia', 'value'),
    Output('output-noticia','color'),
    Output('output-noticia', 'label'),
    Input("submit-button", "n_clicks"),
    State("input-noticia", "value"),
)
def update_pred(n_clicks, value):
    if value and len(value)>4:
        res= nlp(value)
        if (res[0]['label']=='Clickbait'):
            color='#dc4820'
            cad="ES UN TITULAR CLICKBAIT"
        else:
            color='#2379dc'
            cad="ES UN TITULAR DESCRIPTIVO"
            # cad=f"El titular se puede clasificar como {res[0]['label']} con una probabilidad de :{100.0*res[0]['score']: 0.3f}%"
        print
        valor=f"{100.0*res[0]['score']:00.3f}"
        return (valor, color , cad)
    else:
        return ("0.00", "gray", "NA")
# --------------------------------------------------------------------------------------------------------------------------------------
@callback(
    Output('control-chart-live', 'figure'),
    Output('mean-chart-live', 'figure'),
    Output("fuente-select-dropdown", "value"),
    Input('interval-hour', 'n_intervals'),
    # prevent_initial_call=True
)
def update_data(n_intervals):
    df = pd.read_csv(LAST30_FILE_PATH)
    df_agg=pd.read_csv(AGG_FILE_PATH)
    df_mean=df_agg.groupby([df_agg['fecha']],as_index=False)['clickbait_prc'].mean()
    df_mean['fuente']='MEDIA DIARIA'
    df_mean['num']=0
    # df_agg=pd.concat([df_agg,df_mean], ignore_index=True)
    fuentes=sorted(df.fuente.unique())
    f = px.line(
            df_agg, x='fecha', y='clickbait_prc', color='fuente', symbol='fuente', 
            markers=True, 
            title='Evolución de porcentaje de noticias clickbait por Medio y día',
            labels={'fecha':'Fecha', 'clickbait_prc':'% Clickbait','fuente':'Medio'},
            line_shape="spline", render_mode="auto",height=800,
            color_discrete_sequence=px.colors.qualitative.Vivid_r,
            template= 'simple_white',
        )
    f.update_layout(legend=dict(orientation="h"))  #yanchor="top",y=0.99,xanchor="left",x=0.01))
    f.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))
    f.update_layout(
    xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=7,
                        label="7d",
                        step="day",
                        stepmode="backward"),
                    dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                    dict(step="all", label="Todo")
                ])
            ),
            rangeslider=dict(
                visible=False
            ),
            type="date"
        )
    )
    f.update_traces(line=dict(width=2), marker=dict(size=10))
    f.add_scatter(x=df_mean['fecha'], y=df_mean['clickbait_prc'], mode='lines+markers', name='Media diaria', line=dict(width=10, color='Grey'),  marker=dict(size=15))

    f_mean = px.line(
            df_mean, x='fecha', y='clickbait_prc', 
            markers=True, 
            title='Media de clickbaits',
            labels={'fecha':'Fecha', 'clickbait_prc':'% Clickbait'},
            line_shape="spline", render_mode="auto",height=800,
            template= 'simple_white',
        )
    f_mean.update_traces(line=dict(width=10, color='Grey'), marker=dict(size=15))
    f_mean.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))
    return (f,f_mean,  fuentes[0])

        
# ======================================================================================================================================
# LAYOUT
# ======================================================================================================================================
app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        build_graph(),
        build_datos_por_fuente(),
        build_uso_clickbait(),
        generate_modal(),
        dcc.Interval(
            id='interval-hour',
            interval=1000*60*60, # One hour in milliseconds
            n_intervals=0
        ),
    ],
)



if __name__ == "__main__":
    app.run(debug=True)