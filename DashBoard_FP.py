import pandas as pd
import dash
from dash import dcc,html,dash_table, ctx,DiskcacheManager, CeleryManager
from collections import Counter
from dash.dependencies import Output, Input,State
from dash.long_callback import DiskcacheLongCallbackManager
import dash_bootstrap_components as dbc
from datetime import date
import dash_daq as daq
from matplotlib.pyplot import bar_label
import plotly.express as px
import dash_grocery
import plotly.graph_objs as go
import dash_d3cloud
from dash.exceptions import PreventUpdate
from datetime import date, timedelta
import re
import time
import os
today = date.today()

# import spacy
# nlp_model_1 = nlp_model = spacy.load("en_core_web_sm")
def clean_text(text):
    content_texts = text
    contents_string=str(content_texts)
    contents_string_cleaned=re.sub(r'[^a-z A-Z]',' ',contents_string)
    contents_string_cleaned=re.sub(r'\b\w{1,2}\b',' ',contents_string_cleaned)
    contents_string_cleaned=re.sub(r' +',' ',contents_string_cleaned)
    contents_string_cleaned=contents_string_cleaned.lower()
#addedd below will remove later
    # contents_string_cleaned = "".join([word for word in contents_string_cleaned])
    # doc = nlp_model(contents_string_cleaned)
    # contents_string_cleaned = [word.lemma_ for word in doc]
    # contents_string_cleaned = [word for word in contents_string_cleaned if word not in nlp_model.Defaults.stop_words]
    # contents_string_cleaned = " ".join([word for word in contents_string_cleaned])
    # return text
    
    return contents_string_cleaned

pos_final = pd.read_csv("PositiveFeedback.csv")
neg_final = pd.read_csv("NegativeFeedback.csv")

df = pd.read_csv("finalDF.csv")
posDf = pd.read_csv("PositiveFeedback.csv")
# neuDf = neu_final[["Name","Review","Date","Country","Version","Rating","Platform"]]
# mixDf = mix_final[["Name","Review","Date","Country","Version","Rating","Platform"]]
emerengy_df = df[(df['sentiment']=='Positive') |  (df['sentiment']=='Negative') | (df['sentiment']=='Mixed')]
mixDf = pd.read_csv("MixedFeedback.csv")
negDf = pd.read_csv("NegativeFeedback.csv")

app = dash.Dash(__name__,suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.FLATLY],
                meta_tags=[{'name' : 'viewport',
                            'content': 'width=device-width, initial-scale=1.0' }]
                )



# layout
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    # "background-color": "#f8f9fa",
}
LEFTBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "right": 0,
    "bottom": 0,
    "width": "19rem",
    "padding": "2rem 1rem",
    # "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "21rem",
    "padding": "2rem 1rem",
}

