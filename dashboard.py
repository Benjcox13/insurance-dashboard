import dash
import dash_core_components as dcc
import dash_html_components as dhc
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import math

df = pd.read_csv("Data.csv")
df = df.dropna()
df.drop(df[df['Credit Score'] > 1000 ].index , inplace=True)

df['Credit Score'] = df['Credit Score'].apply(lambda x: (int(math.ceil(x / 10.0)) * 10))
df['Licence Length'] = df['Licence Length'].apply(lambda x: (round(x * 2) / 2))


df["Transaction Date"] = pd.to_datetime(df["Transaction Date"], format="%d/%m/%Y")
df.sort_values("Transaction Date", inplace=True)

A_df = df.query("`Test Group` == 'A'")
B_df = df.query("`Test Group` == 'B'")

dataframes = {'+':df,'A':A_df,'B':B_df}




external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?family=Open+Sans&display=swap",
        "rel": "stylesheet",
    },
]


metric_list_y = ("Conversion","Total Price","Net Profit","Gross Profit")
metric_list_x = ("Customer Age","Credit Score","Vehicle Value","Vehicle Mileage","Licence Length")

def calculate_metrics(data,metric):
  
    counts = data[metric].value_counts()

    df2 = counts.to_frame().reset_index()

    df2.columns= [metric, 'Frequency']


    df2['Conversion'] = [sum(data['Sale Indicator'].loc[data[metric] == x[metric]])
        for _, x in df2.iterrows()]

    df2['Net Profit'] = [sum(data['Profit'].loc[data[metric] == y[metric]])
        for _, y in df2.iterrows()]

    df2['Gross Profit'] = [sum(data['Tax'].loc[data[metric] == z[metric]])
        for _, z in df2.iterrows()]

    df2['Gross Profit'] = df2['Net Profit']-df2['Gross Profit']

    df2['Total Price'] = [sum(data['Total Price'].loc[data[metric] == w[metric]])
        for _, w in df2.iterrows()]

    df2 = df2.sort_values(by=[metric])

    return df2


def build_card(title, data):
    return dbc.Card(
        dbc.CardBody(
            [
                dhc.H4(title, className="menu-title"),
                dhc.H2(data, className="indicator_value"),
            ]
        )
    )


def commas(number):
    return ("{:,}".format(number))



dashboard = dash.Dash(__name__,external_stylesheets=external_stylesheets)

server = dashboard.server

dashboard.title = "Insurance Dashboard Castestudy"



