
import base64
from cProfile import label
import datetime
from enum import unique
from IPython.display import HTML
from importlib_metadata import method_cache
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import pandas as pd
import json
import requests
import math
import csv
from empyrial import empyrial, Engine, get_report, get_returns_from_data,get_returns
import numpy as np
import quantstats as qs
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine,Integer
from flask import Flask, jsonify, redirect, render_template, render_template_string, request,Response,url_for
import io


app=Flask(__name__)
DIALCT = "mysql"
DRIVER = "pymysql"
USERNAME = "root"
PASSWORD = "199312wmq"
HOST = "127.0.0.1"
PORT = "3306"
DATABASE = "Stock"
DB_URI="{}+{}://{}:{}@{}:{}/{}".format(DIALCT,DRIVER,USERNAME,PASSWORD,HOST,PORT,DATABASE)
app.config['SQLALCHEMY_DATABASE_URI']=DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True

db=SQLAlchemy(app)

class Portfolio(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    ticker_1=db.Column(db.String(10),nullable=False)
    ticker_2=db.Column(db.String(10),nullable=False)
    ticker_3=db.Column(db.String(10),nullable=False)
    diversity=db.Column(db.String(20),nullable=False)
    start_date=db.Column(db.DateTime,nullable=False)
    portfolio_name=db.Column(db.String(30),nullable=False,unique=True)
    Annual_return=db.Column(db.String(30),nullable=False)
    Cumulative_return=db.Column(db.String(30),nullable=False)
    Annual_volatility=db.Column(db.String(30),nullable=False)
    Winning_day_ratio=db.Column(db.String(30),nullable=False)
    Sharpe_ratio=db.Column(db.String(30),nullable=False)
    Calmar_ratio=db.Column(db.String(30),nullable=False)
    Information_ratio=db.Column(db.String(30),nullable=False)
    Stability=db.Column(db.String(30),nullable=False)
    Max_Drawdown=db.Column(db.String(30),nullable=False)
    Sortino_ratio=db.Column(db.String(30),nullable=False)
    Skew=db.Column(db.String(30),nullable=False)
    Kurtosis=db.Column(db.String(30),nullable=False)
    Tail_Ratio=db.Column(db.String(30),nullable=False)
    Common_sense_ratio=db.Column(db.String(30),nullable=False)
    Daily_value_at_risk=db.Column(db.String(30),nullable=False)
    Alpha=db.Column(db.String(30),nullable=False)
    Beta=db.Column(db.String(30),nullable=False)

db.create_all()

api_key = "3ZGSDZGITRAO2JWA"
data_stock = []
meta_info_stock = []
df_stock = []
daily_std_stock = []
daily_volatility_stock = []
monthly_volatility_stock = []

def get_ticker_symbol_list():
    match_symbols = []
    with open('nasdaq-listed-symbols_csv.csv', newline='') as csvfile:
        symbol_data = csv.DictReader(csvfile)
        for symbol in symbol_data:
            match_symbols.append(symbol['Symbol'])
    return  match_symbols

def get_daily_stock(stock_sym,api_key):
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + stock_sym + '&apikey=' + api_key
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        return data
    else:
        return jsonify({'error':"Cannot find daily stock values for !" + stock_sym})


def get_normalized_json(data):

    stock_dates = data['Time Series (Daily)'].keys()
    stock_open = []
    stock_close = []
    stock_high = []
    stock_low = []

    for dt in stock_dates:
        stock_open.append(data['Time Series (Daily)'][dt]['1. open'])
        stock_close.append(data['Time Series (Daily)'][dt]['4. close'])
        stock_high.append(data['Time Series (Daily)'][dt]['2. high'])
        stock_low.append(data['Time Series (Daily)'][dt]['3. low'])

    df = pd.json_normalize(data, max_level=2)
    df = pd.DataFrame(
        {'Date': stock_dates, 'stock_open': stock_open, 'stock_close': stock_close, 'stock_high': stock_high,
         'stock_low': stock_low})
    df.index = df['Date']
    stock_close_data = df['stock_close'].astype(float)
    stock_open_data = df['stock_open'].astype(float)
    df['returns'] = (stock_close_data - stock_open_data) / stock_open_data * 100
    df['30_EWM'] = df['returns'].ewm(span=30, adjust=False).mean()
    return df

def get_volatility(tickers):
    i=0

    for ticker in tickers:
        data_stock.append(get_daily_stock(ticker, '3ZGSDZGITRAO2JWA'))
        meta_info_stock.append(list(data_stock[i].values())[0])

        df_stock.append(get_normalized_json(data_stock[i]))
        daily_volatility_stock.append(df_stock[i]['returns'].std())
        monthly_volatility_stock.append(daily_volatility_stock[i] * math.sqrt(21))
        i+=1
    return  data_stock, meta_info_stock ,df_stock , daily_volatility_stock ,monthly_volatility_stock



@app.route('/')
def index():
    portfolio=Portfolio.query.all()
    return render_template('stock_home.html',tickets=get_ticker_symbol_list(),portfolio=portfolio)

# @app.route('/post/', methods=['post'])
@app.route('/portfolio/',methods=['post'])
def post():
    global api_key
    tk1=request.form.get('ticket1')
    tk2=request.form.get('ticket2')
    tk3=request.form.get('ticket3')
    diversity=request.form.get('portfolio')
    start_date=request.form.get('date')
    user_id=request.form.get('user') 
    portfolio_name=request.form.get('portfolio_name')

    tickers = [tk1, tk2, tk3]
    if tk1!=tk2 and tk2!=tk3 and tk1!=tk3:
        if diversity=='Do not diveristy':
            tickers_portfolio = Engine(start_date=start_date, portfolio=tickers, weights=[0.3, 0.3, 0.3],benchmark=["SPY"],rebalance='1y')
            get_report(tickers_portfolio)

        elif diversity=="Medium diveristy":
            tickers_portfolio = Engine(start_date=start_date, portfolio=tickers, weights=[0.3, 0.3, 0.3],benchmark=["SPY"],rebalance='1y')
            get_report(tickers_portfolio)
        elif diversity=='Optimize':
            tickers_portfolio = Engine(start_date=start_date, portfolio=tickers, weights=[0.3, 0.3, 0.3],benchmark=["SPY"],rebalance='1y')
            get_report(tickers_portfolio)
        else:
            tickers_portfolio = Engine(start_date=start_date, portfolio=tickers, weights=[0.3, 0.3, 0.3],benchmark=["SPY"],rebalance='1y')
            get_report(tickers_portfolio)

    else:
        return jsonify({'Error':'Please select three different tickers'})
      
    dict_new =eval(json.dumps(empyrial.df))
    data_key=dict_new['']
    data_value=dict_new['Backtest']
    Backtest=dict(zip(data_key,data_value))

    if request.form.get('Save portfolio')=='Save portfolio':

        portfolio=Portfolio(id=user_id,ticker_1=tk1,
        ticker_2=tk2,ticker_3=tk3,diversity=diversity,start_date=start_date,portfolio_name=portfolio_name,
        Annual_return=Backtest['Annual return'],Cumulative_return=Backtest['Cumulative return'],
        Annual_volatility=Backtest['Annual volatility'],Winning_day_ratio=Backtest['Winning day ratio'],
        Sharpe_ratio=Backtest['Sharpe ratio'],Calmar_ratio=Backtest['Calmar ratio'],Information_ratio=Backtest['Information ratio'],
        Stability=Backtest['Stability'],Max_Drawdown=Backtest['Max Drawdown'],Sortino_ratio=Backtest['Sortino ratio'],
        Skew=Backtest['Skew'],Kurtosis=Backtest['Kurtosis'],Tail_Ratio=Backtest['Tail Ratio'],
        Common_sense_ratio=Backtest['Common sense ratio'],Daily_value_at_risk=Backtest['Daily value at risk'],
        Alpha=Backtest['Alpha'],Beta=Backtest['Beta'])
        db.session.add(portfolio)
        db.session.commit()

        return redirect('/')

    elif request.form.get('search details')=='search details':

        return jsonify({'Showing portfolio analysis for :{0} {1} and {2}'.format(tk1,tk2,tk3):Backtest})


@app.route('/all_portfolio/', methods=['get'])
def get(): 
    portfolio=Portfolio.query.all()
    if len(portfolio)==0:
        return jsonify({'Error':'No any existing portfolio at this moment'})
    else:
        return render_template('all_portfolio.html',portfolio=portfolio)


@app.route('/all_portfolio/<folioname>/',methods=['delete','get'])
def delete(folioname):

    Portfolio.query.filter_by(portfolio_name=folioname).delete()
    db.session.commit()
    return redirect(url_for('get'))

@app.route('/<folioname>/<diversity>/',methods=['put','get'])
def change_diversity(folioname,diversity):
    datasets=Portfolio.query.filter_by(portfolio_name=folioname).first()
    datasets.diversity=diversity
    if datasets.diversity=='Do not diveristy':
        tickers_portfolio = Engine(start_date=datasets.start_date.strftime("%Y-%m-%d"), portfolio=[datasets.ticker_1,datasets.ticker_2,datasets.ticker_3], weights=[0.3, 0.3, 0.3],benchmark=["SPY"],rebalance='1y')
        get_report(tickers_portfolio)

    elif datasets.diversity=="Medium diveristy":
        tickers_portfolio = Engine(start_date=datasets.start_date.strftime("%Y-%m-%d"), portfolio=[datasets.ticker_1,datasets.ticker_2,datasets.ticker_3], weights=[0.3, 0.3, 0.3],benchmark=["SPY"],rebalance='1y')
        get_report(tickers_portfolio)
    elif datasets.diversity=='Optimize':
        tickers_portfolio = Engine(start_date=datasets.start_date.strftime("%Y-%m-%d"), portfolio=[datasets.ticker_1,datasets.ticker_2,datasets.ticker_3], weights=[0.3, 0.3, 0.3],benchmark=["SPY"],rebalance='1y')
        get_report(tickers_portfolio)
    else:
        tickers_portfolio = Engine(start_date=datasets.start_date.strftime("%Y-%m-%d"), portfolio=[datasets.ticker_1,datasets.ticker_2,datasets.ticker_3], weights=[0.3, 0.3, 0.3],benchmark=["SPY"],rebalance='1y')
        get_report(tickers_portfolio)
        
    dict_new =eval(json.dumps(empyrial.df))
    data_key=dict_new['']
    data_value=dict_new['Backtest']
    Backtest=dict(zip(data_key,data_value))

    datasets.Annual_return=Backtest['Annual return']
    datasets.Cumulative_return=Backtest['Cumulative return']
    datasets.Annual_volatility=Backtest['Annual volatility']
    datasets.Winning_day_ratio=Backtest['Winning day ratio']
    datasets.Sharpe_ratio=Backtest['Sharpe ratio']
    datasets.Calmar_ratio=Backtest['Calmar ratio']
    datasets.Information_ratio=Backtest['Information ratio']
    datasets.Stability=Backtest['Stability']
    datasets.Max_Drawdown=Backtest['Max Drawdown']
    datasets.Sortino_ratio=Backtest['Sortino ratio']
    datasets.Skew=Backtest['Skew'],
    datasets.Kurtosis=Backtest['Kurtosis']
    datasets.Tail_Ratio=Backtest['Tail Ratio']
    datasets.Common_sense_ratio=Backtest['Common sense ratio']
    datasets.Daily_value_at_risk=Backtest['Daily value at risk']
    datasets.Alpha=Backtest['Alpha']
    datasets.Beta=Backtest['Beta']

    db.session.commit()

    return redirect(url_for('get'))


if __name__=="__main__":
    app.run(debug=True)