BUTTON_STYLE={
#     'background-color': '#f8f9fa',
    'border-radius': '12px',
    'text-align': 'left',
    'height': '50px',
    'width': '24rem',
    'padding': '2',
    'border': 'none',
}
sidebar = html.Div(
    [
        html.H4("Analysis", className="text-muted"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Sentiment", href="/sentiment", active="exact"),
                dbc.NavLink("Visualization", href="/visualization", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
#     className = "shadow"
)
leftbar = html.Div(
    [
        html.Br(),
        html.Br(),
        html.P(
            [
                html.Span(
                    "FP-Version Release Dates \n ",
                    id="tooltip-target",
                    style={"textDecoration": "underline", "cursor": "pointer"},
                ),
            ]
        ),
        dbc.Tooltip(
            "2022 Oct 5 - 4.22.0"
            "2022 Sept 14 - 4.21.0",
            target="tooltip-target",
        ),
        html.H5("Filters", className="text-muted"),
        html.Br(),
        html.Div([
                dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=date(2022, 5, 1),
                max_date_allowed=today,
                initial_visible_month=today,
                # end_date=today
                minimum_nights=4,
                clearable=True,
                with_portal=True,
                reopen_calendar_on_clear = True,
            ),
            html.Br(),
            html.Br(),
            html.H6("Country"),
                dcc.Dropdown(
                id="country",
                    options=[
                        {"label": col, "value": col} for col in df['Country'].dropna().unique()
                    ],
                    multi= True,
                ),
            html.Br(),
            html.H6("Version"),
                dcc.Dropdown(
                id="version",
                    multi= True,
                ),
            html.Br(),
            html.H6("Platform"),
            dcc.Dropdown(
                id="platform",
                    options=[
                        {"label": val, "value": val} for val in df['Platform'].sort_values(ascending=False).dropna().unique() if val != None
                    ],
                    multi=True,
                )
            ],className="ml-10 display-flex")
    ],
    style=LEFTBAR_STYLE,
)

@app.callback(
    Output("positioned-toast", "is_open"),
    [Input("positioned-toast-toggle", "n_clicks")],
)
def open_toast(n):
    if n:
        return True
    return False

content = html.Div(id="page-content", style=CONTENT_STYLE)


app.layout = html.Div([dcc.Location(id="url"),sidebar,leftbar,content])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return [html.Div([
        dbc.Col([
             html.H2("Welcome to Our Dashboard", className="display-5"),
             html.Hr(className="my-2"),
             html.Hr(className="my-2"),
             html.P([
                    "You can use this Dashboard to",
                     html.Br(),
                    "Check Customer's Sentiment",
                     html.Br(),
                    "Date-Range wise Review Fetch - with Mandatory fields(Country , Version, Platform )",
                     html.Br(),
                    " Over-all Positive and Negative WordCloud",
                    html.Br(),
                    "Get Report of Selected Date-Range"
                ]),
            dbc.Button("View Report", color="light", outline=True,id="btn-home"),
        ],
        className="shadow-lg h-100 p-5 text-white bg-dark rounded-lg")
      ]
    ),
    html.Br(),
    html.Br(),
    html.Div(id='home-Overall')]
    elif pathname == "/sentiment":
        return [html.Div(
        [ 
            html.H5("Sentiment-Breakdown", className="display-6"),
            html.Hr(className="my-2"),
            html.P(
                "what user think of FordPass ?"
            ),
            html.Div(
        [
            dbc.ButtonGroup(
                [dbc.Button("Positive",id='btn-nclicks-1'), dbc.Button("Mixed",id='btn-nclicks-2'), dbc.Button("Negative",id='btn-nclicks-3')],
                size="lg",
                className="me-1",
            ),
            html.Br(),
            html.Br(),
        ]
            )
        ],
        className="shadow h-100 p-5 bg-light border rounded-4",
    ),  
        html.Br(),
        html.Div(id='container-button-timestamp')]
    elif pathname == "/visualization":
        return [html.Div([
            html.Div([
                dbc.Card([
                    dbc.CardHeader("Positive WordCloud"),
                    dash_d3cloud.WordCloud(
                    id='posword_cloud',
                    words=word_for_wordclouds(100),
                    options={
                    'spiral': 'archimedean',
                    'scale': 'log',
                    'rotations': 2,
                    'rotationAngles': [-10, 60],
                    },
                    )
                ], className="mb-3 gap",
    style={"display": "inline-block","width":"48%","padding": "10px",'margin-left': '15px' },  
                ),
                dbc.Card([
                    dbc.CardHeader("Negative WordCloud"),
                    dash_d3cloud.WordCloud(
                    id='negword_cloud',
                    words=word_for_wordclouds_neg(100),
                    options={
                    'spiral': 'archimedean',
                    'scale': 'log',
                    'rotations': 2,
                    'rotationAngles': [-10, 60],
                    },
                    )
                ], className="mb-3 gap",
    style={"display": "inline-block","width":"48%","padding": "10px",'margin-left': '15px' },  
                )
            ]),
        dbc.Button("View", id="btn-senti"),
        html.Div([ 
            html.Div(id='bar-chart'),
            html.Div(id='senti-score'),
            html.Div(id='trend-chart'),

]),

])]
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-lg",
    )

def make_card(cusName,review,date,color,region,appVersion,rating,platf):
    return dbc.Card(
        [
            dbc.Row(
                [

                    dbc.Col(
                        dbc.CardBody(
                            [
                                # html.H5(cusName, className="card-title"),
                                html.H5(cusName, className="card-title"),
                                html.P(
                                    review,
                                    className="card-text",
                                ),
                                html.Div(
                                    dash_grocery.Stars(count=5, size=18, value=int(rating),edit=False)
                                ),
                                html.Small(
                                    date,
                                    className="card-text text-muted",
                                ),
                                html.Small(
                                    region,
                                    className="card-text text-muted",
                                    style={'padding': 10},
                                ),
                                html.Small(
                                    appVersion,
                                    className="card-text text-muted",
                                    style={'padding': 10},
                                ),
                                html.Small(
                                    platf,
                                    className="card-text text-muted",
                                    style={'padding': 10},
                                ),
                               
                            ]
                        ),
                    ),
                ],
            )

        ],
        className="shadow w-100 mb-3",
        color = color,
        outline = True,
    ) 

def date_string_to_date(date_string):
    return pd.to_datetime(date_string, infer_datetime_format=True)
def dataManage(locDf,country,version,platform,start_date,end_date,color):
    msg = []
    if not start_date and not country and not version and not platform:
        data = locDf
    if not start_date and country and version and platform:
        mask = locDf['Country'].isin(country) & locDf['Version'].isin(version) & locDf['Platform'].isin(platform)
        data = locDf.loc[mask]
    if not start_date and country and not version and not platform:
        mask = locDf['Country'].isin(country)
        data = locDf.loc[mask]
    if not start_date and not country and version and not platform:
        mask = locDf['Version'].isin(version)
        data = locDf.loc[mask]
    if not start_date and not country and not version and platform:
        mask = locDf['Platform'].isin(platform)
        data = locDf.loc[mask]
    if not start_date and country and version and not platform:
        mask = locDf['Country'].isin(country) & locDf['Version'].isin(version)
        data = locDf.loc[mask]
    if not start_date and country and not version and platform:
        mask = locDf['Country'].isin(country)& locDf['Platform'].isin(platform)
        data = locDf.loc[mask]
    if not start_date and not country and version and platform:
        mask = locDf['Version'].isin(version)& locDf['Platform'].isin(platform)
        data = locDf.loc[mask]
    if start_date and not country and not version and not platform:
        mask = ((date_string_to_date(locDf["Date"]) >= start_date) & (date_string_to_date(locDf["Date"]) <= end_date))
        data = locDf.loc[mask]
    if start_date and country and version and platform:
        mask = (((date_string_to_date(locDf["Date"]) >= start_date) & (date_string_to_date(locDf["Date"]) <= end_date)) & locDf['Country'].isin(country) & locDf['Version'].isin(version) & locDf['Platform'].isin(platform))
        data = locDf.loc[mask]
    if start_date and country and not version and not platform:
        mask = ((date_string_to_date(locDf["Date"]) >= start_date) & (date_string_to_date(locDf["Date"]) <= end_date)& locDf['Country'].isin(country))
        data = locDf.loc[mask]
    if start_date and not country and version and not platform:
        mask = ((date_string_to_date(locDf["Date"]) >= start_date) & (date_string_to_date(locDf["Date"]) <= end_date)& locDf['Version'].isin(version))
        data = locDf.loc[mask]
    if start_date and not country and not version and platform:
        mask = ((date_string_to_date(locDf["Date"]) >= start_date) & (date_string_to_date(locDf["Date"]) <= end_date)& locDf['Platform'].isin(platform))
        data = locDf.loc[mask]
    if start_date and country and version and not platform:
        mask = ((date_string_to_date(locDf["Date"]) >= start_date) & (date_string_to_date(locDf["Date"]) <= end_date)& locDf['Country'].isin(country)& locDf['Version'].isin(version))
        data = locDf.loc[mask]
    if start_date and country and not version and platform:
        mask = ((date_string_to_date(locDf["Date"]) >= start_date) & (date_string_to_date(locDf["Date"]) <= end_date)& locDf['Country'].isin(country)& locDf['Platform'].isin(platform))
        data = locDf.loc[mask]
    if start_date and not country and version and platform:
        mask = ((date_string_to_date(locDf["Date"]) >= start_date) & (date_string_to_date(locDf["Date"]) <= end_date)& locDf['Version'].isin(version)& locDf['Platform'].isin(platform))
        data = locDf.loc[mask]
    for index, row in data.iterrows():
        cusName = row["Name"]
        review = row["Review"]
        date = row["Date"]
        region = row["Country"]
        appVersion = row["Version"]
        rating = row["Rating"]
        platf = row["Platform"]
        msg.append(make_card(cusName,review,date,color,region,appVersion,rating,platf))
    return  msg  
@app.callback(
    Output('container-button-timestamp', 'children'),
    Input('btn-nclicks-1', 'n_clicks'),
    Input('btn-nclicks-2', 'n_clicks'),
    Input('btn-nclicks-3', 'n_clicks'),
    Input('country','value'),
    Input('version','value'),
    Input('platform','value'),
    Input('my-date-picker-range','start_date'),
    Input('my-date-picker-range','end_date')
)
def manage_cards(btn1, btn2, btn3,country,version,platform,start_date,end_date):
    if "btn-nclicks-1" == ctx.triggered_id:
        return dataManage(posDf,country,version,platform,start_date,end_date,"success")
    elif "btn-nclicks-2" == ctx.triggered_id:
        return dataManage(mixDf,country,version,platform,start_date,end_date,"warning")
    elif "btn-nclicks-3" == ctx.triggered_id:
        return dataManage(negDf,country,version,platform,start_date,end_date,"danger")
@app.callback(
    Output('home-Overall', 'children'),
    Input('btn-home', 'n_clicks'),
    Input('country','value'),
    Input('version','value'),
    Input('my-date-picker-range','start_date'),
    Input('my-date-picker-range','end_date')
)
def homeCard(btn1,country,version,start_date,end_date):
    msg = []
    if start_date and end_date:
        if "btn-home" == ctx.triggered_id:
            mask = ((date_string_to_date(df["Date"]) >= start_date) & (date_string_to_date(df["Date"]) <= end_date))
            data = df.loc[mask]
            posCount = data[data['sentiment'] == 'Positive'].shape[0]
            neuCount = data[data['sentiment'] == 'Neutral'].shape[0]
            negCount = data[data['sentiment'] == 'Negative'].shape[0]
            return html.Div([
                dbc.Card(
                    [ 
                        dbc.CardHeader("Over-All Selected-Range Report"),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.CardBody([
                                            html.H5("Reviews", className="card-title"),
                                            html.H1(data.shape[0]),
                                            html.P("for selected range",className="text-muted"),
                                        ]
                                        )
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        dbc.CardBody([
                                            html.H5("Avg Ratings", className="card-title"),
                                            dash_grocery.Stars(count=5, size=35, value=data['Rating'].median(),edit=False),
                                            # html.P("for selected range",className="text-muted")
                                        ]
                                        )
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        dbc.CardBody([
                                            html.H5("Sentiment Breakdown", className="card-title"),
                                            html.Br(),
                                            dbc.Progress(value=posCount,color="success"),
                                            html.P("Positive"),
                                            dbc.Progress(value=neuCount,color="warning"),
                                            html.P("Neutral"),
                                            dbc.Progress(value=negCount,color="danger"),
                                            html.P("Negative"),
                                        ]
                                        )
                                    ]
                                ),
                            ]
                        )
                        
                    ],
                    className="shadow-lg mb-3",
                color="dark", outline=True),
            ])