dashboard.layout = dhc.Div(
    children=[
         dhc.Div(
            children=[
                dhc.H1(children="Insurance Dashboard Casestudy", className="header-title"
                       ),
                    ],
                className="header",
            ),
         
            dhc.Div(
                children=[
                    dhc.Div(
                        children=[
                            dhc.Div(children="Test Group", className="menu-title"),
                            dcc.Dropdown(
                                id="group-selector",
                                options=[
                                    {'label': 'A', 'value':'A'},
                                    {'label': 'B', 'value':'B'},
                                    {'label': 'A AND B', 'value':'+'},
                                    {'label': 'A VS B', 'value':'v'}
                                    ],
                                value="A",
                                clearable=False,
                                searchable=False
                            ),
                        ]
                    ),
                    dhc.Div(
                        children=[
                            dhc.Div(
                                children="Date Range",
                                className="menu-title"
                                ),
                            dcc.DatePickerRange(
                                id="date-range",
                                min_date_allowed=df["Transaction Date"].min().date(),
                                max_date_allowed=df["Transaction Date"].max().date(),
                                start_date=df["Transaction Date"].min().date(),
                                end_date=df["Transaction Date"].max().date(),
                            ),
                        ]
                    ),
                ],
                className="menu",
                
            ),

         
            dhc.Div([
                    dbc.Row(
                        id="metrics",
                        justify="center",
                        )
                    ]),


            dhc.Div([
                dhc.Div(
                children=[
                    dhc.Div(
                        children=[
                            dhc.Div(children="X Variable", className="menu-title"),
                              dcc.Dropdown(
                                    id='xaxis-column',
                                    options=[{'label': i, 'value': i} for i in metric_list_x],
                                    value='Customer Age',
                                    clearable=False,
                                    searchable=False,
                                    
                                ),
                        ],
                    ),
                    dhc.Div(
                        children=[
                            dhc.Div(
                                children="Y Variable",
                                className="menu-title"
                                ),
                            dcc.Dropdown(
                                id='yaxis-column',
                                options=[{'label': i, 'value': i} for i in metric_list_y],
                                value='Conversion',
                                clearable=False,
                                searchable=False,
                                
                                
                            ),
                        ],
                    ),
                      
                ],
                
                )
            ]),

            dhc.Div(
            children=[
                dhc.Div(
                    children=dcc.Graph(
                        id='metrics-graph', config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
         
           
              
        ]
)



@dashboard.callback(
    Output("metrics-graph", "figure"),
    [
        Input("group-selector", "value"),
        Input('xaxis-column', 'value'),
        Input('yaxis-column', 'value'),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)

def update_charts(test_group,xaxis,yaxis, start_date, end_date):

    if (test_group != "v"):
        data = dataframes[test_group]
        mask = (
                (data["Transaction Date"] >= start_date)
                & (data["Transaction Date"] <= end_date)
            )
        filtered_data = data.loc[mask, :]
        
        overall_metrics = calculate_metrics(filtered_data,xaxis)
        
        fig = px.scatter(x=overall_metrics[xaxis],
                     y=overall_metrics[yaxis]
        )

        fig.update_layout(
            title=(xaxis +" vs " +yaxis),
            xaxis_title=xaxis,
            yaxis_title=yaxis,
        )


        return fig

    else:
        data_A = A_df
        data_B = B_df
        mask = (
                (data_A["Transaction Date"] >= start_date)
                & (data_A["Transaction Date"] <= end_date)
            )
        
        filtered_data_A = data_A.loc[mask, :]

        mask =(
        (data_B["Transaction Date"] >= start_date)
        & (data_B["Transaction Date"] <= end_date)
        )
        
        filtered_data_B = data_B.loc[mask, :]


        A_metrics = calculate_metrics(filtered_data_A,xaxis)

        B_metrics = calculate_metrics(filtered_data_B,xaxis)

        fig = make_subplots(rows=1, cols=1)

        fig.append_trace(go.Scatter(x=A_metrics[xaxis],y=A_metrics[yaxis],name="A"),row=1,col=1)
                         

        fig.append_trace(go.Scatter(x=B_metrics[xaxis],y=B_metrics[yaxis],name="B"),row=1,col=1)
                         

        fig.update_layout(
            title=(xaxis +" vs " +yaxis),
            xaxis_title=xaxis,
            yaxis_title=yaxis,
        )


        return fig


@dashboard.callback(
    Output("metrics", "children"),
    [
        Input("group-selector", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)

def update_metrics(test_group, start_date, end_date):
    test_group = str(test_group[0])
    if (test_group == 'v'):
        data_A = A_df
        data_B = B_df
        mask = (
                (data_A["Transaction Date"] >= start_date)
                & (data_A["Transaction Date"] <= end_date)
            )
        filtered_data_A = data_A.loc[mask, :]

        conversion = (filtered_data_A['Sale Indicator'].sum()/len(filtered_data_A))

        total_price = filtered_data_A['Total Price'].sum()

        net_profit = filtered_data_A['Profit'].sum()

        gross_profit= filtered_data_A['Profit'].sum()-filtered_data_A['Tax'].sum()


        row_A = [
                dbc.Col(build_card("A Conversion",commas(round(conversion,3))),width=3),
                dbc.Col(build_card("A Total Price",commas(round(total_price,2))),width=3),
                dbc.Col(build_card("A Net Profit",commas(round(net_profit,2))),width=3),
                dbc.Col(build_card("A Gross Profit",commas(round(gross_profit,2))),width=3)
                ]


        mask = (
        (data_B["Transaction Date"] >= start_date)
        & (data_B["Transaction Date"] <= end_date)
        )
        
        filtered_data_B = data_B.loc[mask, :]

        conversion = (filtered_data_B['Sale Indicator'].sum()/len(filtered_data_B))

        total_price = filtered_data_B['Total Price'].sum()

        net_profit = filtered_data_B['Profit'].sum()

        gross_profit= filtered_data_B['Profit'].sum()-filtered_data_B['Tax'].sum()

        row_B = [
                dbc.Col(build_card("B Conversion",commas(round(conversion,3))),width=3),
                dbc.Col(build_card("B Total Price",commas(round(total_price,2))),width=3),
                dbc.Col(build_card("B Net Profit",commas(round(net_profit,2))),width=3),
                dbc.Col(build_card("B Gross Profit",commas(round(gross_profit,2))),width=3)
]
            

        


        return (row_A + row_B)

    else:
        data = dataframes[test_group]
        mask = (
                (data["Transaction Date"] >= start_date)
                & (data["Transaction Date"] <= end_date)
            )
        filtered_data = data.loc[mask, :]

        conversion = (filtered_data['Sale Indicator'].sum()/len(filtered_data))

        total_price = filtered_data['Total Price'].sum()

        net_profit = filtered_data['Profit'].sum()

        gross_profit= filtered_data['Profit'].sum()-filtered_data['Tax'].sum()

        row_A = [
            dbc.Col(build_card("Conversion",commas(round(conversion,3))),width=3),
            dbc.Col(build_card("Total Price",commas(round(total_price,2))),width=3),
            dbc.Col(build_card("Net Profit",commas(round(net_profit,2))),width=3),
            dbc.Col(build_card("Gross Profit",commas(round(gross_profit,2))),width=3)
        ]
        
        


        return row_A
        

    
    

if __name__ == "__main__":
    dashboard.run_server(debug=True,threaded=True)
