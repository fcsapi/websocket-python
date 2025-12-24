"""
FCS Real-time Stock Example - Backend

Pure Python WebSocket client for real-time stock prices.
No browser required - runs directly in terminal.

Install: pip install websocket-client
Run: python stock_example.py
"""

import sys
import os

# Add parent directory to path for import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fcs_client_lib import FCSClient

# Configuration
API_KEY = 'fcs_socket_demo'  # Replace with your API key
SYMBOLS = ['NASDAQ:AAPL', 'NASDAQ:GOOGL', 'NASDAQ:MSFT', 'NYSE:TSLA']
TIMEFRAME = '1D'

# Create client
client = FCSClient(API_KEY)

# Store prices
prices = {}


@client.on_connected
def on_connected():
    print('\n' + '=' * 60)
    print('  FCS Real-time Stock Prices - Backend Example')
    print('=' * 60)
    print(f'  API Key: {API_KEY}')
    print(f'  Symbols: {", ".join(SYMBOLS)}')
    print(f'  Timeframe: {TIMEFRAME}')
    print('=' * 60 + '\n')

    # Subscribe to symbols
    for symbol in SYMBOLS:
        client.join(symbol, TIMEFRAME)


@client.on_message
def on_message(data):
    if data.get('type') == 'price' and data.get('prices'):
        symbol = data.get('symbol', '')
        p = data['prices']
        mode = p.get('mode', '')

        if mode in ['initial', 'candle']:
            prices[symbol] = {
                'open': p.get('o'),
                'high': p.get('h'),
                'low': p.get('l'),
                'close': p.get('c'),
                'volume': p.get('v'),
                'ask': p.get('a'),
                'bid': p.get('b')
            }
            print_price(symbol, prices[symbol])

        elif mode == 'askbid':
            if symbol in prices:
                prices[symbol]['ask'] = p.get('a')
                prices[symbol]['bid'] = p.get('b')
                prices[symbol]['close'] = p.get('c')
            print(f"  {symbol}: Ask=${p.get('a')} Bid=${p.get('b')}")


def print_price(symbol, p):
    """Pretty print stock price data."""
    parts = symbol.split(':')
    exchange = parts[0] if len(parts) > 1 else ''
    ticker = parts[1] if len(parts) > 1 else symbol

    print(f"\n  [{ticker}] ({exchange})")
    print(f"    Price: ${p['close']}")
    print(f"    O: ${p['open']} | H: ${p['high']} | L: ${p['low']} | C: ${p['close']}")
    if p.get('volume'):
        vol = format_volume(p['volume'])
        print(f"    Volume: {vol}")
    if p.get('ask') and p.get('bid'):
        print(f"    Ask: ${p['ask']} | Bid: ${p['bid']}")


def format_volume(vol):
    """Format volume with K/M suffix."""
    try:
        v = float(vol)
        if v >= 1000000:
            return f"{v/1000000:.2f}M"
        elif v >= 1000:
            return f"{v/1000:.2f}K"
        return f"{v:.0f}"
    except:
        return str(vol)


@client.on_close
def on_close(code, msg):
    print(f'\n[!] Connection closed: {code} - {msg}')


@client.on_error
def on_error(error):
    print(f'\n[!] Error: {error}')


if __name__ == '__main__':
    print('\nConnecting to FCS WebSocket...')
    print('Press Ctrl+C to stop\n')

    try:
        client.connect()
        client.run_forever()
    except KeyboardInterrupt:
        print('\n\nDisconnecting...')
        client.disconnect()
        print('Goodbye!')