@app.callback(Output('bar-chart','children'),
        Output('senti-score','children'),
        Output('trend-chart','children'),
        Input('btn-senti','n_clicks'),
        Input('country','value'),
        Input('version','value'),
        Input('my-date-picker-range','start_date'),
        Input('my-date-picker-range','end_date'))
def sample_fun(btn,country,version,start_date,end_date):
    if start_date and end_date:
        if "btn-senti" == ctx.triggered_id:
            mask = ((date_string_to_date(df["Date"]) >= start_date) & (date_string_to_date(df["Date"]) <= end_date))
            data = df.loc[mask]
            posCount = data[data['sentiment'] == 'Positive'].shape[0]
            neuCount = data[data['sentiment'] == 'Neutral'].shape[0]
            negCount = data[data['sentiment'] == 'Negative'].shape[0]
            return [html.Div([
                dcc.Graph(
                    figure={
                        'data': [
                                go.Bar(
                            x = emerengy_df['sentiment'],
                            y = data['Version'].sort_values(ascending=False),

                            )
                            
                    ],
                        'layout': {
                            'title': 'Bar Chart',

                        },
                    }
),
                dcc.Graph(
                    figure={
                        'data': [
                                go.Pie(

                            values=data['Version'].value_counts(),
                            hole=.3,
                            labels=data['Version']
                            )
                            
                    ],
                        'layout': {
                            'title': 'Pie Chart',

                        },
                    },
                    config={
                        'displayModeBar': True,
                        'displaylogo': False,                                       
                        'modeBarButtonsToRemove': ['zoom2d', 'hoverCompareCartesian', 'hoverClosestCartesian', 'toggleSpikelines' ,]
                    },
),
            ]),
                html.Div([
  
            ]),
            html.Div([
                
            ]),
        ]
