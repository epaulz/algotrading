## EXAMPLE OF A SIMPLE 'BREAKOUT' TRADING SYSTEM WITH ALPACA ##

import logging
from time import sleep

import alpaca_trade_api as tradeapi
import pandas as pd

# init
logging.basicConfig(filename='errlog.log', level=logging.WARNING, format='%(asctime)s:%(levelname)s:%(message)s',)

api_key    = 'PKGVS7BNOPEV3OOP2ZAG'
api_secret = 'atr83WReTtd1dTLeCwUZMSVWAKode6UURcGSOD4i'
base_url   = 'https://paper-api.alpaca.markets'
data_url   = 'wss://data.alpaca.markets'

# instantiate REST API
api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')

# init WebSocket
conn = tradeapi.stream2.StreamConn(api_key, api_secret, base_url=base_url, data_url=data_url, data_stream='alpacadatav1')

# return seconds until market close
def time_to_market_close():
    clock = api.get_clock()
    return (clock.next_close - clock.timestamp).total_seconds()

# sleep until market opens
def wait_for_market_open():
    clock = api.get_clock()
    if not clock.is_open:
        time_to_open = (clock.next_open - clock.timestamp).total_seconds()
        sleep(round(time_to_open))

# parameters to determine our trade entries
def set_trade_params(df):
    return {
        'high': df.high.tail(10).max(),
        'low': df.low.tail(10).min(),
        'trade_taken': False,
    }

# send an order once we've established an entry
def send_order(direction, bar):
    if time_to_market_close() > 120:
        print(f'send {direction} trade')
        range_size = trade_params['high'] - trade_params['low']

        if direction == 'buy':
            sl = bar.high - range_size
            tp = bar.high + range_size
        elif direction == 'sell':
            sl = bar.low + range_size
            tp = bar.low - range_size

        api.submit_order(symbol='AAPL', qty=10, side=direction, type='market', time_in_force='day', order_class='bracket', stop_loss=dict(stop_price=str(sl)), take_profit=dict(limit_price=str(tp)),)

        return True
    
    wait_for_market_open()
    return False

# code to execute everytime the WebSocket pushes a new one-minute bar
@conn.on(r'^AM.AAPL$')
async def one_minute_bars(conn, channel, bar):
    if isinstance(candlesticks.df, pd.DataFrame):
        ts = pd.to_datetime(bar.timestamp, unit='ms')
        candlesticks.df.loc[ts] = [bar.open, bar.high, bar.low, bar.close, bar.volume]
    
    if not trade_params['trade_taken']:
        if bar.high > trade_params['high']:
            trade_params['trade_taken'] = send_order('buy', bar)
        elif bar.low < trade_params['low']:
            trade_params['trade_taken'] = send_order('sell', bar)

    if time_to_market_close() > 120:
        wait_for_market_open()

# handle any trade updates from the WebSocket
@conn.on(r'^trade_updates$')
async def on_trade_updates(conn, channel, trade):
    if trade.order['order_type'] != 'market' and trade.order['filled_qty'] == 10:
        # trade closed - look for new trade
        trade_params = set_trade_params(candlesticks.df.AAPL)

# main script would start here
candlesticks = api.get_barset('AAPL', 'minute', limit=10)
trade_params = set_trade_params(candlesticks.df.AAPL)

conn.run(['AM.AAPL', 'trade_updates'])