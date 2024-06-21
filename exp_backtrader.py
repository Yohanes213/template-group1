from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

import matplotlib
matplotlib.use('TkAgg')

from kafka import KafkaConsumer, KafkaProducer
import json
from backend import Backtest
import mlflow
import mlflow.pyfunc
mlflow.set_tracking_uri("http://localhost:5001")



# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('shortperiod', 15),
        ('longperiod', 200),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))


    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.smashort = bt.indicators.SimpleMovingAverage(self.datas[0], period = self.params.shortperiod)
        self.smalong = bt.indicators.SimpleMovingAverage(self.datas[0], period = self.params.longperiod)

    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('Buy Executed, Price: %.2f, Cost: %.2f, Comm: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

            
            else:
                self.log('Sell Executed, Price: %.2f, Cost: %.2f, Comm: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Cancled/margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        
        self.log('Operation PROFIT , GROSS %.2f, NET %.2f'%
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Log the closing price
        self.log('Close, %.2f' % self.dataclose[0])
        
        # Check if an order is pending, if yes, we cannot send a second one
        if self.order:
            return
        
        # Buy on the first day
        if not self.position:
            if self.smashort[0] > self.smalong[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.log('smashort %s' % self.smashort[0])
                self.log('smalong %s' % self.smalong[0])
                self.order = self.buy()
            
        else:
            if self.smashort[0] < self.smalong[0]:
                    self.log('Sell CREATE, %.2f' % self.dataclose[0])
                    self.order = self.sell()



if __name__ == '__main__':
    # Create a cerebro entity

    with open('sample.json', 'r') as f:
        file = json.load(f)

    start_date = datetime.datetime.strptime(file['start_date'], '%Y-%m-%d')
    end_date = datetime.datetime.strptime(file['end_date'], '%Y-%m-%d')
    
    print(file)
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    datapath = 'data/BTC-USD.csv'

    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        #fromdate=datetime.datetime(2023 , 6, 18),
        #dtformat = '%Y-%m-%d',
        fromdate=start_date,
        # Do not pass values before this date
        #todate=datetime.datetime(2024, 6, 18),
        todate=end_date,
        # Do not pass values after this date
        reverse=False)

    cerebro.adddata(data)
    cerebro.broker.setcash(100000)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    cerebro.broker.setcommission(commission=0.0)

    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharperatio')

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    strategies = cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Extract metrics
    strategy = strategies[0]
    trade_analyzer = strategy.analyzers.tradeanalyzer.get_analysis()
    drawdown = strategy.analyzers.drawdown.get_analysis()
    sharpe_ratio = strategy.analyzers.sharperatio.get_analysis()


    metrics = {
        #'number_of_trades': trade_analyzer.total.closed,
        #'winning_trades': trade_analyzer.won.total,
        #'losing_trades': trade_analyzer.lost.total,
        'max_drawdown': drawdown.max.drawdown,
        'sharpe_ratio': sharpe_ratio['sharperatio']
    }

    #values = {"Startegy": "BTC", "Start date": "2023-06-18", "End date": "2024-06-18"}

    with mlflow.start_run():
        mlflow.log_param('Start Date', file['start_date'])
        mlflow.log_param('End Date', file['end_date'])
        mlflow.log_param('Strategy', file['strategy'])
        mlflow.log_metric('max_drawdown', metrics['max_drawdown'])
        #mlflow.log_metric('Sharpe Ratio', metrics['sharpe_ratio'])

    
    # Send metrics to Kafka
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    producer.send('metrics', json.dumps(metrics).encode('utf-8'))
    producer.flush()

    # Print metrics
    print(metrics)

    # Plot the result
    #cerebro.plot()