@app.callback(
    Output("time-series-chart", "figure"), 
    Input('my-date-picker-range','start_date'),
    Input('my-date-picker-range','end_date'))
def update_trend(start_date,end_date):
    mask = ((date_string_to_date(df["Date"]) >= start_date) & (date_string_to_date(df["Date"]) <= end_date))
    data = df.loc[mask]
    fig = px.line(data, x=data['Version'].sort_values(ascending=False).unique(), y=data['sentiment'].sort_values(ascending=False).unique())
    return fig
@app.callback(Output('version','options'),
            Input('my-date-picker-range','start_date'),
            Input('my-date-picker-range','end_date'),
            Input('version', "options"))
def updateOption(start_date, end_date,version):
    if not version:
        return ['4.22.0']
    mask = ((date_string_to_date(df["Date"]) >= start_date) & (date_string_to_date(df["Date"]) <= end_date))
    data = df.loc[mask]
    return [{'label': val, 'value': val} for val in data['Version'].sort_values(ascending=False).dropna().unique() if val != None]
def prepare_input(text_data):
    tokens = re.split("\W+", text_data)
    tokens_with_counts = Counter(tokens)
    return tokens_with_counts
token_with_counts = prepare_input(clean_text(df['Review'].values))
token_with_counts_pos = prepare_input(clean_text(pos_final['Review'].values))
token_with_counts_neg = prepare_input(clean_text(neg_final['Review'].values))
def word_for_wordclouds(n, data_val=token_with_counts_pos):
    tokens_wordcloud = [{"text": a, "value":b} for a, b in data_val.most_common(n)]
    return tokens_wordcloud
