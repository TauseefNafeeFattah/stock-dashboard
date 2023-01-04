import dash
from dash import dcc,html, Input, Output, State
from datetime import datetime as dt
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

from model import prediction
app = dash.Dash(__name__)

server = app.server

app.layout = html.Div([html.Div(
    [
        html.H1("Welcome to Stock Dash!", className="start"),
        html.Div([html.Div([dcc.Input(type="text", placeholder="Stock Code", id="stockCodeInput"),html.Button('Submit', id='stockCodeSubmitButton', n_clicks=0)], className="codeInput"),
        html.Div([dcc.DatePickerRange(id='date-picker-range')], className="datePicker"),
        html.Div([html.Button('Stock Price', id='stockPrice',n_clicks=0), html.Button('Indicators', id='indicators',n_clicks=0)], className="effectButton"),
        html.Div([dcc.Input(type="number", min=0,placeholder="Number of days", id="daysNumber"), html.Button('Forcast', id='forcast', n_clicks=0)], className="forcastDiv")], className="navcenter")

    ],
    className="nav"
), html.Div([
    html.Div([], id="companyInfo"),
    html.Div([], id="stock-price-content"),
    html.Div([], id="indicator-plot-content"),
    html.Div([], id="forcast-content")
], className="content")], className="container")

@app.callback(
    Output('companyInfo', 'children'),
    Input('stockCodeSubmitButton', 'n_clicks'),
    State('stockCodeInput', 'value')
)
def update_company_info_div(n_clicks,stock_code):
    if stock_code != None:
        try:
            ticker = yf.Ticker(stock_code)
            inf = ticker.info
            businessSummary = inf["longBusinessSummary"]
            logo_url = inf["logo_url"]
            name = inf["shortName"]
            return html.Div([
                html.Div([
                    html.Img(src=logo_url),
                    html.H1(name,className="companyName")
                ], className="header"),
                html.P(businessSummary, id="description", className="decription_ticker")
            ])
        except:
            return html.P("Please Enter a valid Stock Code")

@app.callback(
    Output('stock-price-content', 'children'),
    Input('stockPrice', 'n_clicks'),
    State('stockCodeInput', 'value'),
    State('date-picker-range', 'start_date'),
    State('date-picker-range', 'end_date')
)
def update_stock_price_graph_div(n_clicks,stock_code,start_date, end_date):
    if n_clicks != 0: 
        if stock_code== None:
            return html.P("Please Enter a valid Stock Code")
        else:
            if start_date != None:
                if end_date == None or end_date < start_date:
                    end_date=start_date
                df = yf.download(tickers=stock_code,start=str(start_date), end=str(end_date))
            else:
                df = yf.download(stock_code)
                
            df.reset_index(inplace=True)
            fig = get_stock_price_fig(df)
            
            return [dcc.Graph(figure=fig)]

@app.callback(
    Output('indicator-plot-content', 'children'),
    Input('indicators', 'n_clicks'),
    State('stockCodeInput', 'value'),
    State('date-picker-range', 'start_date'),
    State('date-picker-range', 'end_date')
)
def update_indicators_graph_div(n_clicks,stock_code,start_date, end_date):
    if n_clicks != 0: 
        if stock_code== None:
            return html.P("Please Enter a valid Stock Code")
        else:
            if start_date != None:
                if end_date == None or end_date < start_date:
                    end_date=start_date
                df = yf.download(tickers=stock_code,start=str(start_date), end=str(end_date))
            else:
                df = yf.download(stock_code)
                
            df.reset_index(inplace=True)
            fig = get_indicators_fig(df)
            
            return [dcc.Graph(figure=fig)]
@app.callback(
    Output('forcast-content', 'children'),
    Input('forcast', 'n_clicks'),
    State('stockCodeInput', 'value'),
    State('daysNumber', 'value'),   
)
def forcast(n_clicks, stock_code, n_days):
    if n_clicks != 0:
        if stock_code== None:
            return html.P("Please Enter a valid Stock Code")
        
        fig = prediction(stock_code, int(n_days)+1)
        return [dcc.Graph(figure=fig)]

def get_stock_price_fig(df):
    fig = px.line(df,
            x="Date",
            y=["Close", "Open"],
            title="Closing and Openning Price vs Date")
    return fig

def get_indicators_fig(df):
    df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    fig = px.scatter(df,
                     x="Date",
                     y="EWA_20",
                     title="Exponential Moving Average vs Date")
    
    fig.update_traces(mode='lines+markers')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)