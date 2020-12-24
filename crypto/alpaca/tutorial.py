import alpaca_trade_api as tradeapi
import threading

##-- GENERAL SETUP --##

# authentication and connection details
api_key = 'PKBOCUTMKK8CT3RTW1PS'
api_secret = 'cMxwROnk8LAcirjVzEmYihpX6PGg1qRcqDZLLYbf'
base_url = 'https://paper-api.alpaca.markets'

# instantiate REST API
api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')

# obtain account information
account = api.get_account()
#print(account)

# get historical data from in-house source with different intervals
aapl = api.get_barset('AAPL', 'day')
tsla = api.get_barset('TSLA', '15Min')
#print(aapl.df)
#print(aapl._raw)

# increase the limit (default 100)
aapl = api.get_barset('AAPL', '1D', limit=1000)

##-- WEBSOCKETS --##

conn = tradeapi.stream2.StreamConn(api_key, api_secret, base_url)

@conn.on(r'^account_updates$')
async def on_account_updates(conn, channel, account):
    print('account', account)

@conn.on(r'^trade_updates$')
async def on_trade_updates(conn, channel, trade):
    print('trade', trade)

# additional parameters for price data
ws_url = 'wss://data.alpaca.markets'
conn   = tradeapi.stream2.StreamConn(api_key, api_secret, base_url=base_url, data_url=ws_url, data_stream='alpacadatav1')

# example of three types of data we can request from the WebSocket

# trade data
@conn.on(r'^T.AAPL$')
async def trade_info(conn, channel, bar):
    print('bars', bar)
    print(bar._raw)

# quote info
@conn.on(r'^Q.AAPL$')
async def quote_info(conn, channel, bar):
    print('bars', bar)

# one-minute bar data
@conn.on(r'^AM.AAPL$')
async def one_minute_bars(conn, channel, bar):
    print('bars', bar)

# start WebSocket in a thread
def ws_start():
    # request the data streams
    conn.run(['account_updates', 'trade_updates'])#, 'AM.AAPL'])

ws_thread = threading.Thread(target=ws_start, daemon=True)
ws_thread.start()

##-- INDICATORS --##

# calculate moving average with rolling size of 20
mving_avg_20 = aapl.df.AAPL.close.rolling(20).mean()
std_dev      = aapl.df.AAPL.close.rolling(20).std()

# TIP: Pandas TA library offer 120+ indicators

##-- ORDERING --##

# send an order to buy one share of TSLA at a $400.00 limit
#api.submit_order(symbol='TSLA', qty=1, side='buy', time_in_force='gtc', type='limit', limit_price=400.00, client_order_id='002')
#position = api.get_position('TSLA')
#position = api.get_order_by_client_order_id('001')

# send the same order but as a 'market' order
#api.submit_order(symbol='TSLA', qty=1, side='buy', time_in_force='gtc', type='market')
#position = api.get_position('TSLA')

# set a stop loss or take profit
#api.submit_order(symbol='TSLA', qty=1, side='buy', time_in_force='gtc', type='limit', limit_price=650.00, order_class='bracket', stop_loss=dict(stop_price='600.00'), take_profit=dict(limit_price='675.00'))

#print(api.get_clock())

while True:
    pass