def word_for_wordclouds_neg(n, data_val=token_with_counts_neg):
    tokens_wordcloud = [{"text": a, "value":b} for a, b in data_val.most_common(n)]
    return tokens_wordcloud

@app.callback([Output('poswordcloud','words'),
        Output('poswordcloud', 'options')],
        Input('btn-senti','n_clicks'),
        Input('my-date-picker-range','start_date'),
        Input('my-date-picker-range','end_date')
        )
def makecloud(btn,start_date,end_date):
    if "btn-senti" == ctx.triggered_id:
        mask = ((date_string_to_date(pos_final["Date"]) >= start_date) & (date_string_to_date(pos_final["Date"]) <= end_date))
        data = pos_final.loc[mask]
        content_values = data['Review'].values
        content_cleaned = clean_text(content_values)
        text_data = prepare_input(content_cleaned)
        text = word_for_wordclouds(100)
        options = {
            'spiral': 'archimedean',
                    'scale': 'log',
                    'rotations': 2,
                    'rotationAngles': [-10, 60],
                    }
    return text, options
@app.callback([Output('negwordcloud','words'),
        Output('negwordcloud', 'options')],
        Input('btn-senti','n_clicks'),
        Input('my-date-picker-range','start_date'),
        Input('my-date-picker-range','end_date')
        )
def makenegcloud(btn,start_date,end_date):
    if "btn-senti" == ctx.triggered_id:
        mask = ((date_string_to_date(neg_final["Date"]) >= start_date) & (date_string_to_date(neg_final["Date"]) <= end_date))
        data = neg_final.loc[mask]
        content_values = data['Review'].values
        content_cleaned = clean_text(content_values)
        text_data = prepare_input(content_cleaned)
        text1 = word_for_wordclouds(100)
        options = { 
            'spiral': 'archimedean',
                    'scale': 'log',
                    'rotations': 2,
                    'rotationAngles': [-10, 60],
                    }
    return text1, options
# -------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(port=8099,use_reloader=False)
