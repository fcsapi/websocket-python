"""
FCS Real-time Forex Example - Backend

Pure Python WebSocket client for real-time forex prices.
No browser required - runs directly in terminal.

Install: pip install websocket-client
Run: python forex_example.py
"""

import sys
import os

# Add parent directory to path for import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fcs_client_lib import FCSClient

# Configuration
API_KEY = 'fcs_socket_demo'  # Replace with your API key
SYMBOLS = ['FX:EURUSD', 'FX:GBPUSD', 'FX:USDJPY', 'FX:AUDUSD']
TIMEFRAME = '1D'

# Create client
client = FCSClient(API_KEY)

# Store prices
prices = {}


@client.on_connected
def on_connected():
    print('\n' + '=' * 60)
    print('  FCS Real-time Forex Prices - Backend Example')
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
                'ask': p.get('a'),
                'bid': p.get('b')
            }
            print_price(symbol, prices[symbol])

        elif mode == 'askbid':
            if symbol in prices:
                prices[symbol]['ask'] = p.get('a')
                prices[symbol]['bid'] = p.get('b')
                prices[symbol]['close'] = p.get('c')
            spread = calculate_spread(p.get('a'), p.get('b'))
            print(f"  {symbol}: Ask={p.get('a')} Bid={p.get('b')} Spread={spread} pips")


def print_price(symbol, p):
    """Pretty print forex price data."""
    pair = symbol.split(':')[1] if ':' in symbol else symbol
    spread = calculate_spread(p.get('ask'), p.get('bid'))

    print(f"\n  [{pair}]")
    print(f"    Price: {p['close']}")
    print(f"    O: {p['open']} | H: {p['high']} | L: {p['low']} | C: {p['close']}")
    if p.get('ask') and p.get('bid'):
        print(f"    Ask: {p['ask']} | Bid: {p['bid']} | Spread: {spread} pips")


def calculate_spread(ask, bid):
    """Calculate spread in pips."""
    if not ask or not bid:
        return '--'
    try:
        spread = abs(float(ask) - float(bid))
        # For JPY pairs, multiply by 100, otherwise by 10000
        multiplier = 100 if spread > 0.1 else 10000
        return round(spread * multiplier, 1)
    except:
        return '--'


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
